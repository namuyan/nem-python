how to use
==========


# CLASS
* `from nem_python.nem_connect import NemConnect`
    * Base class of this lib.
    * Communicate with free APIs of SuperNode.
* `from nem_python.transaction_builder import TransactionBuilder`
    * Converter transaction object to binary.
* `from nem_python.transaction_reform import TransactionReform`
    * Reformat of incoming and outgoing transaction.
    * Single and Multi sig can be used as same.
* `from nem_python.dict_math import DictMath`
    * Mosaic amount calculator class.
* `from nem_python.ed25519 import Ed25519`
    * Encryption class. sign, verify, encrypt, decrypt.
    
# Usage
### Basic functions

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

### Send functions
You should be careful, avoid double spending.

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

### Multisig functions
```python
from nem_python.nem_connect import NemConnect
 
nem = NemConnect()
nem.start()
 
# sending from multisig account
cosigner_pk = '80d2ae0d784d28db38b5b85fd77e190981cea6f4328235ec173a90c2853c0761'
multisig_pk = '28e8469422106f406051a24f2ea6402bac6f1977cf7e02eb3bf8c11d4070157a'
recipient_ck = 'NCLW2T3CRAD36NW557T7ABX4BNXWI4AQWHVCB6TK'
mosaics = {"nem:xem": 10000}
nem.multisig_mosaics_transfer(cosigner_pk, multisig_pk, recipient_ck, mosaics)
 
# Create multisig account
multisig_pk = '28e8469422106f406051a24f2ea6402bac6f1977cf7e02eb3bf8c11d4070157a'
cosigner_pks = ['80d2ae0d784d28db38b5b85fd77e190981cea6f4328235ec173a90c2853c0761']
cosigner_require = 0  # 0 means N of N multisig creation
nem.multisig_account_creation(multisig_pk, cosigner_pks, cosigner_require)
 
# Modification multisig account
cosigner_pk = '80d2ae0d784d28db38b5b85fd77e190981cea6f4328235ec173a90c2853c0761'
multisig_pk = '28e8469422106f406051a24f2ea6402bac6f1977cf7e02eb3bf8c11d4070157a'
remove_pk = ['1234....54321']  # remove from cosigner
cosigner_change = -1 # relative change, 0 means no change
nem.multisig_account_modification(cosigner_pk, multisig_pk, remove_pk, cosigner_change)
```

### transaction broadcast
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

### reform transaction
Simplify transaction data.  
* message_type
    * 0 = no message(unicode)
    * 1 = plain message(unicode)
    * 2 = decrypted message(utf8 bytes)
    * 3 = hexcode(utf8 hex)
    * 4 = not decrypted message(utf8 hex)
* sample
    ```text
    [
        {
            'txtype': 257, 
            'txhash': 'bb383bc1cbcf04e70c681a86e8f4cdb5d829aa458cf422402aeacc32c26e6567', 
            'height': 1473702, 
            'version': 1744830466, 
            'time': 1516811458, 
            'deadline': 1516815058, 
            'sender': 'NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH', 
            'recipient': 'NCVGXTCV7YYGCUTOWRSEALEVHVTDFRJ54BQYDKTI', 
            'coin': 
            {'halloween2017:candy': 10}, 
            'fee': 350000, 
            'message': 
            'TipNEM 出金', 
            'message_type': 1, 
            'signature': '8c7d131a60d1b8495f56ccce7c2a91aaf5ba28e5425ea44b11884da7b03ec44da9f92df892532590cef8062f3254b61d8ee7818528d89d1cb367668776c15a0c'
        }
  ]
    ```

```python
from nem_python.nem_connect import NemConnect
from nem_python.transaction_reform import TransactionReform
 
nem = NemConnect()
nem.start()
 
tx_list = nem.get_account_transfer_newest(ck='NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH', call_name=nem.TRANSFER_OUTGOING)
 
tr = TransactionReform()
txs = tr.reform_transactions(tx_list)
print(txs)
```

### Mosaic amount calculate
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

### Encryption action
Look sample code. [test_encryption.py](test/test_encryption.py)

### Check New Transaction
Monitoring transaction you need to sign.
```python
from nem_python.nem_connect import NemConnect
import time
nem = NemConnect()
nem.start()
 
# Add monitor Account, it's a exchange address and is good example.
nem.monitor_cks.append('NAGJG3QFWYZ37LMI7IQPSGQNYADGSJZGJRD2DIYA')
 
while True:
    time.sleep(5)
    # check multisig tx
    print(nem.unconfirmed_multisig_que.get_nowait())
    # check new incoming
    print(nem.new_received_que.get_nowait())
 
# You can remove monitor account
# nem.monitor_cks.remove('NAGJG3QFWYZ37LMI7IQPSGQNYADGSJZGJRD2DIYA')
```

**unconfirmed_multisig_que**  
Two type data append to Queue.  
type `new` is first notification. type `cosigner` is notification other cosigner signed.
```python
a = {
    'type': 'new',
    'txhash': '6bffafe04d4d5d8e0a8a21d55ed9d014122c260080445e4192f4cd4b7a5b2a5e',
    'account': 'NAGJG3QFWYZ37LMI7IQPSGQNYADGSJZGJRD2DIYA',
    'inner_tx': {
        'timeStamp': 89452819,
        'amount': 3986000000,
        'fee': 50000,
        'recipient': 'NC5BSBLYDHPRBMX4NZ7BKWIJWSAMKKIRJ7IITW6V',
        'type': 257,
        'deadline': 89456419,
        'message': {},
        'version': 1744830465,
        'signer': 'fbae41931de6a0cc25153781321f3de0806c7ba9a191474bb9a838118c8de4d3'
    },
    'all_cosigner': ['NBEM6SFOHU5PORIGAVG3NNJIMCG73R2TWEEIDAZ5', 'NCTWKWGD564GIQQCZ5X5TC4YM46VXWLT3QWD5NLZ'],
    'need_cosigner': 2
}
b = {
    'type': 'cosigner',
    'txhash': '3eb20079eb130ec2322e46f156e6ee364d827afe4b916f78861cebd829147535',
    'account': 'NAGJG3QFWYZ37LMI7IQPSGQNYADGSJZGJRD2DIYA',
    'inner_tx': {
        'timeStamp': 89455580,
        'amount': 5900000000,
        'fee': 50000, 
        'recipient': 'NASCQBZDV2MCDJNQXKJWCOKCFILCCSYZFVGLRRWS',
        'type': 257,
        'deadline': 89459180,
        'message': {}, 
        'version': 1744830465, 
        'signer': 'fbae41931de6a0cc25153781321f3de0806c7ba9a191474bb9a838118c8de4d3'
    }, 
    'cosigner': 'NAGJG3QFWYZ37LMI7IQPSGQNYADGSJZGJRD2DIYA'
}
```

**new_received_que**  
Notify you new incoming.
```python
a = {
    'txtype': 257,
    'txhash': '91815b4bc16016a503bc54db46222f22b421fa7b9a46acf280f53eb66f1d09a0',
    'height': 1477640,
    'version': 1744830465,
    'time': 1517050264,
    'deadline': 1517136664,
    'sender': 'NBPCLQ2IPDU4UCVVPCCRFUTKRN742UQRE67MQBEE',
    'recipient': 'NAGJG3QFWYZ37LMI7IQPSGQNYADGSJZGJRD2DIYA',
    'coin': {'nem:xem': 1850000},
    'fee': 100000, 
    'message': 'a8feb7d76b87d5ce',
    'message_type': 1,
    'signature': 'ea5ff0fd5e31665b75099699ffd0741209ba3851187052c85b1fc1aac39b47706f59dadee5344f1aa20828c146fdfdba87f2ef0a1121f7052c6a117f50d42c0e'
}
```