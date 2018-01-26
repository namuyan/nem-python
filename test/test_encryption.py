#!/user/env python3
# -*- coding: utf-8 -*-

from nem_python.ed25519 import Ed25519


def test():
    PUB = '80d2ae0d784d28db38b5b85fd77e190981cea6f4328235ec173a90c2853c0761'
    PRI = '6a858fb93e0202fa62f894e591478caa23b06f90471e7976c30fb95efda4b312'
    MSG = "how silent! the cicada's voice soaks into the rocks. " \
          "Up here, a stillness the sound of the cicadas seeps into the crags."
    ecc = Ed25519()

    address = ecc.get_address(pk=PUB)
    print(address)
    sign = Ed25519.sign(message=MSG, secret_key=PRI, public_key=PUB)
    print(sign)
    vrify = Ed25519.verify(message=MSG, signature=sign, public_key=PUB)
    print(vrify)

    PUB2 = '28e8469422106f406051a24f2ea6402bac6f1977cf7e02eb3bf8c11d4070157a'
    PRI2 = '3c60f29c84b63c76ca8e3f1068ad328285ae8d5af2a95aa99ceb83d327dfb97e'
    print("pub2 address", ecc.get_address(pk=PUB2))
    enc = Ed25519.encrypt(private_key=PRI, public_key=PUB2, message=MSG)
    print(enc)
    dec = Ed25519.decrypt(private_key=PRI2, public_key=PUB, msg_hex=enc)
    print(dec)

if __name__ == '__main__':
    test()
