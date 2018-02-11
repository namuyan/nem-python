sending function of nem-python
==============================
Send functions

CAUTION
-------
You should be careful, avoid **double spending**.  
Although you receive error by API, you should be suspicious by deadline.

Examples
--------
```python
from nem_python.nem_connect import NemConnect
 
nem = NemConnect()
nem.start()
 
# Estimate sending fee
# {'nem:xem': 100000}
nem.estimate_send_fee(mosaics={"nem:xem": 1000, "namuyan:faucet": 122})
 
# Estimate message fee, msg is None or bytes
# {'nem:xem': 50000}
nem.estimate_msg_fee(msg=b'hello world')
 
# Estimate levy fee
# {'nem:xem': 1000000, 'dim:coin': 1}
nem.estimate_levy_fee(mosaics={"dim:coin": 1000, "gold:gold": 10})
 
# Simple mosaic transfer transaction object maker
# msg_type=1 non-encrypted, msg_type=2 encrypted
# {'type': 257, 'version': 1744830465, 'signer': '80d2ae0d784d28db38b5b85fd77e190981cea6f4328235ec173a90c2853c0761', 'timeStamp': 89347608, 'deadline': 89354808, 'recipient': 'NCLW2T3CRAD36NW557T7ABX4BNXWI4AQWHVCB6TK', 'amount': 100000, 'fee': 100000, 'message': {'type': 1, 'payload': '68656c6c6f20776f726c64'}}
sender_pk = '80d2ae0d784d28db38b5b85fd77e190981cea6f4328235ec173a90c2853c0761'  # Sender public key
recipient_ck = 'NCLW2T3CRAD36NW557T7ABX4BNXWI4AQWHVCB6TK'  # Recipient compressed key
nem.mosaic_transfer(sender_pk, recipient_ck, mosaics={"nem:xem": 100000}, msg_body=b'hello world')
```

broadcast
--------
```python
from nem_python.nem_connect import NemConnect
from nem_python.transaction_builder import TransactionBuilder
from nem_python.ed25519 import Ed25519
 
nem = NemConnect()
nem.start()
 
# create raw transaction
tb = TransactionBuilder()
tx_dict = {
    'type': 257, 'version': -1744830463,
    'signer': '80d2ae0d784d28db38b5b85fd77e190981cea6f4328235ec173a90c2853c0761',
    'timeStamp': 89357633, 'deadline': 89364833,
    'recipient': 'NCLW2T3CRAD36NW557T7ABX4BNXWI4AQWHVCB6TK',
    'amount': 100000, 'fee': 100000,
    'message': {'type': 1, 'payload': '68656c6c6f20776f726c64'}
}
tx_hex = tb.encode(tx_dict)
print(tx_hex)
 
# sign transaction
secret_key = '6a858fb93e0202fa62f894e591478caa23b06f90471e7976c30fb95efda4b312'
public_key = '80d2ae0d784d28db38b5b85fd77e190981cea6f4328235ec173a90c2853c0761'
sign = Ed25519.sign(tx_hex, secret_key, public_key)
 
# broadcast transaction
tx_hash = nem.transaction_announce(tx_hex, sign)
print(tx_hash)
```

[GO BACK](../README.md)