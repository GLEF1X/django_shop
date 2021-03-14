import random
from typing import Optional, List, Tuple

DEFAULT_ARGUMENTS = (
    "force_insert",
    "force_update",
    "using",
    "update_fields"
)


def generate_abbreviation(chars_count: int = 8) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    word = ''
    for _ in range(0, chars_count):
        word += random.choice(chars)
    return word


def format_saving_kwargs(kwargs: dict, attrs: List[str]) -> Tuple[dict, dict]:
    formatted_kwargs = {}
    initializer_kwargs = {}
    for key in kwargs.keys():
        if key in attrs:
            formatted_kwargs.update(
                {
                    key: kwargs.get(key)
                }
            )
        else:
            if key in DEFAULT_ARGUMENTS:
                initializer_kwargs.update(
                    {
                        key: kwargs.get(key)
                    }
                )

    return formatted_kwargs, initializer_kwargs
