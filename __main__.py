from argparse import ArgumentParser
from time import sleep

from WhatsApp import main, TIMEOUT
from logger import alert, logger
from sys import platform


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('index', type=int)
    args = parser.parse_args()
    index = args.index
    while True:
        try:
            if platform == 'linux':
                from xvfbwrapper import Xvfb
                with Xvfb():
                    if main(index) == 'success':
                        sleep(TIMEOUT * 60)
            else:
                if main(index) == 'success':
                    sleep(TIMEOUT * 60)
        except Exception as error:
            logger(__file__).exception(error)
            alert(error.__str__(), 'me')
