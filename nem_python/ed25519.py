#!/usr/bin/env python3

"""
this code is a cleaned version of http://ed25519.cr.yp.to/python/ed25519.py for python3

code released under the terms of the GNU Public License v3, copyleft 2015 yoochan

http://code.activestate.com/recipes/579102-ed25519/
"""

import collections
import hashlib
import os
import base64
from binascii import hexlify, unhexlify
from operator import getitem, methodcaller
from Crypto.Cipher import AES
from .python_sha3 import sha3_256, sha3_512

Point = collections.namedtuple('Point', ['x', 'y'])

key_mask = int.from_bytes(b'\x3F' + b'\xFF' * 30 + b'\xF8', 'big', signed=False)

b = 256
q = 2 ** 255 - 19


class Ed25519:
    def __init__(self, main_net=True):
        self.l = 2 ** 252 + 27742317777372353535851937790883648493
        self.d = -121665 * self.inverse(121666)
        self.i = pow(2, (q - 1) // 4, q)
        self.B = self.point(4 * self.inverse(5))
        self.main_net = main_net

    @staticmethod
    def to_hash(m):
        return sha3_512(m).digest()
        # return hashlib.sha512(m).digest()

    def from_bytes(self, h):
        """ pick 32 bytes, return a 256 bit int """
        return int.from_bytes(h[0:b // 8], 'little', signed=False)

    def to_bytes(self, k):
        return k.to_bytes(b // 8, 'little', signed=False)

    def as_key(self, h):
        return 2 ** (b - 2) + (self.from_bytes(h) & key_mask)

    def secret_key(self, seed=None):
        """ pick a random secret key """
        if seed is None:
            m = os.urandom(1024)
        else:
            m = seed.encode('utf8')
        h = self.to_hash(m)
        k = self.as_key(h)
        return hexlify(self.to_bytes(k))

    def public_key(self, sk):
        """ compute the public key from the secret one """
        h = self.to_hash(unhexlify(sk)[::-1])
        a = self.as_key(h)
        c = self.outer(self.B, a)
        return hexlify(self.point_to_bytes(c))

    def get_address(self, pk):
        """ compute the nem-py address from the public one """
        s = sha3_256()
        s.update(unhexlify(pk))
        sha3_pubkey = s.digest()

        h = hashlib.new('ripemd160')
        h.update(sha3_pubkey)
        ripe = h.digest()

        if self.main_net:
            version = b"\x68" + ripe
        else:
            version = b"\x98" + ripe

        s2 = sha3_256()
        s2.update(version)
        checksum = s2.digest()[0:4]
        return base64.b32encode(version + checksum)

    def inverse(self, x):
        return pow(x, q - 2, q)

    @staticmethod
    def str2bytes(string):
        return string if type(string) is bytes else string.encode('utf8')

    @staticmethod
    def sign(message, secret_key, public_key):
        try:
            message = unhexlify(Ed25519.str2bytes(message))
        except:
            message = Ed25519.str2bytes(message)

        secret_key = Ed25519.str2bytes(secret_key)
        public_key = Ed25519.str2bytes(public_key)

        ecc = SignClass()
        sign = ecc.sign(message, unhexlify(secret_key)[::-1], unhexlify(public_key))
        return hexlify(sign).decode()

    @staticmethod
    def verify(message, signature, public_key):
        try:
            message = unhexlify(Ed25519.str2bytes(message))
        except:
            message = Ed25519.str2bytes(message)

        signature = Ed25519.str2bytes(signature)
        public_key = Ed25519.str2bytes(public_key)

        ecc = SignClass()
        try:
            result = ecc.verify(unhexlify(signature), message, unhexlify(public_key))
            return result
        except:
            return False

    @staticmethod
    def encrypt(private_key, public_key, message):
        _message = Ed25519.str2bytes(message)
        _sk = Ed25519.str2bytes(private_key)
        _pk = Ed25519.str2bytes(public_key)

        ecc = SignClass()
        encrypted_hex = ecc.encrypt(unhexlify(_sk)[::-1], unhexlify(_pk), _message)
        return encrypted_hex.decode()

    @staticmethod
    def decrypt(private_key, public_key, msg_hex):
        _msg_hex = Ed25519.str2bytes(msg_hex)
        _sk = Ed25519.str2bytes(private_key)
        _pk = Ed25519.str2bytes(public_key)

        ecc = SignClass()
        raw_msg = ecc.decrypt(unhexlify(_sk)[::-1], unhexlify(_pk), _msg_hex)
        return Ed25519._unpad(raw_msg)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def recover(self, y):
        """ given a value y, recover the preimage x """
        p = (y * y - 1) * self.inverse(self.d * y * y + 1)
        x = pow(p, (q + 3) // 8, q)
        if (x * x - p) % q != 0:
            x = (x * self.i) % q
        if x % 2 != 0:
            x = q - x
        return x

    def point(self, y):
        """ given a value y, recover x and return the corresponding P(x, y) """
        return Point(self.recover(y) % q, y % q)

    def is_on_curve(self, P):
        return (P.y * P.y - P.x * P.x - 1 - self.d * P.x * P.x * P.y * P.y) % q == 0

    def inner(self, P, Q):
        """ inner product on the curve, between two points """
        x = (P.x * Q.y + Q.x * P.y) * self.inverse(1 + self.d * P.x * Q.x * P.y * Q.y)
        y = (P.y * Q.y + P.x * Q.x) * self.inverse(1 - self.d * P.x * Q.x * P.y * Q.y)
        return Point(x % q, y % q)

    def outer(self, P, n):
        """ outer product on the curve, between a point and a scalar """
        if n == 0:
            return Point(0, 1)
        Q = self.outer(P, n // 2)
        Q = self.inner(Q, Q)
        if n & 1:
            Q = self.inner(Q, P)
        return Q

    def point_to_bytes(self, P):
        return (P.y + ((P.x & 1) << 255)).to_bytes(b // 8, 'little')

    def bytes_to_point(self, b):
        i = self.from_bytes(b)
        y = i % 2 ** (b - 1)
        x = self.recover(y)
        if (x & 1) != ((i >> (b - 1)) & 1):
            x = q - x
        return Point(x, y)


class SignClass:
    l = 2 ** 252 + 27742317777372353535851937790883648493
    ident = (0, 1, 1, 0)
    Bpow = []

    def __init__(self):
        self.d = -121665 * self.inv(121666) % q
        self.By = 4 * self.inv(5)
        self.Bx = self.xrecover(self.By)
        self.B = (self.Bx % q, self.By % q, 1, (self.Bx * self.By) % q)
        self.I = pow(2, (q - 1) // 4, q)
        self.int2byte = methodcaller("to_bytes", 1, "big")
        self.Bpow = self.make_Bpow()

    def make_Bpow(self):
        P = self.B
        Bpow = []
        for i in range(253):
            Bpow.append(P)
            P = self.edwards_double(P)

        return Bpow

    @staticmethod
    def to_hash(m):
        return sha3_512(m).digest()

    @staticmethod
    def to_hash_sha3_256(m):
        return sha3_256(m).digest()

    def sign(self, m, sk, pk):
        h = self.to_hash(sk)
        a = 2 ** (b - 2) + sum(2 ** i * self.bit(h, i) for i in range(3, b - 2))

        m_raw = bytes([getitem(h, j) for j in range(b // 8, b // 4)]) + m
        r = self.Hint_hash(m_raw)

        R = self.scalarmult_B(r)
        S = (r + self.Hint_hash(self.encodepoint(R) + pk + m) * a) % self.l

        return self.encodepoint(R) + self.encodeint(S)

    def verify(self, s, m, pk):
        if len(s) != b // 4:
            raise ValueError("signature length is wrong")

        if len(pk) != b // 8:
            raise ValueError("public-key length is wrong")

        R = self.decodepoint(s[:b // 8])
        A = self.decodepoint(pk)
        S = self.decodeint(s[b // 8:b // 4])
        h = self.Hint_hash(self.encodepoint(R) + pk + m)

        (x1, y1, z1, t1) = P = self.scalarmult_B(S)
        (x2, y2, z2, t2) = Q = self.edwards_add(R, self.scalarmult(A, h))

        fP_on = not self.isoncurve(P)
        fQ_on = not self.isoncurve(Q)
        fX_on = (x1 * z2 - x2 * z1) % q != 0
        fY_on = (y1 * z2 - y2 * z1) % q != 0

        if fP_on or fQ_on or fX_on or fY_on:
            return False
        else:
            return True

    def inv(self, z):
        """$= z^{-1} \mod q$, for z != 0"""
        # Adapted from curve25519_athlon.c in djb's Curve25519.
        z2 = z * z % q  # 2
        z9 = self.pow2(z2, 2) * z % q  # 9
        z11 = z9 * z2 % q  # 11
        z2_5_0 = (z11 * z11) % q * z9 % q  # 31 == 2^5 - 2^0
        z2_10_0 = self.pow2(z2_5_0, 5) * z2_5_0 % q  # 2^10 - 2^0
        z2_20_0 = self.pow2(z2_10_0, 10) * z2_10_0 % q  # ...
        z2_40_0 = self.pow2(z2_20_0, 20) * z2_20_0 % q
        z2_50_0 = self.pow2(z2_40_0, 10) * z2_10_0 % q
        z2_100_0 = self.pow2(z2_50_0, 50) * z2_50_0 % q
        z2_200_0 = self.pow2(z2_100_0, 100) * z2_100_0 % q
        z2_250_0 = self.pow2(z2_200_0, 50) * z2_50_0 % q  # 2^250 - 2^0
        return self.pow2(z2_250_0, 5) * z11 % q  # 2^255 - 2^5 + 11 = q - 2

    def pow2(self, x, p):
        """== pow(x, 2**p, q)"""
        while p > 0:
            x = x * x % q
            p -= 1
        return x

    def xrecover(self, y):
        xx = (y * y - 1) * self.inv(self.d * y * y + 1)
        x = pow(xx, (q + 3) // 8, q)

        if (x * x - xx) % q != 0:
            x = (x * self.I) % q

        if x % 2 != 0:
            x = q - x

        return x

    def edwards_add(self, P, Q):
        # This is formula sequence 'addition-add-2008-hwcd-3' from
        # http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html
        (x1, y1, z1, t1) = P
        (x2, y2, z2, t2) = Q

        a = (y1 - x1) * (y2 - x2) % q
        b = (y1 + x1) * (y2 + x2) % q
        c = t1 * 2 * self.d * t2 % q
        dd = z1 * 2 * z2 % q
        e = b - a
        f = dd - c
        g = dd + c
        h = b + a
        x3 = e * f
        y3 = g * h
        t3 = e * h
        z3 = f * g

        return (x3 % q, y3 % q, z3 % q, t3 % q)

    def edwards_double(self, P):
        # This is formula sequence 'dbl-2008-hwcd' from
        # http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html
        (x1, y1, z1, t1) = P

        a = x1 * x1 % q
        b = y1 * y1 % q
        c = 2 * z1 * z1 % q
        # dd = -a
        e = ((x1 + y1) * (x1 + y1) - a - b) % q
        g = -a + b  # dd + b
        f = g - c
        h = -a - b  # dd - b
        x3 = e * f
        y3 = g * h
        t3 = e * h
        z3 = f * g

        return (x3 % q, y3 % q, z3 % q, t3 % q)

    def encodepoint(self, P):
        (x, y, z, t) = P
        zi = self.inv(z)
        x = (x * zi) % q
        y = (y * zi) % q
        bits = [(y >> i) & 1 for i in range(b - 1)] + [x & 1]
        return b''.join([
            self.int2byte(sum([bits[i * 8 + j] << j for j in range(8)]))
            for i in range(b // 8)
        ])

    def encodeint(self, y):
        bits = [(y >> i) & 1 for i in range(b)]
        return b''.join([
            self.int2byte(sum([bits[i * 8 + j] << j for j in range(8)]))
            for i in range(b // 8)
        ])

    def decodepoint(self, s):
        y = sum(2 ** i * self.bit(s, i) for i in range(0, b - 1))
        x = self.xrecover(y)
        if x & 1 != self.bit(s, b - 1):
            x = q - x
        P = (x, y, 1, (x * y) % q)
        if not self.isoncurve(P):
            raise ValueError("decoding point that is not on curve")
        return P

    def decodeint(self, s):
        return sum(2 ** i * self.bit(s, i) for i in range(0, b))

    def scalarmult(self, P, e):
        if e == 0:
            return self.ident
        Q = self.scalarmult(P, e // 2)
        Q = self.edwards_double(Q)
        if e & 1:
            Q = self.edwards_add(Q, P)
        return Q

    def scalarmult_B(self, e):
        """
        Implements scalarmult(B, e) more efficiently.
        """
        # scalarmult(B, l) is the identity
        e = e % self.l
        P = self.ident
        for i in range(253):
            if e & 1:
                P = self.edwards_add(P, self.Bpow[i])
            e = e // 2
        assert e == 0, e
        return P

    def Hint_hash(self, m):
        h = sha3_512(m).digest()
        return sum(2 ** i * self.bit(h, i) for i in range(2 * b))

    def isoncurve(self, P):
        (x, y, z, t) = P
        return (z % q != 0 and
                x * y % q == z * t % q and
                (y * y - x * x - z * z - self.d * t * t) % q == 0)

    @staticmethod
    def bit(h, i):
        return (getitem(h, i // 8) >> (i % 8)) & 1

    def encrypt(self, your_sk, recipient_pk, message):
        h = self.to_hash(your_sk)
        a = 2 ** (b - 2) + sum(2 ** i * self.bit(h, i) for i in range(3, b - 2))
        A = self.decodepoint(recipient_pk)
        g = self.encodepoint(self.scalarmult(A, a))
        salt = os.urandom(32)
        iv = os.urandom(16)
        key_int = int.from_bytes(g, 'big') ^ int.from_bytes(salt, 'big')
        shared_key = self.to_hash_sha3_256(key_int.to_bytes(32, 'big'))
        cipher = AES.new(shared_key, AES.MODE_CBC, iv)
        encrypted_msg = cipher.encrypt(self._pad(message))
        return hexlify(salt + iv + encrypted_msg)

    @staticmethod
    def _pad(s):
        pad = 32 - len(s) % 32
        add = 32 - len(s) % 32
        return s + add * pad.to_bytes(1, 'big')

    def decrypt(self, your_sk, sender_pk, message):
        salt = unhexlify(message[:64])
        iv = unhexlify(message[64:96])
        encrypted_msg = unhexlify(message[96:])
        # print(hexlify(salt), hexlify(iv), hexlify(encrypted_msg))
        h = self.to_hash(your_sk)
        a = 2 ** (b - 2) + sum(2 ** i * self.bit(h, i) for i in range(3, b - 2))
        A = self.decodepoint(sender_pk)
        g = self.encodepoint(self.scalarmult(A, a))
        key_int = int.from_bytes(g, 'big') ^ int.from_bytes(salt, 'big')
        shared_key = self.to_hash_sha3_256(key_int.to_bytes(32, 'big'))
        cipher = AES.new(shared_key, AES.MODE_CBC, iv)
        return cipher.decrypt(encrypted_msg)

