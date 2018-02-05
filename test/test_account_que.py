#!/user/env python3
# -*- coding: utf-8 -*-


from nem_python.nem_connect import NemConnect
import json
import time


def test():
    main_net = True
    nem = NemConnect(main_net=main_net)
    nem.start()
    print("start")
    # Create que
    multisig_que = nem.multisig_que.create()
    received_que = nem.received_que.create()

    nem.monitor_cks.append(b'NAGJG3QFWYZ37LMI7IQPSGQNYADGSJZGJRD2DIYA')

    while True:
        time.sleep(10)
        try:
            # check multisig tx
            print(json.dumps(multisig_que.get_nowait(), indent=4))
            # check new incoming
            print(json.dumps(received_que.get_nowait(), indent=4))
        except:
            print("no data")


if __name__ == "__main__":
    test()
