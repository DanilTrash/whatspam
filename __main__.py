from multiprocessing import Process
from time import sleep

from Database import Database
from WhatsApp import WhatsApp
from logger import logger

LOGGER = logger('MAIN')


def main(index, admin, timeout):
    while True:
        try:
            whats = WhatsApp(index, admin, timeout)
            if whats.resp['status'] != 'OK':
                LOGGER.warning(f"{admin} {whats.resp['status']}")
                continue
            authorisation = whats.authorisation()
            if authorisation:
                whats.spam()
                whats.driver.close()
                sleep(timeout * 60)
                continue
            else:
                whats.driver.close()
                LOGGER.error(f'{admin} не авторизирован')
                continue
        except Exception as error:
            LOGGER.error(f'{admin} {error}', exc_info=True)
            sleep(timeout * 60)


if __name__ == '__main__':
    LOGGER.info(__name__)
    admins = Database().admins
    timeout = 120
    procs = []
    for index, admin in enumerate(admins):
        proc = Process(target=main, args=(index, admin, timeout), daemon=True)
        procs.append(proc)
        proc.start()
        sleep(10 * 60)
    for proc in procs:
        proc.join()
