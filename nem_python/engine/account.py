#!/user/env python3
# -*- coding: utf-8 -*-

import sqlite3
import threading
import time
import logging
import os
import random
from binascii import unhexlify, hexlify
import fasteners
from tempfile import gettempdir
from ..nem_connect import NemConnect
from ..transaction_reform import TransactionReform
from ..transaction_builder import TransactionBuilder
from ..dict_math import DictMath
from ..ed25519 import Ed25519
from .utils import int_time, tag2hex, msg2tag

F_DEBUG = True


class Account(threading.Thread):
    max_int = 256 ** 5 - 1
    outsider_id = 1
    owner_id = 2
    confirm_height = 3
    f_close = False
    f_at_first = False

    def __init__(self, nem, pk, prices, sk=None, main_net=True):
        super().__init__(name='Account', daemon=True)
        assert isinstance(pk, str), 'pk is string format'
        self.f_ok = False
        self.nem = nem
        self.sk = sk
        self.pk = pk
        self.prices = prices
        self.main_net = main_net
        self.ecc = Ed25519(main_net=main_net)
        self.ck = self.ecc.get_address(pk=pk.encode()).decode()
        dir_name = 'nem_python' + ('' if main_net else '_test')
        # data and tmp dir settings
        self.data_dir = os.path.join(os.path.expanduser('~'), dir_name)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.tmp_dir = os.path.join(gettempdir(), dir_name)
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        # DB related settings
        self.transaction = fasteners.InterProcessLock(os.path.join(self.tmp_dir, 'account.%s.lock' % self.ck))
        self.db_path = os.path.join(self.data_dir, 'account.%s.db' % self.ck)
        self.iso_level = "IMMEDIATE"  # Write時のみLock
        self._check_new_creation()
        self.db = self.create_connect()

    def create_connect(self):
        return sqlite3.connect(database=self.db_path, isolation_level=self.iso_level)

    def get_price(self, mosaic):
        return self.prices[mosaic] if mosaic in self.prices else 0.0

    def get_value(self, mosaic, amount):
        return int(self.get_price(mosaic) * amount)

    def run(self):
        logging.info("Start account engine")
        received_que = self.nem.received_que.create()
        self.nem.monitor_cks.append(self.ck)
        logging.info("1: initializing transaction data.")
        db = self.create_connect()
        incoming_many, outgoing_many = self._initialize(db)
        logging.info("2: finish initializing, income=%d, outgoing=%d" % (len(incoming_many), len(outgoing_many)))
        self.f_ok = True
        while True:
            receive = received_que.get()
            threading.Thread(target=self._confirm, name='Confirm', args=(receive,), daemon=True).start()
            logging.info("New incoming 0x%s" % receive['txhash'])

    def _confirm(self, receive):
        tr = TransactionReform(main_net=self.main_net, your_ck=self.ck)
        span = 15
        limit = receive['deadline'] - receive['time']
        count = limit // span
        while count > 0:
            count -= 1
            time.sleep(span)
            # self.confirm_height 以上Blockが進んだか？
            if self.nem.height < receive['height'] + self.confirm_height:
                continue
            # incomingにTXは含まれるか？
            txs = self.nem.get_account_transfer_newest(ck=self.ck, call_name=self.nem.TRANSFER_INCOMING)
            txs = tr.reform_transactions(txs)
            if len(txs) == 0:
                print("B")
                continue
            incoming_txhash = [tx['txhash'] for tx in txs]
            if receive['txhash'] not in incoming_txhash:
                print("C")
                continue
            # incomingに取り込まれたので記録する
            db = self.create_connect()
            with db as conn:
                hash_bin = unhexlify(receive['txhash'].encode())
                f = conn.execute("""
                SELECT `txhash` FROM `incoming_table` WHERE `txhash`= ?
                """, (hash_bin,))
                if f.fetchone() is not None:
                    print("D")
                    continue  # ダブルスペンディング防止
                from_id = self.outsider_id
                try:
                    tag = msg2tag(receive['message'])
                    to_id = self.find_user(tag=tag, address=receive['sender'], db=db)
                except:
                    import traceback
                    traceback.print_exc()
                    to_id, tag = self.create_user(group='@unknown', db=db)
                mosaics = receive['coin']
                time_int = receive['time']
                height = receive['height']
                self.move(from_id, to_id, mosaics, time_int,
                          balance_check=False, txhash=hash_bin, height=height, db=db)
            logging.info("Confirmed %s" % list(receive.values()))
            db.close()
            return

    def backup(self):
        import shutil
        with self.transaction:
            name = 'backup.%d.db' % int_time()
            shutil.copyfile(src=self.db_path, dst=os.path.join(self.data_dir, name))

    def debug(self, sql):
        if F_DEBUG:
            f = self.db.execute(sql)
            return f.fetchall()

    """ USER ACTIONS """

    def create_user(self, address=None, group=None, db=None):
        # tag無しor見知らぬAddressからの入金は毎回Userを作る
        if db is None:
            db = self.db
        with db as conn:
            while True:
                tag = random.randint(100, self.max_int)
                try:
                    conn.execute("""
                    INSERT INTO `user_table`
                    (`address`, `group`, `tag`, `time`) VALUES (?, ?, ?, ?)
                    """, (address, group, tag, int_time()))
                    conn.commit()
                    break
                except sqlite3.Error:
                    db.rollback()
            f = conn.execute("SELECT last_insert_rowid()")
            user_id = f.fetchone()[0]
        return user_id, tag

    def update_user(self, user_id, address=None, group=None, db=None):
        assert user_id > 2, 'you can edit id (>2)'
        if db is None:
            db = self.db
        with db as conn:
            for c, v, i in [('address', address, user_id), ('group', group, user_id)]:
                if v is None:
                    continue
                conn.execute("""
                UPDATE `user_table` SET `%s` = ? WHERE `userid` = ?
                """ % c, (v, i))
            conn.commit()

    def fix_user(self, delete_id, to_id, db=None):
        # Unknown user delete_id の残高を to_idへ振り分ける
        assert delete_id != to_id, "delete and fix user is same."
        if db is None:
            db = self.db
        with db as conn:
            conn.execute("""
            UPDATE `incoming_table` SET
            `userid` = ?
            WHERE `userid` = ?
            """, (to_id, delete_id))
            conn.execute("""
            UPDATE `incoming_table` SET
            `userid` = ?
            WHERE `userid` = ?
            """, (to_id, delete_id))
            conn.execute("""
            DELETE FROM `user_table`
            WHERE `userid` = ?
            """, (delete_id,))
            conn.commit()

    def find_user(self, tag=None, address=None, group=None, db=None):
        if db is None:
            db = self.db
        with db as conn:
            for name, value in [('tag', tag), ('address', address), ('group', group)]:
                if value is None:
                    continue
                f = conn.execute("""
                SELECT `userid` FROM `user_table`
                WHERE `%s` = ?
                """ % name, (value,))
                user_id = f.fetchone()
                if user_id is None:
                    continue
                else:
                    return user_id[0]
        raise AccountError('Not found user info.')

    def get_user(self, userid, db=None):
        if db is None:
            db = self.db
        with db as conn:
            f = conn.execute("""
            SELECT * FROM `user_table` WHERE `userid` = ?
            """, (userid,))
        #
        return f.fetchone()

    def id_of_group(self, group, db=None):
        assert group is not None, 'group is None type.'
        if db is None:
            db = self.db
        with db as conn:
            f = conn.execute("""
            SELECT `userid` FROM `user_table` WHERE `group` = ?
            """, (group,))
            ids = f.fetchall()
        if ids:
            return [i for (i,) in ids]
        return list()

    """ BALANCE ACTIONS """

    def balance(self, userid, db=None):
        if db is None:
            db = self.db
        with db as conn:
            conn.commit()
            f = conn.execute("""
            SELECT `mosaic`, SUM(`amount`)
            FROM `incoming_table`
            WHERE `userid` = ?
            GROUP BY `mosaic`
            """, (userid,))
            incoming = f.fetchall()
            f = conn.execute("""
            SELECT `mosaic`, SUM(`amount`)
            FROM `outgoing_table`
            WHERE `userid` = ?
            GROUP BY `mosaic`
            """, (userid,))
            outgoing = f.fetchall()
            incoming = {mosaic: amount for mosaic, amount in incoming} if incoming else list()
            outgoing = {mosaic: amount for mosaic, amount in outgoing} if outgoing else list()
            balance = DictMath.sub(incoming, outgoing)
        return balance

    def balance_group(self, db=None):
        if db is None:
            db = self.db
        with db as conn:
            conn.commit()
            f = conn.execute("""
            SELECT `userid`, `group` FROM `user_table`
            """)
            group = dict()
            for u, g in f.fetchall():
                if g in group:
                    group[g].append(str(u))
                else:
                    group[g] = [str(u)]
            balance = dict()
            for g in group:
                f = conn.execute("""
                SELECT `mosaic`, SUM(`amount`)
                FROM `incoming_table`
                WHERE `userid` IN (%s)
                GROUP BY `mosaic`
                """ % ', '.join(group[g]))
                _balance = f.fetchall()
                balance[g] = {m: a for m, a in _balance} if _balance else dict()
            return balance

    def history(self, userid, db=None):
        if db is None:
            db = self.db
        with db as conn:
            f = conn.execute("""
            SELECT
                `type`, LOWER(HEX(`txhash`)), `height`, `mosaic`, `amount`, `value`, `price`, `time`
            FROM (
            SELECT 'incoming' AS 'type', * FROM `incoming_table` WHERE userid = ?
                UNION
            SELECT 'outgoing' AS 'type', * FROM `outgoing_table` WHERE userid = ?
            ) AS `tmp` ORDER BY `height` DESC
            """, (userid, userid))
        # type 'incoming' or 'outgoing'
        transaction = f.fetchall()
        if transaction:
            return transaction
        else:
            return list()

    """ SENDING ACTIONS """

    def send(self, from_id, to_address, mosaics, msg=b'', only_check=True, encrypted=False, db=None):
        assert self.sk is not None, 'You need sk if you use \"send\"'
        to_address = to_address.replace('-', '')
        assert to_address != self.ck, "You send to and receive to same address."
        fee = self.nem.estimate_levy_fee(mosaics)
        fee = DictMath.add(fee, self.nem.estimate_msg_fee(msg))
        fee = DictMath.add(fee, self.nem.estimate_send_fee(mosaics))
        if encrypted:
            msg = self.ecc.encrypt(self.sk, self.pk, msg)
            msg = unhexlify(msg.encode())
            msg_type = 2
        else:
            msg_type = 1
        tx_dict = self.nem.mosaic_transfer(self.pk, to_address, mosaics, msg, msg_type)
        tb = TransactionBuilder()
        tx_hex = tb.encode(tx_dict)
        tx_sign = self.ecc.sign(tx_hex, self.sk, self.pk)
        if only_check:
            balance = self.balance(from_id)
            need_amount = DictMath.add(fee, mosaics)
            send_ok = DictMath.all_plus_amount(DictMath.sub(balance, need_amount))
            # only_check=False return sending info, NOT send
            return fee, send_ok, tx_dict, tx_hex, tx_sign
        else:
            with self.transaction:
                if db is None:
                    db = self.db
                with db as conn:
                    conn.commit()
                    balance = self.balance(from_id)
                    need_amount = DictMath.add(fee, mosaics)
                    if not DictMath.all_plus_amount(DictMath.sub(balance, need_amount)):
                        raise AccountError('You try to withdraw beyond ID:%d have.' % from_id)
                    tx_hash = self.nem.transaction_announce(tx_hex, tx_sign)
                    outgoing_many = list()
                    for mosaic in need_amount:
                        # height, time is None
                        amount = need_amount[mosaic]
                        value = self.get_value(mosaic, amount)
                        price = self.get_price(mosaic)
                        outgoing_many.append((
                            unhexlify(tx_hash.encode()), None, from_id, mosaic, amount, value, price, None
                        ))
                    conn.executemany("""
                    INSERT INTO `outgoing_table` VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, outgoing_many)
                    conn.commit()
                threading.Thread(target=self._send, name='Wait',
                                 args=(tx_hash, db), daemon=False).start()
            return tx_hash

    def _send(self, txhash):
        span = 10
        limit = self.nem.retention // span
        tr = TransactionReform(main_net=self.main_net, your_ck=self.ck)
        db = self.create_connect()
        while limit > 0:
            limit -= 1
            time.sleep(span)
            txs = self.nem.get_account_transfer_newest(self.ck, self.nem.TRANSFER_OUTGOING)
            txs = tr.reform_transactions(txs)
            for tx in txs:
                if tx['txhash'] != txhash:
                    continue
                with db as conn:
                    conn.execute("""
                    UPDATE `outgoing_table` SET `height`= ?, `time`= ? WHERE `txhash`= ?
                    """, (tx['height'], tx['time'], unhexlify(txhash.encode())))
                    conn.commit()
                logging.info("Sending success 0x%s" % txhash)
                db.close()
                return
        logging.info("Failed sending 0x%s" % txhash)

    def move_by_group(self, from_group, to_group, mosaics, db=None):
        assert from_group is not None, 'You need to set from_group'
        assert to_group is not None, 'You need to set to_group'
        from_id = self.find_user(group=from_group)
        to_id = self.find_user(group=to_group)
        balance = self.balance_group(db=db)
        remain = DictMath.sub(balance[from_group], mosaics)
        if DictMath.all_plus_amount(remain):
            return self.move(from_id=from_id, to_id=to_id, mosaics=mosaics, balance_check=False, db=db)
        else:
            raise AccountError('You try to move more balance than from_id have.')

    def move(self, from_id, to_id, mosaics, time_int=None, balance_check=True, txhash=None, height=None, db=None):
        assert from_id != to_id, "Account of sender and recipient is same."
        if db is None:
            db = self.db
        with db as conn:
            with self.transaction:
                conn.commit()
                if time_int is None:
                    time_int = int_time()
                if txhash is None:
                    txhash = os.urandom(20)  # inner tx is 20bytes
                else:
                    assert isinstance(txhash, bytes), 'txhash is raw binary'
                    f = conn.execute("""
                    SELECT `txhash` FROM `incoming_table` WHERE `txhash`= ?
                    """, (txhash,))
                    if f.fetchone() is not None:
                        raise AccountError('Already inserted txhash to incoming_table.')
                    f = conn.execute("""
                    SELECT `txhash` FROM `outgoing_table` WHERE `txhash`= ?
                    """, (txhash,))
                    if f.fetchone() is not None:
                        raise AccountError('Already inserted txhash to incoming_table.')

                height = height if height else self.nem.height
                assert to_id or from_id, "sender and receiver is unknown."
                if balance_check:
                    balance = self.balance(from_id)
                    if not DictMath.all_plus_amount(DictMath.sub(balance, mosaics)):
                        raise AccountError('You try to withdraw beyond ID:%d have.' % from_id)
                if to_id != self.outsider_id:
                    incoming = [  # to_idに入金される
                                  (txhash, height, to_id, m, a, self.get_value(m, a), self.get_price(m), time_int)
                                  for m, a in sorted(mosaics.items())]
                    conn.executemany("""
                    INSERT INTO `incoming_table` VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?)""", incoming)

                if from_id != self.outsider_id:
                    outgoing = [  # from_idから出金される
                                  (txhash, height, from_id, m, a, self.get_value(m, a), self.get_price(m), time_int)
                                  for m, a in sorted(mosaics.items())]
                    conn.executemany("""
                    INSERT INTO `outgoing_table` VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?)""", outgoing)
                conn.commit()
        return hexlify(txhash).decode()

    # Inner actions
    def _check_new_creation(self):
        if os.path.exists(self.db_path):
            return
        self.f_at_first = True
        with self.create_connect() as db:
            try:
                db.execute("""
                CREATE TABLE `incoming_table` (
                `txhash` BLOB, `height` INTEGER,
                `userid` INTEGER, `mosaic` TEXT, `amount` INTEGER,
                `value` INTEGER, `price` REAL,
                `time` INTEGER
                )""")
                db.execute("""
                CREATE TABLE `outgoing_table` (
                `txhash` BLOB, `height` INTEGER,
                `userid` INTEGER, `mosaic` TEXT, `amount` INTEGER,
                `value` INTEGER, `price` REAL,
                `time` INTEGER
                )""")
                db.execute("""
                CREATE TABLE `user_table` (
                `userid` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                `address` TEXT UNIQUE, `group` TEXT, `tag` INTEGER UNIQUE,
                `time` INTEGER
                )""")
                execute = """
                CREATE INDEX `idx_incoming_txhash` ON `incoming_table` (`txhash`)
                CREATE INDEX `idx_incoming_height` ON `incoming_table` (`height`)
                CREATE INDEX `idx_incoming_userid` ON `incoming_table` (`userid`)
                CREATE INDEX `idx_outgoing_txhash` ON `outgoing_table` (`txhash`)
                CREATE INDEX `idx_outgoing_height` ON `outgoing_table` (`height`)
                CREATE INDEX `idx_outgoing_userid` ON `outgoing_table` (`userid`)
                CREATE INDEX `idx_user_address` ON `user_table` (`address`)
                CREATE INDEX `idx_user_group` ON `user_table` (`group`)
                CREATE INDEX `idx_user_tag` ON `user_table` (`tag`)
                """.split("\n")
                for code in execute:
                    if len(code) > 10:
                        db.execute(code)
                # Add unknown user add
                if self.create_user(group='@outsider', db=db)[0] != self.outsider_id:
                    raise AccountError('OutsiderID differ from created.')
                if self.create_user(group='@owner', db=db)[0] != self.owner_id:
                    raise AccountError('OwnerID differ from created.')
                # Outsider's tag is None
                db.execute("""
                UPDATE `user_table` SET `tag` = NULL
                WHERE `userid` = ?
                """, (self.outsider_id,))
                db.commit()
            except sqlite3.Error as e:
                db.close()
                os.remove(self.db_path)
                assert AccountError('Failed create db, %s' % e)

    def _get_history(self, call):
        count = 100
        while count > 0:
            try:
                return self.nem.get_account_transfer_all(
                    ck=self.ck, call_name=call, c=10000)
            except Exception as e:
                time.sleep(5)
                logging.info("Failed _get_history %s" % e)
                continue
        raise AccountError('Cannot get account history.')

    def _initialize(self, db):
        tr = TransactionReform(main_net=self.main_net, your_ck=self.ck)
        incoming = self._get_history(self.nem.TRANSFER_INCOMING)
        incoming = tr.reform_transactions(incoming)[::-1]
        outgoing = self._get_history(self.nem.TRANSFER_OUTGOING)
        outgoing = tr.reform_transactions(outgoing)[::-1]

        with db as conn:
            conn.commit()
            incoming_many = list()
            for tx in incoming:
                if tx['recipient'] != self.ck:
                    continue
                txhash = unhexlify(tx['txhash'].encode())
                f = conn.execute("""
                SELECT `txhash` FROM `incoming_table` WHERE `txhash`= ? """, (txhash,))
                if f.fetchone() is not None:
                    continue
                height = tx['height']
                try:
                    if self.f_at_first:
                        userid = self.owner_id
                    else:
                        tag = msg2tag(tx['message'])
                        userid = self.find_user(tag=tag, address=tx['sender'], db=db)
                except:
                    import traceback
                    traceback.print_exc()
                    userid, tag = self.create_user(group='@unknown', db=db)
                for mosaic in tx['coin']:
                    amount = tx['coin'][mosaic]
                    value = self.get_value(mosaic, amount)
                    price = self.get_price(mosaic)
                    incoming_many.append((
                        txhash, height, userid, mosaic, amount, value, price, tx['time']
                    ))
            if len(incoming_many) > 0:
                conn.executemany("""
                INSERT INTO `incoming_table` VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, incoming_many)

            outgoing_many = list()
            for tx in outgoing:
                if tx['sender'] != self.ck:
                    continue
                txhash = unhexlify(tx['txhash'].encode())
                f = conn.execute("""
                SELECT `txhash`, `height` FROM `outgoing_table` WHERE `txhash`= ?
                """, (txhash,))
                txs = f.fetchall()
                if len(txs) > 0:
                    for txhash_, height_ in txs:
                        if height_ is None:
                            # UPDATE失敗TXを修正
                            conn.execute("""
                            UPDATE `outgoing_table` SET `height`= ?, `time`= ?
                            WHERE `txhash`= ?
                            """, (tx['height'], tx['time'], txhash_))
                            break
                    else:
                        continue  # 取り込まれなかったと思われるTXは手動削除
                else:
                    height = tx['height']
                    if self.f_at_first:
                        userid = self.owner_id
                    else:
                        userid, tag = self.create_user(group='@unknown', db=db)  # Unknown user
                    fee = self.nem.estimate_levy_fee(tx['coin'])
                    fee = DictMath.add(fee, {'nem:xem': tx['fee']})
                    all_amount = DictMath.add(fee, tx['coin'])
                    for mosaic in all_amount:
                        amount = all_amount[mosaic]
                        if amount == 0:
                            continue
                        value = self.get_value(mosaic, amount)
                        price = self.get_price(mosaic)
                        outgoing_many.append((
                            txhash, height, userid, mosaic, amount, value, price, tx['time']
                        ))
            if len(outgoing_many) > 0:
                conn.executemany("""
                INSERT INTO `outgoing_table` VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, outgoing_many)
            if len(incoming_many) > 0 or len(outgoing_many) > 0:
                conn.commit()
        return incoming_many, outgoing_many


class AccountError(Exception): pass
