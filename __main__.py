from multiprocessing import Process
from time import sleep

from Database import Database
from WhatsApp import WhatsApp
from logger import logger

LOGGER = logger('MAIN')


def main(index, admin):
    while True:
        try:
            whats = WhatsApp(index, admin)
            if whats.resp['status'] != 'OK':
                LOGGER.warning(f"{admin} multilogin {whats.resp['status']}")
                continue
            authorisation = whats.authorisation()
            if authorisation:
                whats.spam()
                whats.driver.close()
                sleep(TIMEOUT * 60)
                continue
            else:
                whats.driver.close()
                LOGGER.error(f'{admin} не авторизирован')
                continue
        except Exception as error:
            LOGGER.error(f'{admin} {error}', exc_info=True)
            sleep(TIMEOUT * 60)


TIMEOUT = 120
if __name__ == '__main__':
    LOGGER.info(__name__)
    admins = Database().admins
    procs = []
    for index, admin in enumerate(admins):
        # main(index, admin)
        proc = Process(target=main, args=(index, admin), daemon=True)
        procs.append(proc)
        proc.start()
        sleep(5 * 60)
    for proc in procs:
        proc.join()
