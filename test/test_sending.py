#!/user/env python3
# -*- coding: utf-8 -*-


from nem_python.nem_connect import NemConnect
from nem_python.dict_math import DictMath
from nem_python.transaction_builder import TransactionBuilder
from nem_python.transaction_reform import TransactionReform
from binascii import hexlify, unhexlify
from nem_ed25519.signature import sign


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
    sign_raw = sign(msg=unhexlify(tx_hex.encode()), sk=cosigner_sk, pk=cosigner_pk)
    sign_hex = hexlify(sign_raw).decode()
    print("sign", sign_hex)
    r = nem.transaction_announce(tx_hex, sign_hex)
    print(r)


if __name__ == "__main__":
    multisig_sending()
