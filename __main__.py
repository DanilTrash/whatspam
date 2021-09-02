from argparse import ArgumentParser
from WhatsApp import main
from logger import logger


if __name__ == '__main__':
    try:
        parser = ArgumentParser()
        parser.add_argument('index', type=int)
        args = parser.parse_args()
        main(args.index)
    except Exception as error:
        logger(__file__).exception(error)
