from enum import Enum

import telebot
from loguru import logger as loguru_logger

from config import TG_TOKEN, TG_IDS


class Icons(Enum):
    SUCCESS = "🟢"
    ERROR = "🔴"
    WARNING = "🟡"
    INFO = "🔵"
    DEBUG = "🟣"


class CustomLogger:
    def __init__(self, telegram_logger):
        self.telegram_logger = telegram_logger
        self.loguru_logger = loguru_logger

    def success(self, message: str, send_to_tg=True) -> None:
        self.loguru_logger.success(message)
        if send_to_tg:
            self.telegram_logger(f"{Icons.SUCCESS.value} {message}")

    def error(self, message: str, send_to_tg=True) -> None:
        self.loguru_logger.error(message)
        if send_to_tg:
            self.telegram_logger(f"{Icons.ERROR.value} {message}")

    def warning(self, message: str, send_to_tg=True) -> None:
        self.loguru_logger.warning(message)
        if send_to_tg:
            self.telegram_logger(f"{Icons.WARNING.value} {message}")

    def info(self, message: str, send_to_tg=True) -> None:
        self.loguru_logger.info(message)
        if send_to_tg:
            self.telegram_logger(f"{Icons.INFO.value} {message}")

    def debug(self, message: str, send_to_tg=True) -> None:
        self.loguru_logger.debug(message)
        if send_to_tg:
            self.telegram_logger(f"{Icons.DEBUG.value} {message}")

    def exception(self, message: str, send_to_tg=True) -> None:
        self.loguru_logger.exception(message)

    @staticmethod
    def send_message_telegram(bot, text: str):
        try:
            for tg_id in TG_IDS:
                bot.send_message(tg_id, text)
        except Exception as e:
            raise Exception(f"Encountered an error when sending telegram message: {e}")

    @staticmethod
    def tg_logger(text):
        bot = telebot.TeleBot(TG_TOKEN, disable_web_page_preview=True)
        CustomLogger.send_message_telegram(bot, text)


logger = CustomLogger(telegram_logger=CustomLogger.tg_logger)