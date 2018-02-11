Multisig of nem-python
======================
Multisig function of NEM is flexisible.

Examples
--------
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

[GO BACK](../README.md)
