import logging
import logging.handlers
import os


def get_logger(filename: str):
    """
    Функция возвращает logger по имени и сохраняет логи в файлы с
    соответствующим названием, разделяя по часам
    :param filename: название для logger
    :return: logger
    """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger(filename)
    logger.propagate = False
    if not logger.handlers:
        log_path = os.path.join(LOG_DIR, f"{filename}.log")
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_path, when='h', interval=1, backupCount=90
        )
        log_formatter = logging.Formatter("[%(levelname)s] "
                                          "%(asctime)s %(message)s")
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
    logger.setLevel('INFO')

    return logger
