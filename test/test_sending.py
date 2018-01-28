#!/user/env python3
# -*- coding: utf-8 -*-


from nem_python.nem_connect import NemConnect
from nem_python.dict_math import DictMath
from nem_python.ed25519 import Ed25519
from nem_python.transaction_builder import TransactionBuilder
from nem_python.transaction_reform import TransactionReform
import logging


def multisig_sending():
    # Multisig sending
    main_net = False
    nem = NemConnect(main_net=main_net)
    nem.start()
    print("start")

    cosigner_sk = ''
    cosigner_pk = ''
    multisig_pk = ''
    recipient_ck = ''
    mosaics = {'nem:xem': 123}
    tx_dict = nem.multisig_mosaics_transfer(cosigner_pk, multisig_pk, recipient_ck, mosaics)
    print("tx:", tx_dict)
    tb = TransactionBuilder()
    tx_hex = tb.encode(tx_dict)
    print("tx hex:", tx_hex)
    sign = Ed25519.sign(tx_hex, cosigner_sk, cosigner_pk)
    print("sign", sign)
    r = nem.transaction_announce_dev(tx_hex, sign)
    print(r)


if __name__ == "__main__":
    multisig_sending()
