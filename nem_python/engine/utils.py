import time
from binascii import hexlify, unhexlify


def int_time():
    return int(time.time())


def msg2tag(msg):
    b = unhexlify(msg[:10].encode())
    return int.from_bytes(b, 'big')


def tag2hex(tag):
    assert isinstance(tag, int), 'tag is int'
    return hexlify(tag.to_bytes(5, 'big')).decode()
