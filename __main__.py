import os
import sys
from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
from time import sleep

from PIL import Image
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from alert import alert
from data import Database

dirs = ['captchas',
        'logs',
        'user_data', ]

for dir in dirs:
    if not Path(dir).exists():
        os.mkdir(dir)


class Driver:
    driver = None

    def __init__(self, profile_id):
        self.profile = profile_id

    def chrome_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f'--user-data-dir={os.getcwd()}/user_data/{self.profile}')
        self.driver = webdriver.Chrome(options=options)
        return self.driver


class Browser:
    WEB_WHATSAPP_URL = "https://web.whatsapp.com/"

    def __init__(self, model):
        self.model = model
        self.driver = Driver(model.profile_id).chrome_driver()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def auth(self):
        """
        authorising method
        load page -> get result of loading ->
        if page loads with qr code -> sends qr code to user
        if account already authorized -> return True
        """
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
            logger.exception(error)

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
            logger.error(error)
            return False

    def get_qrcode(self) -> str:
        """
        finds and get picture of qr code
        """
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
        captch_filename = f'captchas/{self.model.user}_captcha.png'
        im.save(captch_filename)
        return captch_filename

    def solve_qrcode(self):
        """
        gets qr code and send it to user
        """
        logger.info('solving captcha')
        alert(self.model.user + ' авторизируйтесь', self.model.telegram, self.get_qrcode())
        try:
            qr_code_xpath = '//canvas'
            WebDriverWait(self.driver, 17).until_not(lambda d: self.driver.find_element(By.XPATH, qr_code_xpath),
                                                     'captcha not solved')
            return True
        except TimeoutException as error:
            logger.error(error)
            return False

    def loading(self):
        """
        gets a whatsapp main page and returns result of it`s loading
        """
        logger.info(f'{self.model.user} Whatsapp загружается')
        self.driver.get(self.WEB_WHATSAPP_URL)
        elements = dict(
            search_bar='//*[@id="side"]/div[1]/div/label/div/div[2]',
            exit_button='//*[@id="app"]/div[1]/div/div/div/div/div/div[3]/div[2]',
            qr_code='//canvas'
        )
        logger.info('loading')
        for _ in range(1200):
            for key in elements.keys():
                try:
                    self.driver.find_element_by_xpath(elements.get(key))
                    return key
                except Exception:  # fixme
                    pass

    def type_text(self, element, message):
        """
        inputs text into input field
        usually in search bar or messaging field
        """
        JS_ADD_TEXT_TO_INPUT = """
          var elm = arguments[0], txt = arguments[1];
          elm.textContent += txt;
          elm.dispatchEvent(new Event('keydown', {bubbles: true}));
          elm.dispatchEvent(new Event('keypress', {bubbles: true}));
          elm.dispatchEvent(new Event('input', {bubbles: true}));
          elm.dispatchEvent(new Event('keyup', {bubbles: true}));
          """
        for letter in message:
            self.driver.execute_script(JS_ADD_TEXT_TO_INPUT, element,
                                       letter.encode("unicode_escape").decode('unicode_escape'))

    def find_group(self, target):
        """
        gets target and returns it element in search result
        """
        group_xpath = f'//*/span[@title="{target}"]'
        return self.find_element(group_xpath, 10)

    def find_qrcode(self):
        """
        return qr code element
        """
        qr_code_xpath = '//canvas'
        return self.find_element(qr_code_xpath, 20)

    def find_search_bar(self):
        """
        return search bar field element
        """
        search_bar = '//*[@id="side"]/div[1]/div/label/div/div[2]'
        return self.find_element(search_bar, 20)

    def find_textarea(self):
        """
        return textarea of message field element
        """
        text_area = '//*/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]'
        return self.find_element(text_area)

    def find_element(self, xpath, timeout=10):
        """
        wait until xpath of element appears on web page and returns web-element as object
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                lambda d: self.driver.find_element(By.XPATH, xpath), f'unable to find {xpath}'
            )
            return element
        except Exception as error:
            logger.error(error)
            return None

    def find_contact(self, target):
        try:
            self.find_search_bar().clear()
            self.find_search_bar().click()
            self.type_text(self.find_search_bar(), target)
            self.find_group(target).click()
            return True
        except Exception as error:
            logger.error(error)
            return False

    def send_message(self, target, message) -> bool:
        """
        sends messages to specific contact or group
        """
        logger.info(target)
        try:
            self.type_text(self.find_textarea(), message)
            self.find_textarea().send_keys(Keys.ENTER)
            logger.info(f'{self.model.user} отправлено в {target}')
            return True
        except Exception as error:
            logger.info(error)
            return False

    def teardown(self) -> None:
        """
        closes browser
        """

        logger.info('closing browser')
        self.driver.quit()

    def join_group(self, link):
        self.driver.get(link)
        join_group_button_xpath = '//*[@id="app"]/div[1]/span[2]/div[1]/div/div/div/div/div/div[2]/div[2]/div/div'
        el = self.find_element(join_group_button_xpath, 10)
        if el:
            el.click()
            return True
        else:
            return False


class Model:
    _class_name = 'Model'

    def __init__(self, page):
        self.page = page


class JoinGropsModel(Model):
    _class_name = 'JoinGropsModel'

    def __call__(self):
        self.data = Database(self.page)
        groups = Database('687502802').join_links
        with Browser(self.data) as browser:
            alert(f'{self.data.user} авторизация', self.data.telegram)
            browser.auth()
            logger.info(f'{self.data.user} {self._class_name}')
            for link in groups:
                print(link)
                browser.join_group(link)
                sleep(2)


class ParseModel(Model):
    _class_name = 'Parsing'

    def __call__(self):
        self.data = Database(self.page)
        with Browser(self.data) as browser:
            alert(f'{self.data.user} авторизация', self.data.telegram)
            browser.auth()
            logger.info(f'{self.data.user} парсинг запущен')
            alert(f'{self.data.user} парсинг запущен', self.data.telegram)
            browser.parse()


class SpamModel(Model):
    _class_name = 'SpamActivity'

    def __call__(self):
        while True:
            self.data = Database(self.page)
            try:
                with Browser(self.data) as browser:
                    alert(f'{self.data.user} авторизация', self.data.telegram)
                    browser.auth()
                    alert(f'{self.data.user} спам запущен', self.data.telegram)
                    logger.info(f'{self.data.user} спам запущен')
                    targets_list = self.data.targets
                    for target in targets_list:
                        try:
                            if browser.find_contact(target):
                                browser.send_message(target, self.data.message[0])
                            else:
                                logger.error('ошибка поиска %s' % target)
                        except Exception as error:
                            logger.exception(error)
                alert(f'{self.data.user} спам завершен', self.data.telegram)
                logger.info(f'{self.data.user} спам завершен')
            except Exception as error:
                logger.exception(error)
            finally:
                sleep(int(self.data.timer))


def main():
    parser = ArgumentParser()
    parser.add_argument('client')
    parser.add_argument('mode')
    args = parser.parse_args()
    models = {
        'spam': SpamModel,
        'parse': ParseModel,
        'join': JoinGropsModel
    }
    model = models[args.mode](args.client)
    model()


if __name__ == '__main__':
    if sys.platform == 'linux':
        from xvfbwrapper import Xvfb
        with Xvfb():
            main()
    else:
        main()
