nem-python
==========
nem-python is simple NEM library.  
[README-JP.md](README-JP.md)

Feature
-------
* Do **not** require NIS running on local.
* You can sign on **offline**.
* Useful transaction builder.
* Useful simplify transaction.

Require
-------
Python3 (>=3.5)

how to use
-----
```python
from nem_python.nem_connect import NemConnect
nem = NemConnect(main_net=True)
nem.start()
```

[all class](doc/CLASS.md)
[basic usage](doc/BASIC-USAGE.md)
[sending](doc/SENDING.md)
[multisig](doc/MULTISIG.md)
[receive check](doc/RECEIVE-CHECK.md)
[reform](doc/REFORM.md)

Samples
------
Look test folder.

Author
------
[@namuyan_mine](http://twitter.com/namuyan_mine/)

Licence
-------
MIT