basic usage of nem-python
=========================
Simple usage

CAUTION
-------
All functions use SN APIs, so a connection chosen internally sometimes be unstable and return an error.
I recommend the code shown below.
```python
while True:
    try:
        result = nem.get_account_info()
        break
    except Exception as e:
        print(e)
        continue
```

Basic examples
--------------
```python
from nem_python.nem_connect import NemConnect
 
nem = NemConnect()
nem.start()
 
# Recode peers and get peers list
# {('http', 'go.nem.ninja', 7890), ('http', '153.122.13.52', 7890), ..]
nem.get_peers()
 
# Get account info
# {'meta': {'cosignatories': [], 'cosignatoryOf': [], 'status': 'LOCKED', 'remoteStatus': 'INACTIVE'}, 'account': {'address': 'NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH', 'harvestedBlocks': 32, 'balance': 108648716445, 'importance': 2.020618859543048e-05, 'vestedBalance': 104215356130, 'publicKey': 'a7d9eec00e192cdb82df471a7804974c85ba282f7f4272ec5a5dc8f640f267d3', 'label': None, 'multisigInfo': {}}}
nem.get_account_info(ck='NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH')
 
# Get account owned mosaics info
# {'nem:xem': 108648716445, 'gox:gox': 999717 ...}
nem.get_account_owned_mosaic(ck='NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH')
 
# Get account newest 25 history, incoming, outgoing, and all.
# Select by nem.TRANSFER_INCOMING, nem.TRANSFER_OUTGOING, nem.TRANSFER_ALL
# [{'meta': {'innerHash': {}, 'id': 1568525, 'hash': {'data': '190228b5d149b445dfd1d5633f602b36b9a8374a40a437df46850953ed73e89f'}, 'height': 1475687}, 'transaction': {'timeStamp': 89344239, 'amount': 10000000, 'signature': '0233b15bc70ff2355cb485ee97601ee8a6f2b2d0aeab4b20e5f552259302e8d94662560c33448dd8aabe268cbabccf735d7f92c85fc1e1c2290e3c209365ad05', 'fee': 100000, 'recipient': 'NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH', 'type': 257, 'deadline': 89430639, 'message': {'payload': '35303530376538643135', 'type': 1}, 'version': 1744830465, 'signer': '6fb74341ad3bd8002e8e8bf84f1ab6cf6eb2308af2f1db619669f5faa9f904b7'}}, {'meta': {'innerHash': {'data': '853c39ecc4d9da1243888ffb9393067a6248862ee03b22bd4acbe3c46505ea88'}, 'id': 1567163, 'hash': {'data': '14d2c6aef0617b5b63b13261235e7e52163c894fc3e6d87c9844f2fb75bbbbd1'}, ...]
nem.get_account_transfer_newest(ck='NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH', call_name=nem.TRANSFER_OUTGOING)
 
# Get account all history, incoming, outgoing, and all.
# It takes some time and is easy to fail.
nem.get_account_transfer_all(ck='NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH', call_name=nem.TRANSFER_OUTGOING)
 
# Get account newest 25 harvests
# [{'timeStamp': 86631027, 'difficulty': 109604435290570, 'totalFee': 0, 'id': 1436196, 'height': 1430846}, {'timeStamp': 86252769, 'difficulty': 95104743995256, 'totalFee': 150000, 'id': 1429693, 'height': 1424593}, ..]
nem.get_account_harvests_newest(ck='NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH')
 
# Get account all harvests
# It takes some time and is easy to fail.
nem.get_account_harvests_all(ck='NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH')
```

Encryption action
-----------------
Look sample code. [test_encryption.py](test/test_encryption.py)

mosaic calculation
------------------
```python
from nem_python.dict_math import DictMath
 
a = {"nem:xem": 1234, "cash:yen": 3345}
b = {"nem:xem": 4321, "cash:daller": 12}
print(DictMath.add(a, b))
 
c = DictMath.sub(a, b)
print(c)
 
# Check all mosaic amount plus
print(DictMath.all_plus_amount(c))
```

[GO BACK](../README.md)