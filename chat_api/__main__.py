import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta
from time import sleep

from browser import Browser
from whatsapp_api import ChatApi
from database import Database
from logger import logger, alert
from onesec_api import Mailbox


LOGGER = logger('client')


class Client(ChatApi):
    def __init__(self, index):
        LOGGER.info(index)
        self.data = Database(index)
        self.admin = self.data('admin')
        self.telegram = self.data('telegram')
        LOGGER.info(self.admin)
        self.timeout = int(self.data('timeout'))
        self.instance = self.data('instance')
        self.token = self.data('token')
        if self.instance and self.token:
            ChatApi.__init__(self, instance=self.instance, token=self.token)

    def _send_qr_code(self):
        captcha = self.get_qr_code(captcha_path=f'captcha_{self.admin}.png')
        alert(f'{self.admin} авторизируйтесь', self.telegram, captcha)
        sleep(20)

    def _collect_groups(self):
        groups = []
        for dialog in self.get_dialogs().get('dialogs'):
            group = {'id': dialog.get('id'), 'name': dialog.get('name')}
            groups.append(group)
        return groups

    def _auth(self):
        result = False
        loading_count = 0
        while result is False:
            auth_status = self.get_status().get('accountStatus')
            LOGGER.info(auth_status)
            if auth_status == 'authenticated':
                result = True
            if auth_status == 'got qr code':
                self._send_qr_code()
            if auth_status == 'loading':
                self.takeover()
                loading_count += 1
            if loading_count > 3:
                self.logout()
        return result

    def reg_api_keys(self):
        self.email = Mailbox()
        self.proxy = self.data('proxy')
        self.browser = Browser(self.proxy, self.email)
        self.browser.reg_api_keys()
        self.browser.check_last_mail()
        return True

    def collect_groups_name(self):
        self._auth()
        result = False
        while result is False:
            with open('groups.txt', 'w+', encoding='utf_8_sig') as f:
                dialogs = self.get_dialogs().get('dialogs')
                for dialog in dialogs:
                    print(dialog.get('name'))
                    f.write(dialog.get('name')+'\n')
                if len(dialogs) > 10:
                    return True

    def spam(self):
        self._auth()
        collect_groups = self._collect_groups()
        self.groups = self.data('targets').split('\n')
        if len(collect_groups) < 10:
            return False
        self.message = self.data('message')
        alert(f'{self.admin} спам запущен', self.telegram)
        for group in collect_groups:
            self.takeover()
            if group.get('name') in self.groups:
                LOGGER.info(group.get('name'))
                self.send_message(group.get('id'), self.message)
        time = datetime.now() + timedelta(minutes=self.timeout)
        alert(f'Для {self.admin} спам запустится в {time.strftime("%H:%M")}', self.telegram)
        LOGGER.info(f'Для {self.admin} спам запустится в {time.strftime("%H:%M")}')
        self.sleep()

    def sleep(self):
        sleep(self.timeout * 60)


def main():
    if len(sys.argv) == 1:
        sys.argv = ['.', '1384103625']
    parser = ArgumentParser()
    parser.add_argument('client', type=int)
    parser.add_argument('--mode', '-m', default='spam')
    args = parser.parse_args()
    client = Client(args.client)
        # result = client.reg_api_keys()
        # result = client.collect_groups_name()
        # client.spam()


try:
    if __name__ == '__main__':
        main()
except Exception as error:
    LOGGER.exception(error)
