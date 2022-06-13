from telethon.sync import TelegramClient

from module.data import ConfigFromDB

from loguru import logger


def alert(message: str, entity: str, file: str = None):  # tood config file with all data
    logger.info(message)
    config = ConfigFromDB('1492898183')
    with TelegramClient(config.user_session, config.api_id, config.api_hash) as client:
        client.send_message(entity, message, file=file)
