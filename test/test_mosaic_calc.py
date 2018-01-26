#!/user/env python3
# -*- coding: utf-8 -*-

from nem_python.dict_math import DictMath

from nem_python.dict_math import DictMath

a = {"nem:xem": 1234, "cash:yen": 3345}
b = {"nem:xem": 4321, "cash:daller": 12}
print(DictMath.add(a, b))

c = DictMath.sub(a, b)
print(c)
print(DictMath.all_plus_amount(c))
