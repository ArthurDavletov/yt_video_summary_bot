import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
import time


class CustomFormatter(logging.Formatter):
    """Кастомный форматер с миллисекундами."""
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, dt)
        else:
            s = time.strftime("%Y-%m-%d %H:%M:%S", dt)
        return f"{s}.{int(record.msecs):03d}"


LOG_FILE = Path(os.path.dirname(__file__)) / "logs" / "bot.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True) # Создание директории

root_logger = logging.getLogger()
root_logger.handlers = []  # Очистка обработчиков
root_logger.setLevel(logging.DEBUG)  # Уровень логирования

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5*1024*1024,
    backupCount=3, encoding="utf-8"
)
file_formatter = CustomFormatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S"
)

file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)


def get_logger(name):
    """Возвращает настроенный логгер."""
    return logging.getLogger(name)