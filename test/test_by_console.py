#!/user/env python3
# -*- coding: utf-8 -*-


from nem_python.nem_connect import NemConnect
from nem_python.dict_math import DictMath
from nem_ed25519.base import Ed25519 as ecc
from nem_python.transaction_builder import TransactionBuilder
from nem_python.transaction_reform import TransactionReform
from nem_python.engine.account import Account
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
    main_net = False
    get_logger()
    nem = NemConnect(main_net=main_net)
    nem.start()
    # old account
    # sk = '58befddd606faae2cd838216fd5308b1dacccfc02a8b5abc30e4f61049cec866'
    # pk = '6c70d178851c89ed5bad5cd889e515ccbc942218041055039a129b44c29e4f1a'
    # ck = 'TBAJHXNMA3DL7X2YUU3ALKKVSSK6IKMFU7UZ7AHD'
    sk = '2f8b1bb35e1fd47d6273dd5be91e9f0c276a93e43a46fd4cc023270e74d6bef1'
    pk = '58686baa2da7abf3de3056b45dafae265a8285b33bfc507b9d876167d6907eaf'
    ck = 'TA7ZFM7W5DNI7BOQYNDI3XRJQ3CVTDPGRU7N46S4'
    ant = Account(nem=nem, pk=pk, sk=sk, main_net=main_net)
    ant.start()
    print("start")
    ant.history_group('@owner')
    # ant.create_user()
    # nem.get_account_transfer_newest(ck, nem.TRANSFER_INCOMING)

    dm = DictMath()
    tr = TransactionReform(main_net=main_net, your_ck=ck)
    tb = TransactionBuilder()

    while True:
        try:
            cmd = input('>> ')
            exec("print(" + cmd + ")")
        except (EOFError, KeyboardInterrupt):
            break
        except Exception:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test()
