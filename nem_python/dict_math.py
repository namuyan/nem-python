#!/user/env python3
# -*- coding: utf-8 -*-


class DictMath:
    @staticmethod
    def add(a, b):
        # result = a + b
        c = dict()
        keys = set(a) | set(b)
        for k in keys:
            c[k] = a[k] if k in a else 0
            c[k] += b[k] if k in b else 0
        return c

    @staticmethod
    def sub(a, b):
        # result = a - b
        c = dict()
        keys = set(a) | set(b)
        for k in keys:
            c[k] = a[k] if k in a else 0
            c[k] -= b[k] if k in b else 0
        return {e: c[e] for e in c if c[e] != 0}

    @staticmethod
    def all_plus_amount(a):
        for v in a.values():
            if v < 0:
                return False
        else:
            return True
