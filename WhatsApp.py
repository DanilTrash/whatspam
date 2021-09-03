from datetime import timedelta, datetime
from io import BytesIO
from time import sleep

from xvfbwrapper import Xvfb
from requests import get
from PIL import Image
from selenium.webdriver import Remote
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from Database import Database
from logger import alert, logger

WEB_WHATSAPP_URL = "https://web.whatsapp.com/"
TIMEOUT = 120
LOGGER = logger(__file__)


class WhatsApp:
    def __init__(self, index):  # fix не работает если запущен экземпляр мультилогина
        self.admin = Database().admins[index]
        self.profile_id = Database().profile_ids[index]
        self.telegram = Database().telegrams[index]
        self.targets = Database().targets[index]
        self.message = Database().messages[index]
        LOGGER.info(f'{self.profile_id}'
                    f'\n{self.admin}'
                    )
        mla_url = 'http://127.0.0.1:35000/api/v1/profile/start?automation=true&profileId=' + self.profile_id
        self.resp = get(mla_url).json()
        if self.resp['status'] == 'OK':
            value = self.resp['value']
            self.driver = Remote(command_executor=value, desired_capabilities={'acceptSslCerts': True})
            LOGGER.info(f'{self.admin} instanced')

    def get_qrcode(self):
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
        im.save(f'{self.admin}_captcha.png')
        alert(self.admin + ' авторизируйтесь', self.telegram, f'{self.admin}_captcha.png')
        sleep(20)

    def authorisation(self):
        self.driver.get(WEB_WHATSAPP_URL)
        LOGGER.info(f'{self.admin} Whatsapp загружается')
        try:
            WebDriverWait(self.driver, 20).until(lambda d: 'Не отключайте свой телефон' in self.driver.page_source)
            return 'Success'
        except TimeoutException:
            LOGGER.error(f'{self.admin} не авторизирован')
        try:
            exit_button_xpath = '//*[@id="app"]/div[1]/div/div/div/div/div/div[3]/div[1]'
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element(By.XPATH, exit_button_xpath)).click()
        except TimeoutException:
            pass
        try:
            qr_code_xpath = '//canvas'
            self.driver.find_element(By.XPATH, qr_code_xpath)
            return 'Captcha'
        except NoSuchElementException:
            return False

    def spam(self):
        if type(self.message) is float:
            return False
        if type(self.targets) is float:
            return False
        LOGGER.info(f'{self.admin} спам запущен')
        alert(f'{self.admin} спам запущен')
        for target in self.targets.split('\n'):
            try:
                search_bar = '//*[@id="side"]/div[1]/div/label/div/div[2]'
                search_bar_element = WebDriverWait(self.driver, 7).until(
                    lambda d: self.driver.find_element(By.XPATH, search_bar))
                search_bar_element.clear()  # fix StaleElementReferenceException
                search_bar_element.send_keys(target)
                group_xpath = f'//span[@title="{target}"]'
                WebDriverWait(self.driver, 7).until(
                    lambda d: self.driver.find_element(By.XPATH, group_xpath))
                self.driver.find_element(By.XPATH, group_xpath).click()
                text_area = '//*[@id="main"]/footer/div[1]/div[2]/div/div[1]/div/div[2]'
                text_area_element = WebDriverWait(self.driver, 7).until(
                    lambda d: self.driver.find_element(By.XPATH, text_area))
                text_area_element.clear()
                for line in self.message.splitlines():
                    if str.encode(line[:-1]) != b'\n':
                        text_area_element.send_keys(line)
                    text_area_element.send_keys(Keys.ALT + Keys.ENTER)
                text_area_element.send_keys(Keys.ENTER)
                print(f'{self.admin} отправлено в {target}')
            except (TimeoutException, StaleElementReferenceException):
                LOGGER.error(f'{self.admin} не отправлено в {target}')
                continue
            except Exception as error:
                LOGGER.exception(f'{self.admin} {error}')
                break
        time = datetime.now() + timedelta(minutes=TIMEOUT)
        LOGGER.info(f'Для {self.admin} спам запустится в {time.strftime("%H:%M")}')
        alert(f'Для {self.admin} спам запустится в {time.strftime("%H:%M")}')


def main(index):
    with Xvfb(1280, 1024):
        while True:
            whats = WhatsApp(index)
            if whats.resp['status'] != 'OK':
                LOGGER.warning(f"{whats.admin} multilogin {whats.resp['status']}")
                continue
            try:
                authorisation = whats.authorisation()
                if authorisation == 'Success':
                    whats.spam()
                    whats.driver.close()
                    break
                if authorisation == 'Captcha':
                    whats.get_qrcode()
                    whats.driver.close()
                else:
                    whats.driver.close()
            except Exception as error:
                LOGGER.error(f'{whats.admin} {error}', exc_info=True)
        sleep(TIMEOUT * 60)
