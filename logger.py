import logging
from telethon.sync import TelegramClient

api_id = 4345538
api_hash = '49313b839c59755f6d4ed52c002576f9'


def logger(name, mode='a'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    formatter = logging.Formatter('%(asctime)s ~ %(levelname)s: %(message)s')
    fileHandler = logging.FileHandler('log.log', encoding='utf_8_sig', mode=mode)
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger


def alert(message=None, entity=585403132, file=None):
    with TelegramClient(f'+79687580328', api_id, api_hash) as client:
        client.send_message(entity, message, file=file)
