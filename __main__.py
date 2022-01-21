import logging
import os
import sys
from argparse import ArgumentParser
from io import BytesIO
from time import sleep

from PIL import Image
from requests import get
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

from telethon.sync import TelegramClient


class Database:

    def __init__(self, page):
        self.url = ('https://docs.google.com/spreadsheets/d/12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0/'
                    f'export?format=csv&id=12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0&gid={page}')

    def __call__(self, arg):
        value = pd.read_csv(self.url, dtype={arg: str})[arg]
        return value


def logger(name, mode='w', log_file='log'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    fileHandler = logging.FileHandler(log_file+'.log', encoding='utf_8_sig', mode=mode)
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger


def alert(message: str, entity: str, file: bytes = None):
    api_id = 4345538
    api_hash = '49313b839c59755f6d4ed52c002576f9'

    with TelegramClient(f'danil', api_id, api_hash) as client:
        client.send_message(entity, message, file=file)


class Driver:
    driver = None

    def __init__(self, model):
        self.logger = model.logger
        self.profile = model.profile_id
        self.proxy = model.proxy

    def multilogin_driver(self):
        while self.driver is None:
            mla_url = 'http://127.0.0.1:35000/api/v1/profile/start?automation=true&profileId=' + self.profile
            resp = get(mla_url).json()
            if resp['status'] == 'OK':
                value = resp['value']
                self.driver = webdriver.Remote(command_executor=value, desired_capabilities={'acceptSslCerts': True})
            else:
                self.logger.error('profile status: {} {}'.format(resp['status'], resp['message']))
        return self.driver

    def chrome_driver(self):
        options = webdriver.ChromeOptions()
        if self.proxy:
            options.add_argument('--proxy-server={}'.format(self.proxy))
        options.add_argument(f'--user-data-dir={os.getcwd()}/user_data/{self.profile}')
        self.driver = webdriver.Chrome(options=options)
        return self.driver


class Browser:
    WEB_WHATSAPP_URL = "https://web.whatsapp.com/"

    def __init__(self, model):
        '''
        initialises driver of browser
        '''
        self.model = model
        self.driver = Driver(model).chrome_driver()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def auth(self):
        '''
        authorising method
        load page -> get result of loading ->
        if page loads with qr code -> sends qr code to user
        if account already authorized -> return True
        '''
        result = False
        while result is False:
            loading_result = self.loading()
            if loading_result == 'search_bar':
                result = True
            if loading_result == 'qr_code':
                self.solve_qrcode()
            else:
                self.quit()

    def quit(self):
        try:
            self.find_element('//*[@id="app"]/div[1]/div/div/div/div/div/div[3]/div[2]').click()
        except Exception as error:
            self.model.logger.exception(error)

    def parse(self):
        groups = []
        # elements = '//*[@id="pane-side"]/div[1]/div/div/div/div/div/div[2]/div[1]/div[1]/span'
        elements = '//*/div[2]/div[1]/div[1]/span'
        print('Прокрути чаты')
        try:
            while True:
                uniqueelements = []
                for element in self.driver.find_elements_by_xpath(elements):
                    try:
                        chat = element.get_attribute('title')
                        uniqueelements.append(chat)
                    except StaleElementReferenceException:
                        continue
                for group in set(uniqueelements) - set(groups):
                    groups.append(group)
                    print(group)
                    with open('targets.txt', 'w+', encoding='utf_8_sig') as f:
                        f.write('\n'.join(groups))
        except Exception as error:
            self.model.logger.error(error)
            return False

    def get_qrcode(self):
        '''
        finds and get picture of qr code
        '''
        qr_code_xpath = '//canvas'
        captcha_element = self.driver.find_element(By.XPATH, qr_code_xpath)
        location = captcha_element.location_once_scrolled_into_view
        size = captcha_element.size
        png = self.driver.get_screenshot_as_png()
        im = Image.open(BytesIO(png))
        left = location['x'] - 20
        top = location['y'] - 20
        right = location['x'] + size['width'] + 20
        bottom = location['y'] + size['height'] + 20
        im = im.crop((left, top, right, bottom))
        im.save(f'{self.model.user}_captcha.png')
        return f'{self.model.user}_captcha.png'

    def solve_qrcode(self):
        '''
        gets qr code and send it to user
        '''
        self.model.logger.info('solving captcha')
        alert(self.model.user + ' авторизируйтесь', self.model.telegram, self.get_qrcode())
        try:
            qr_code_xpath = '//canvas'
            WebDriverWait(self.driver, 17).until_not(lambda d: self.driver.find_element(By.XPATH, qr_code_xpath),
                                                     'captcha not solved')
            return True
        except TimeoutException as error:
            self.model.logger.error(error)
            return False

    def loading(self):
        '''
        gets a whatsapp main page and returns result of it`s loading
        '''
        self.model.logger.info(f'{self.model.user} Whatsapp загружается')
        self.driver.get(self.WEB_WHATSAPP_URL)
        elements = dict(
            search_bar='//*[@id="side"]/div[1]/div/label/div/div[2]',
            exit_button='//*[@id="app"]/div[1]/div/div/div/div/div/div[3]/div[2]',
            qr_code='//canvas'
        )
        for _ in range(1200):
            for key in elements.keys():
                try:
                    self.driver.find_element_by_xpath(elements.get(key))
                    return key
                except Exception:
                    self.model.logger.error(f'unable to find {key}')

    def type_text(self, element, message):
        '''
        inputs text into input field
        usually in search bar or messaging field
        '''
        JS_ADD_TEXT_TO_INPUT = """
          var elm = arguments[0], txt = arguments[1];
          elm.textContent += txt;
          elm.dispatchEvent(new Event('keydown', {bubbles: true}));
          elm.dispatchEvent(new Event('keypress', {bubbles: true}));
          elm.dispatchEvent(new Event('input', {bubbles: true}));
          elm.dispatchEvent(new Event('keyup', {bubbles: true}));
          """
        for letter in message:
            self.driver.execute_script(JS_ADD_TEXT_TO_INPUT, element, letter.encode("unicode_escape").decode('unicode_escape'))

    def find_group(self, target):
        '''
        gets target and returns it element in search result
        '''
        group_xpath = f'//*/span[@title="{target}"]'
        return self.find_element(group_xpath, 10)

    def find_qrcode(self):
        '''
        return qr code element
        '''
        qr_code_xpath = '//canvas'
        return self.find_element(qr_code_xpath, 20)

    def find_search_bar(self):
        '''
        return search bar field element
        '''
        search_bar = '//*[@id="side"]/div[1]/div/label/div/div[2]'
        return self.find_element(search_bar, 20)

    def find_textarea(self):
        '''
        return textarea of message field element
        '''
        text_area = '//*/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]'
        return self.find_element(text_area)

    def find_element(self, xpath, timeout=10):
        '''
        wait until xpath of element appears on web page and returns web-element as object
        '''
        try:
            element = WebDriverWait(self.driver, timeout).until(
                lambda d: self.driver.find_element(By.XPATH, xpath), f'unable to find {xpath}'
            )
            return element
        except Exception as error:
            self.model.logger.error(error)
            return None

    def find_contact(self, target):
        try:
            self.find_search_bar().clear()
            self.find_search_bar().click()
            self.type_text(self.find_search_bar(), target)
            self.find_group(target).click()
            return True
        except Exception as error:
            self.model.logger.error(error)
            return False

    def send_message(self, target, message) -> bool:
        '''
        sends messages to specific contact or group
        '''
        self.model.logger.info(target)
        try:
            self.type_text(self.find_textarea(), message)
            self.find_textarea().send_keys(Keys.ENTER)
            self.model.logger.info(f'{self.model.user} отправлено в {target}')
            return True
        except Exception as error:
            self.model.logger.info(error)
            return False

    def teardown(self) -> None:
        '''
        closes browser
        '''

        self.model.logger.info('closing browser')
        self.driver.quit()


class Model:
    _class_name = 'Model'
    data = Database(self.page)

    def __init__(self, page):
        self.page = page
        self.user = self.data('user')[0]
        self.proxy = self.data('proxy').fillna('')[0]
        self.profile_id = self.data('profile_id')[0]
        self.telegram = self.data('telegram')[0]
        self.logger = logger(self.user, log_file=self.user)


class ParseModel(Model):
    _class_name = 'Parsing'

    def __init__(self, page):
        super().__init__(page)
        self.logger.info(f'{self._class_name} initialized')

    def __call__(self):
        with Browser(self) as browser:
            alert(f'{self.user} авторизация', self.telegram)
            browser.auth()
            self.logger.info(f'{self.user} парсинг запущен')
            alert(f'{self.user} парсинг запущен', self.telegram)
            browser.parse()


class SpamModel(Model):
    _class_name = 'SpamActivity'

    def __init__(self, page):
        super().__init__(page)
        self.logger.info(f'{self._class_name} initialized')
        self.timer_btw_targets = int(self.data('timer_btw_targets')[0])
        self.timer = int(self.data('timer')[0])

    def __call__(self):
        while True:
            try:
                with Browser(self) as browser:
                    alert(f'{self.user} авторизация', self.telegram)
                    browser.auth()
                    alert(f'{self.user} спам запущен', self.telegram)
                    self.logger.info(f'{self.user} спам запущен')
                    for target in self.data('targets').dropna().tolist():
                        try:
                            if browser.find_contact(target):
                                browser.send_message(target, self.data('message')[0])
                                sleep(self.timer_btw_targets)
                            else:
                                self.logger.error('ошибка поиска %s' % target)
                        except Exception as error:
                            self.logger.exception(error)
                    alert(f'{self.user} спам завершен', self.telegram)
                    self.logger.info(f'{self.user} спам завершен')
            except Exception as error:
                self.logger.exception(error)
            sleep(self.timer)


def main():
    parser = ArgumentParser()
    parser.add_argument('client')
    parser.add_argument('mode')
    args = parser.parse_args()
    if args.mode == 'spam':
        model = SpamModel(args.client)
        model()
    elif args.mode == 'parse':
        model = ParseModel(args.client)
        model()


if __name__ == '__main__':
    if sys.platform == 'linux':
        from xvfbwrapper import Xvfb
        with Xvfb():
            main()
    else:
        main()
