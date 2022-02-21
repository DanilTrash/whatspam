from telethon.sync import TelegramClient

from data import Database


def alert(message: str, entity: str, file: str = None):  # tood config file with all data
    data = Database('1492898183')
    api_id: int = int(data.api_id)
    api_hash: str = data.api_hash
    user_session: str = data.user_session
    with TelegramClient(user_session, api_id, api_hash) as client:
        client.send_message(entity, message, file=file)
