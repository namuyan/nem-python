checking function of nem-python
===============================
Check New Transaction
Monitoring transaction you need to sign.

Simple
------
```python
from nem_python.nem_connect import NemConnect
import time
nem = NemConnect()
nem.start()
# Create que
multisig_que = nem.multisig_que.create()
received_que = nem.received_que.create()
 
# Add monitor Account, it's a exchange address and is good example.
nem.monitor_cks.append('NAGJG3QFWYZ37LMI7IQPSGQNYADGSJZGJRD2DIYA')
 
while True:
    time.sleep(5)
    # check multisig tx
    print(multisig_que.get_nowait())
    # check new incoming
    print(received_que.get_nowait())
 
# You can remove monitor account
# nem.monitor_cks.remove('NAGJG3QFWYZ37LMI7IQPSGQNYADGSJZGJRD2DIYA')
```

multisig_que
------------
Two type data append to Queue.  
type `new` is first notification. type `cosigner` is notification other cosigner signed.

### new
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
```

### cosigner
```python
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

received_que
------------
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

[GO BACK](../README.md)
