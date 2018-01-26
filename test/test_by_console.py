#!/user/env python3
# -*- coding: utf-8 -*-


from nem_python.nem_connect import NemConnect
from nem_python.dict_math import DictMath
from nem_python.ed25519 import Ed25519
from nem_python.transaction_builder import TransactionBuilder
from nem_python.transaction_reform import TransactionReform
import logging

"""

"""


def get_logger(level=logging.DEBUG):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)-6s] [%(threadName)-10s] [%(asctime)-24s] %(message)s')
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(formatter)
    logger.addHandler(sh)


def test():
    main_net = True
    nem = NemConnect(main_net=main_net)
    nem.start()
    get_logger()
    print("start")

    dm = DictMath()
    ecc = Ed25519(main_net=main_net)
    tr = TransactionReform(main_net=main_net)
    tb = TransactionBuilder()

    while True:
        try:
            cmd = input('>> ')
            exec("print(" + cmd + ")")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    test()
