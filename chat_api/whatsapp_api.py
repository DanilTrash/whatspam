import json

import requests
from logger import logger

LOGGER = logger('whats_api')


class ChatApi:
    API_URL = 'https://api.chat-api.com'

    def __init__(self, instance, token):
        self.instance = instance
        self.token = token

    def logout(self) -> dict:
        req = requests.post(f'{self.API_URL}/instance{self.instance}/logout?token={self.token}')
        return req.json()

    def takeover(self) -> dict:
        req = requests.post(f'{self.API_URL}/instance{self.instance}/takeover?token={self.token}')
        return req.json()

    def get_me(self) -> dict:
        req = requests.get(f'{self.API_URL}/instance{self.instance}/me?token={self.token}')
        return req.json()

    def get_status(self) -> dict:
        req = requests.get(f'{self.API_URL}/instance{self.instance}/status?token={self.token}')
        return req.json()

    def get_dialogs(self, limit=0, page=0) -> dict:
        req = requests.get(f'{self.API_URL}/instance{self.instance}/dialogs?token={self.token}&limit={limit}&page={page}')
        return req.json()

    def get_messages(self, limit) -> dict:
        req = requests.get(f'{self.API_URL}/instance{self.instance}/messages?token={self.token}&limit={limit}')
        return req.json()

    def get_messages_history(self, page) -> dict:
        req = requests.get(f'{self.API_URL}/instance{self.instance}/messagesHistory?token={self.token}&page={page}')
        return req.json()

    def send_message(self, target, text) -> dict:
        json_body = dict(chatId=target, body=text)
        req = requests.post(f'{self.API_URL}/instance{self.instance}/sendMessage?token={self.token}',
                            data=json_body)
        return req.json()

    def get_qr_code(self, captcha_path) -> str:
        req = requests.get(f'{self.API_URL}/instance{self.instance}/qr_code?token={self.token}')
        with open(captcha_path, 'wb') as f:
            f.write(req.content)
        return captcha_path


if __name__ == '__main__':
    account_number = 79288397841
    what = ChatApi(357148, 'tg8en4ezxwwnqr3k')
    print(what.get_me())
    # dialogs = what.get_dialogs()
    # with open(f'dialogs_{account_number}.json', 'w') as f:
    #     json.dump(dialogs, f)
    #     print(dialogs)
    with open(f'dialogs_{account_number}.json', 'r') as f:
        # for dialog in json.load(f)['dialogs']:
        #     print(dialog['id'][:-5])
        for dialog in json.load(f)['dialogs']:
            print(dialog['name'])
