import os


from module.client import client


def main():
    if os.name == "linux" or 'posix':
        from xvfbwrapper import Xvfb
        with Xvfb():
            client()
    else:
        client()


if __name__ == '__main__':
    main()
