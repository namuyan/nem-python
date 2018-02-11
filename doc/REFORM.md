reform functio of nem-python
============================
Simplify transaction data.  

CAUTION
------
If you reform multisig transaction, you need to check sender or recipient is your ck.  
NIS output your cosigner tx of multisig.
 
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
 
ck='NCR2CQE6AI3DIRHPHEPBSVDBOQFSHXFSQF4NIUAH'
tx_list = nem.get_account_transfer_newest(ck, call_name=nem.TRANSFER_OUTGOING)
 
tr = TransactionReform()
txs = tr.reform_transactions(tx_list)
print(txs)
```

[GO BACK](../README.md)
