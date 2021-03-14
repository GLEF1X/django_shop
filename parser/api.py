import asyncio
from dataclasses import dataclass
from itertools import repeat
from typing import Literal, Optional, Union, Dict, List, Tuple, Any, Type, Generator, Awaitable, AsyncGenerator

from aiohttp import ClientTimeout, ClientSession, ContentTypeError, ClientRequest, ClientProxyConnectionError
from aiohttp.client import DEFAULT_TIMEOUT
from aiosocksy import Socks5Auth, SocksError
from aiosocksy.connector import ProxyConnector, ProxyClientRequest

ProxyError = Exception()


@dataclass(frozen=True)
class Response:
    status_code: int
    response_data: Optional[Union[dict, str, bytes, bytearray, Exception]] = None

    @classmethod
    def bad_response(cls) -> 'Response':
        return cls(
            status_code=500,
            response_data=ProxyError
        )


@dataclass()
class CredentialService:
    login: str
    password: str
    ip_address: str
    service_type: Literal['SOCKS5', 'SOCKS4'] = 'SOCKS5'
    proxy_auth: Optional[Socks5Auth] = None
    socks_url: Optional[str] = None

    def get_proxy(self) -> Dict[str, Union[str, Socks5Auth]]:
        if not isinstance(self.proxy_auth, Socks5Auth):
            self.proxy_auth = Socks5Auth(
                login=self.login,
                password=self.password
            )

        self.socks_url = '{socks_type}://{ip_address}'.format(
            socks_type=self.service_type.lower(),
            ip_address=self.ip_address
        )
        return dict(
            proxy_auth=self.proxy_auth,
            proxy=self.socks_url
        )


class RequestAuthError(Exception):
    """
    Ошибка при неправильной аунтефикации POST or GET data

    """


class HttpBase(object):
    """
    Class, which include abstract methods of parser

    """


class RequestProxyError(Exception):
    """Возникает, если были переданы неправильные параметры запроса"""


class HttpXParser(HttpBase):
    """
    Парсер для django сайта, собирает дополнительную информацию

    """
    _sleep_time = 2

    def __init__(self):
        self._base_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            'Accept-Language': "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            # 'Accept': 'application/json, text/plain, */*',
        }
        self._session: Optional[ClientSession] = None
        self.url = 'http://127.0.0.1/api/'
        self._timeout = ClientTimeout(total=2 * 15, connect=None, sock_connect=5, sock_read=None)
        self._connector: Optional[ProxyConnector] = None

    async def _request(
            self,
            url: Optional[str] = None,
            get_json: bool = False,
            validate_django: bool = False,
            method: Literal['POST', 'GET'] = 'POST',
            set_timeout: bool = True,
            cookies: Optional[dict] = None,
            skip_exceptions: bool = False,
            proxy: Optional[CredentialService] = None,
            data: Optional[Dict[str, Union[str, int, List[Union[str, int]]]]] = None,
            headers: Optional[Dict[str, Union[str, int]]] = None,
            session: Optional[Type[ClientSession]] = None,
            **client_kwargs) -> Response:
        """
        Метод для отправки запроса,
        может возвращать в Response ProxyError в качестве response_data, это означает, что вы имеете проблемы с прокси,
        возможно нужно добавить дополнительные post данные, если вы используете method = POST, или headers, если запрос GET


        :param url: ссылка, куда вы хотите отправить ваш запрос
        :param get_json: указывает на то, хотите ли вы получить ответ в формате json
        :param method: POST or GET(тип запроса)
        :param proxy: instance of CredentialService
        :param data:
        :param headers:
        :param session: aiohttp.ClientSession object
        :param client_kwargs: key/value for aiohttp.ClientSession initialization
        :return: Response instance
        """
        headers = headers.update(self._base_headers) if isinstance(headers, dict) else self._base_headers

        if isinstance(proxy, CredentialService):
            self._connector = ProxyConnector(verify_ssl=False)
            self.request_class = ProxyClientRequest

        try:
            proxy_kwargs = proxy.get_proxy()
        except AttributeError:
            proxy_kwargs = {}

        if not isinstance(session, ClientSession):
            # Sending query
            async with ClientSession(
                    timeout=self._timeout if set_timeout else DEFAULT_TIMEOUT,
                    connector=self._connector,
                    request_class=self.request_class if isinstance(proxy, CredentialService) else ClientRequest,
                    **client_kwargs
            ) as session:
                self._session = session
                try:
                    response = await self._session.request(
                        method=method,
                        url=self.url if not url else url,
                        data=self._set_auth(data) if validate_django else data,
                        headers=headers,
                        **proxy_kwargs
                    )
                except (ClientProxyConnectionError, SocksError):
                    if not skip_exceptions:
                        raise ConnectionError()
                    return Response.bad_response()
                    # Get content from site
                try:
                    data = await response.json(
                        content_type="application/json"
                    )
                except ContentTypeError as ex:
                    if get_json:
                        raise RequestAuthError() from ex
                    data = await response.read()
                return Response(
                    status_code=response.status,
                    response_data=data
                )

    @staticmethod
    def _set_auth(
            data: Optional[
                Dict[str, Union[str, int, List[Union[str, int]], Tuple[Union[str, int]]]]
            ] = None) -> Optional[Dict[str, str]]:
        """
        Метод валидации для джанго апи

        :param data: It must be dict(your headers or data)
        :return: validated data or headers
        """
        try:
            from djangoProject.settings import SECRET_KEY, SECRET_CODE
        except ImportError:
            SECRET_KEY = None
            SECRET_CODE = None
        if not isinstance(data, dict):
            data = {}
        data.update(
            {
                'SECRET_KEY': SECRET_KEY,
                'SECRET_CODE': SECRET_CODE
            }
        )
        return data

    async def fetch(self, *, times: int = 10, **kwargs) -> AsyncGenerator[Response, None]:
        """
        Basic usage: \n
        parser = HttpXParser() \n
        async for response in parser.fetch():
            print(response)

        :param times: int of quantity requests
        :param kwargs: HttpXParser._request kwargs
        :return:
        """
        try:
            django_support = kwargs.get('validate_django')
            if django_support and kwargs.get('proxy'):
                raise RequestProxyError('Invalid params. You cant use proxy with django localhost')
        except KeyError:
            pass
        coroutines = [self._request(**kwargs) for _ in repeat(None, times)]
        for future in asyncio.as_completed(fs=coroutines):
            yield await future

    def fast(self) -> 'HttpXParser':
        """
        Method to fetching faster with using faster event loop(uvloop) \n
        USE IT ONLY ON LINUX SYSTEMS, on windows or mac its dont give performance!

        :return:
        """
        try:
            from uvloop import EventLoopPolicy
            asyncio.set_event_loop_policy(EventLoopPolicy())
        except ImportError:
            from asyncio import AbstractEventLoopPolicy as EventLoopPolicy
            asyncio.set_event_loop_policy(EventLoopPolicy())
            "Catching import error and forsake standard policy"
        return self

    def __getattr__(self, item: Any) -> Any:
        """
        Method, which can get an attribute of base_headers by this method

        :param item: key name of _base_headers dict data
        :return:
        """
        try:
            return self._base_headers.get(item)
        except KeyError:
            """Returning None"""

    def __eq__(self, other: Any) -> bool:
        """
        Method to compare instances of parsers

        :param other: other object
        :return: bool
        """
        if isinstance(other, self.__class__):
            if other.url == self.url and other._base_headers == self._base_headers:
                return True
        return False

    def __setitem__(self, key, value) -> None:
        """

        :param key: key of base_headers dict
        :param value: value of base_headers dict
        :return: None
        """
        self._base_headers.update(
            {key: value}
        )

    @staticmethod
    def combine_proxies(
            proxies: Union[List[CredentialService], Tuple[CredentialService]]
    ) -> Union[
        List[CredentialService], Tuple[CredentialService]
    ]:
        """
        Method to combine proxies

        :param proxies:
        :return: shuffled iterable(list or tuple of CredentialService objects)
        """
        import random
        random.shuffle(proxies)
        return proxies


# Client Code

async def send_query():
    parser = HttpXParser()
    async for response in parser.fast().fetch(
        url='https://school12.osvita-konotop.gov.ua/',
        times=1000,
        method='GET'
    ):
        print(response.status_code)


if __name__ == '__main__':
    asyncio.run(send_query())