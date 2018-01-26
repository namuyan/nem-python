nem-python
==========
nem-python is simple NEM library.  
[README-JP.md](README-JP.md)

Feature
-------
* Do not require NIS running on local.
* You can sign on this library.
* Useful transaction builder.
* Useful simplify transaction.

Require
-------
Python3 (>=3.5)

HowToUse
-----
```python
from nem_python.nem_connect import NemConnect
nem = NemConnect(main_net=True)
nem.start()
```

[HOWTOUSE.md](HOWTOUSE.md)

Samples
------
Look test folder.

Author
------
[@namuyan_mine](http://twitter.com/namuyan_mine/)

Licence
-------
MIT