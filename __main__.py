from multiprocessing import Process
from time import sleep

from Database import Database
from WhatsApp import main
from logger import logger

LOGGER = logger(__file__)


if __name__ == '__main__':
    LOGGER.info(__file__)
    admins = Database().admins
    procs = []
    for index, admin in enumerate(admins):
        proc = Process(target=main, args=(index, admin), daemon=True)
        procs.append(proc)
        proc.start()
        sleep(2 * 60)
    for proc in procs:
        proc.join()
