import os
from io import BytesIO
from pathlib import Path
from time import sleep

from PIL import Image
from loguru import logger
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from module.alert import alert
from module.data import UserFromDB

for directory in ['captchas', 'user_data']:
    if not Path(directory).exists():
        os.mkdir(directory)


class Driver:
    search_bar = '//*[@id="side"]/div[1]/div/div/div[2]/div/div[2]'
    text_area = '//*/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]'
    parse_elements = '//div/div/div/div[2]/div[1]/div[1]/div/span'

    def chrome_driver(self, profile):
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-data-dir={os.getcwd()}/user_data/{profile}')
        self.driver = Chrome(ChromeDriverManager().install(), options=options)
        return self.driver

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

        return self.find_element(self.search_bar, 20)

    def find_textarea(self):
        """
        return textarea of message field element
        """
        return self.find_element(self.text_area)

    def find_element(self, xpath, timeout=10):
        """
        wait until xpath of element appears on web page and returns web-element as object
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                lambda d: self.driver.find_element(By.XPATH, xpath), f'unable to find {xpath}'
            )
            return element
        except TimeoutException:
            logger.error(f'can`t find {xpath}')
            return None

    def teardown(self) -> None:
        """
        closes browser
        """

        logger.info('closing browser')
        self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def get_qrcode(self, file_name: str) -> str:
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
        im.save(file_name)
        return file_name


class Browser(Driver):
    WEB_WHATSAPP_URL = "https://web.whatsapp.com/"
    state: str = None

    def __init__(self, user: UserFromDB):
        self.user = user
        self.driver = self.chrome_driver(self.user.page_id)

    def auth(self):
        alert(f'{self.user.name} авторизация', self.user.telegram)
        result = False
        while result is False:
            loading_result = self.loading()
            if loading_result == 'search_bar':
                result = True
                alert(f'{self.user.name} авторизирован', self.user.telegram)
            if loading_result == 'qr_code':
                self.solve_qrcode()
            else:
                self.try_again()

    def loading(self):
        alert(f'{self.user.name} Whatsapp загружается', self.user.telegram)
        self.driver.get(self.WEB_WHATSAPP_URL)
        elements = dict(
            search_bar=self.search_bar,
            qr_code='//canvas'
        )

        result = None
        while result is None:
            for key in elements.keys():
                if self.find_element(elements[key], timeout=0):
                    result = key
            sleep(1.5)
        return result

    def try_again(self):
        if 'Попытка подключения к телефону' in self.driver.page_source:
            self.find_element('//div[2]/div/div').click()

    def solve_qrcode(self):
        alert(f'{self.user.name} авторизируйтесь', self.user.telegram,
              file=self.get_qrcode(f'captchas/{self.user.name}_captcha.png'))
        try:
            qr_code_xpath = '//canvas'
            WebDriverWait(self.driver, 17).until_not(
                lambda d: self.driver.find_element(By.XPATH, qr_code_xpath), 'captcha not solved'
            )
            return True
        except TimeoutException as error:
            logger.error(error)
            return False

    def quit(self):
        if 'Попытка подключения к телефону' in self.driver.page_source:
            self.find_element('//div[1]/div/div').click()

    def parse(self):
        alert(f'{self.user.name} парсинг запущен', self.user.telegram)
        groups = []
        print('Прокрути чаты')
        try:
            while True:
                uniqueelements = []
                for element in self.driver.find_elements(By.XPATH, self.parse_elements):
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
        logger.info(target)
        try:
            self.type_text(self.find_textarea(), message)
            self.find_textarea().send_keys(Keys.ENTER)
            logger.info(f'{self.user.name} отправлено в {target}')
            return True
        except Exception as error:
            logger.info(error)
            return False

    # def join_group(self, link):
    #     self.driver.get(link)
    #     join_group_button_xpath = '//*[@id="app"]/div[1]/span[2]/div[1]/div/div/div/div/div/div[2]/div[2]/div/div'
    #     el = self.find_element(join_group_button_xpath, 10)
    #     if el:
    #         el.click()
    #         return True
    #     else:
    #         return False
