import argparse

from selenium.common.exceptions import StaleElementReferenceException

from WhatsApp import WhatsApp
from logger import logger

LOGGER = logger('WhatsAppParser')


class WhatsAppParser(WhatsApp):
    def __init__(self, index):
        super().__init__(index)

    def parse(self):
        groups = []
        elements = '//*[@id="pane-side"]/div[1]/div/div/div/div/div/div[2]/div[1]/div[1]/span'
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
        except Exception:
            with open('targets.csv', 'w+', encoding='utf-8') as f:
                f.write('\n'.join(groups))


def main(index):
    while True:
        whats_parser = WhatsAppParser(index)
        authorisation = whats_parser.authorisation()
        if authorisation == 'Success':
            whats_parser.parse()
        if authorisation == 'Captcha':
            whats_parser.get_qrcode()
            whats_parser.driver.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('index', type=int)
    args = parser.parse_args()
    main(args.index)
