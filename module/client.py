from argparse import ArgumentParser
from time import sleep

from loguru import logger

from module.alert import alert
from module.browser_controller import Browser
from module.data import UserFromDB


class Model:

    def __init__(self, page):
        self.page = page

    def __call__(self, *args, **kwargs):
        pass


# class JoinGropsModel(Model):
#     _class_name = 'JoinGropsModel'
#
#     def __call__(self):
#         self.data = Database(self.page)
#         groups = Database('687502802').join_links
#         with Browser(self.data) as browser:
#             alert(f'{self.data.user} авторизация', self.data.telegram)
#             browser.auth()
#             logger.info(f'{self.data.user} {self._class_name}')
#             for link in groups:
#                 print(link)
#                 browser.join_group(link)
#                 sleep(2)


class ParseModel(Model):

    def __call__(self):
        self.user = UserFromDB(self.page)
        with Browser(self.user) as browser:
            browser.auth()
            browser.parse()


class SpamModel(Model):

    def spam(self):
        with Browser(self.user) as browser:
            browser.auth()
            alert(f'{self.user.name} спам запущен', self.user.telegram)
            for target in self.user.targets:
                try:
                    if browser.find_contact(target):
                        browser.send_message(target, self.user.message)
                    else:
                        logger.error('ошибка поиска %s' % target)
                except Exception as error:
                    logger.exception(error)

    def __call__(self):
        while True:
            self.user = UserFromDB(self.page)
            self.spam()
            alert(f'{self.user.name} спам завершен', self.user.telegram)
            sleep(self.user.timer)


def client():
    parser = ArgumentParser()
    parser.add_argument('client')
    parser.add_argument('mode')
    args = parser.parse_args()
    models = {
        'spam': SpamModel,
        'parse': ParseModel,
        # 'join': JoinGropsModel
    }
    model = models[args.mode](args.client)
    model()
