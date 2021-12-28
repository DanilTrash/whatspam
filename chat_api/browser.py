import os

import selenium.common.exceptions as exceptions
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from logger import logger

LOGGER = logger('browser')


class Browser:
    def __init__(self, proxy, email):
        self.email = email
        self.options = ChromeOptions()
        if proxy:
            self.options.add_argument('--proxy-server=%s' % proxy)
        self.driver = Chrome(options=self.options)

    def reg_api_keys(self):
        url = 'https://app.chat-api.com/registration'
        self.driver.get(url)
        try:
            email_xpath = '//*[@name="email"]'
            password_xpath = '//*[@name="password"]'
            password_confirm_xpath = '//*[@name="passwordConfirm"]'
            element = WebDriverWait(self, 10).until(lambda d: self.driver.find_element_by_xpath(email_xpath))
            element.send_keys(str(self.email))
            self.driver.find_element_by_xpath(password_xpath).send_keys(str(self.email))
            self.driver.find_element_by_xpath(password_confirm_xpath).send_keys(str(self.email))
            self.driver.find_element_by_xpath('//*/md-checkbox/div[1]').click()
            submit_xpath = '//*[@id="content"]/div/div[2]/div[1]/form/button'
            self.driver.find_element_by_xpath(submit_xpath).click()
            return True
        except (exceptions.NoSuchElementException, exceptions.TimeoutException) as error:
            LOGGER.error(error)
            return False

    def check_last_mail(self):
        self.email.check_last_mail()
        self.driver.get(f'file:///{os.getcwd()}/message.html')
        try:
            WebDriverWait(self.driver, 5).until(lambda d: self.driver.find_element_by_xpath('//*/tr[3]/td/a')).click()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            instance_element = WebDriverWait(self.driver, 30).until(
                lambda d: self.driver.find_element_by_xpath('//*/div/span[2]/strong'))
            LOGGER.info(instance_element.text[1:])
            token_eleemnt = WebDriverWait(self.driver, 30).until(
                lambda d: self.driver.find_element_by_xpath('//*/div[2]/strong[2]'))
            LOGGER.info(token_eleemnt.text)
            return True
        except exceptions.TimeoutException as error:
            LOGGER.exception(error)
            return False
