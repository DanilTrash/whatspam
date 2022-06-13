import sys

from module.client import client


def main():
    if sys.platform == 'linux':
        from xvfbwrapper import Xvfb
        with Xvfb():
            client()
    else:
        client()


if __name__ == '__main__':
    main()
