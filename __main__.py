import argparse
from WhatsApp import main
from multiprocessing import Process

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', '-i', required=True, type=int)
    args = parser.parse_args()
    index = args.index
    proc = Process(target=main, args=(args.index,), daemon=True)
    proc.start()
    proc.join()
