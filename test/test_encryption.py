#!/user/env python3
# -*- coding: utf-8 -*-

from nem_ed25519.key import get_address
from nem_ed25519.signature import sign, verify
from nem_ed25519.encrypt import encrypt, decrypt


def test():
    PUB = '80d2ae0d784d28db38b5b85fd77e190981cea6f4328235ec173a90c2853c0761'
    PRI = '6a858fb93e0202fa62f894e591478caa23b06f90471e7976c30fb95efda4b312'
    MSG = "how silent! the cicada's voice soaks into the rocks. " \
          "Up here, a stillness the sound of the cicadas seeps into the crags.".encode()

    address = get_address(pk=PUB, main_net=True)
    print(address)
    sign_raw = sign(msg=MSG, sk=PRI, pk=PUB)
    print(sign_raw)
    # raised ValueError if verification filed
    verify(msg=MSG, sign=sign_raw, pk=PUB)

    PUB2 = '28e8469422106f406051a24f2ea6402bac6f1977cf7e02eb3bf8c11d4070157a'
    PRI2 = '3c60f29c84b63c76ca8e3f1068ad328285ae8d5af2a95aa99ceb83d327dfb97e'
    print("pub2 address", get_address(pk=PUB2, main_net=True))
    enc = encrypt(sk=PRI, pk=PUB2, msg=MSG)
    print(enc)
    dec = decrypt(sk=PRI2, pk=PUB, enc=enc)
    print(dec)

if __name__ == '__main__':
    test()
