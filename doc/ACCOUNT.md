class Account of nem-python
===========================
This help you build off-chain system.  
System provide identification tag to each users, 
You can edit balance each user without any fee.

This is alpha version! 

Basic
=====
You need setup NemConnect.  
If you don't need sending function, not need `sk`.
```python
from nem_python.nem_connect import NemConnect
from nem_python.engine.account import Account
 
main_net = False
nem = NemConnect(main_net=main_net)
nem.start()
# example
sk = '2d8347a3312bca46bdb67c9da60447617f6a5d0c44f8458e28612a4e6f615a6b'
pk = 'cab1fe0ce0889d5c7807afc0b96c8eca6b02628aea2c3fb65b11950c5bee65e0'
ck = 'TAOXSZJDCFJ3YPOTAH72CIYOUGLZCTIZBFTFXQ5X'
 
# sk is option, need for send function and encrypted message decode.
ant = Account(nem=nem, pk=pk, sk=sk, main_net=main_net)
ant.start()
```

History
-------
```python
# Get user balance dict
# return: {'nem:xem': 14588981, 'namuyan:nemrin': 1}
ant.balance(userid)
 
 
# Get group balance dict
# :param group: group[str]
# return: {
#   '@outsider': {},
#   '@owner': {'0bitcoin.bitcoin:btc': 1000000, 'nem:xem': 12314000}
# }
ant.balance_group(group)
 
 
# Get all group's balance
# return: {
# '@expired': {},   <= expired mosaic transaction replaced to this user
# '@outsider': {},  <= deposit and withdraw transaction's dummy user
# '@owner': {'namuyan:nemrin': 1, 'nem:xem': 24352970}, <= owner account, first balance is owner's
# '@unknown': {'nem:xem': 40002},   <= no bind info incoming transaction's user
# 'namuyan': {'nem:xem': 13410000}} <= I creatae example user manually
ant.balance_all_group()
 
 
# Get user transaction history
# return: list[
# (type[str], txhash[str], height[int], mosaic[str], amount[int], value[int], price[float], time[int])
# ,..]
ant.history(userid)
 
 
# Get group transaction history
# :param group: group[str]
# return: list[
# (type[str], txhash[str], height[int], mosaic[str], amount[int], value[int], price[float], time[int])
# ,..]
ant.history_group(group)
```

User
----
```python
# Get userid list of group
# return: userid[list]
ant.id_of_group(group)
 
 
# Create user, bing address or group
# If you send to address with hex message, bind to user.
# If you set address, tx of incoming to address bind to user.
# :param address: bind address[str] (option)
# :param group: bind group[str] (option)
# :return: tuple(userid[int], tag[int])
ant.create_user(address=None, group=None)
 
 
# Update user bind info.
# :param user_id: userid[int]
# :param address: bind address[str] (option)
# :param group: bind group[str] (option)
ant.update_user(user_id, address=None, group=None)
 
 
# Fix user balance
# move balance delete_id  => to_id
# and delete user info of delete_id.
# CAUTION: Not recommend for often use.
ant.fix_user(delete_id, to_id)
 
 
# Find user by tag, address or group
# return: userid[int] or raise AccountError
ant.find_user(tag=None, address=None, group=None)
 
 
# Get user info by userid.
# return: (userid[int], address[str], tag[int], time[int])
ant.get_user(userid)
```

Price
-----
*price* is not exchange price, you setup privately.
```python
# Setup Mosaic price, inner value.
# :param mosaic: mosaic 'nem:xem' [str]
# :param price: price/amount [float]
ant.update_price(mosaic, price)
 
 
# Get all price you setup.
# return: mosaics, {mosaic[str]: price/amount[float]}
ant.get_prices()
 
 
# Get price of mosaic
# :param mosaic: mosaic 'nem:xem' [str]
# return: price/amount [float]
ant.get_price(mosaic)
 
 
# Calculate value
# :param mosaic: mosaic 'nem:xem' [str]
# :param amount: amount [int]
# :return: value[int] = price/amount[float] * mosaic_amount[int]
ant.get_value(mosaic, amount)
```

Send
----
```python
# Send from userid
# :param from_id: userid[int]
# :param to_address: address[str]
# :param mosaics: mosaics[dict]
# :param msg: binary message[bytes]
# :param only_check: check tx info[bool]
# :param balance_check: check enough balance[bool]
# :param encrypted: encrypt by inner function[bool] (option)
# :return: 
# :return: only_check=True , (fee[dict], send_ok[bool], tx_dict[dict], tx_hex[hex str], tx_sign[hex str])
# :return: only_check=False, txhash[hex str]
ant.send(from_id, to_address, mosaics, msg=b'', only_check=True, balance_check=True, encrypted=False)
 
 
# Send from group
# S:param from_group: group[str]
# S:param to_address: address[str]
# S:param mosaics: mosaics[dict]
# S:param encrypted: encrypt by inner function[bool] (option)
# S:return: txhash[hex str]
ant.send_by_group(from_group, to_address, mosaics, msg=b'', encrypted=False)
 
 
# Move balance
# :param from_group: group name [str]
# :param to_group: group name [str]
# :param mosaics: mosaics [dict]
# :return: txhash[hex str]
ant.move_by_group(from_group, to_group, mosaics)
 
 
# Move user balance
# :param from_id: userid [int]
# :param to_id: userid [int]
# :param mosaics: mosaics [dict]
# :param time_int: time [int]
# :param balance_check: True=allow minus balance [bool]
# :param txhash: binary txhash [bytes]
# :param height: height [int]
# :return: txhash [hex str]
ant.move(from_id, to_id, mosaics, time_int=None, balance_check=True, txhash=None, height=None, db=None)
```

System
------
```python
# Backup db file to data dir
ant.backup()
 
 
# refresh all data.
# It is necessary to reflect DB update of other thread.
ant.refresh()
 
 
# Debug tool, execute SQL directory
# :param sql: SQL [str]
# :param explain: True=explain sql, False=execute sql [bool]
# :return: fetchall() [tuple]
ant.debug(sql='SELECT * FROM user_table')
 
 
# create connection to database
# sqlite3 not allow using other thread, not thread safe.
# return: <sqlite3.Connection object at 0x000001D30DB82570>
db = ant.create_connect()
```

[GO BACK](../README.md)