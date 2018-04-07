#!/user/env python3
# -*- coding: utf-8 -*-

from binascii import unhexlify
from nem_ed25519.key import get_address
from nem_ed25519.encrypt import decrypt


class TransactionReform:
    """
        シングルシグ・マルチシグ、Mosaic・XEMなど
        送金TXの違いを吸収する(送金以外は除かれる)

        [dict]
        txtype, txhash, height, version, time, deadline, sender, recipient
        coin, fee, message, message_type, signature

        'coin': { example
            'manekineko.neko:tanuki': 100,
             'nem:xem': 22107642
        }

        [message_type]
        0 = no message(unicode)
        1 = plain message(unicode)
        2 = decrypted message(utf8 bytes)
        3 = hexcode(utf8 hex)
        4 = not decrypted message(utf8 hex)

    """

    def __init__(self, main_net=True, your_sk=None, your_ck=None):
        self.main_net = main_net
        self.your_ck = your_ck
        self.your_sk = your_sk

    def reform_transactions(self, tx_list):
        assert type(tx_list) is list, 'input should be list.'
        if len(tx_list) > 0:
            his = list()
            for tx_dict in tx_list:
                tx_type = self._tx_version(tx_dict)
                if 0x0101 == tx_type:
                    try:
                        his.append(self._reform_transaction(tx_dict))
                    except TransactionReformError as e:
                        continue
            return his
        else:
            return list()

    @staticmethod
    def _tx_version(tx):
        if 'data' in tx['meta']['innerHash']:
            return tx['transaction']['otherTrans']['type']  # wrapper tx
        else:
            return tx['transaction']['type']  # single tx

    def _reform_transaction(self, tx):
        """ Notice: only 0x0101(257) version (transfer transaction) """
        r = dict()
        if 'data' in tx['meta']['innerHash']:
            # wrapper tx
            inner_tx = tx['transaction']['otherTrans']
            r['txtype'] = inner_tx['type']
            r['txhash'] = tx['meta']['innerHash']['data']
            r['height'] = tx['meta']['height']
            r['version'] = inner_tx['version']
            r['time'] = inner_tx['timeStamp'] + 1427587585
            r['deadline'] = inner_tx['deadline'] + 1427587585

            r['sender'] = self.pk2ck(inner_tx['signer'])
            r['recipient'] = inner_tx['recipient']

            # マルチシグTXでは子署名者も含まれるので除く
            if self.your_ck is not None and self.your_ck not in (r['sender'], r['recipient']):
                raise TransactionReformError('You are not sender or recipient.')

            if 'mosaics' not in inner_tx:
                # ver1 tx
                r['coin'] = {'nem:xem': inner_tx['amount']}

            else:
                # ver2 tx
                mux = round(inner_tx['amount'] / 1000000)
                r['coin'] = {}
                for mosaic in inner_tx['mosaics']:
                    mosaic_name = mosaic['mosaicId']['namespaceId'] + ':' + mosaic['mosaicId']['name']
                    r['coin'][mosaic_name] = mosaic['quantity'] * mux

            r['fee'] = inner_tx['fee']

            r = self.decode_msg(r, inner_tx)

            r['signature'] = tx['transaction']['signature']

        else:
            # single tx
            r['txtype'] = tx['transaction']['type']
            r['txhash'] = tx['meta']['hash']['data']
            r['height'] = tx['meta']['height']
            r['version'] = tx['transaction']['version']
            r['time'] = tx['transaction']['timeStamp'] + 1427587585
            r['deadline'] = tx['transaction']['deadline'] + 1427587585

            r['sender'] = self.pk2ck(tx['transaction']['signer'])
            r['recipient'] = tx['transaction']['recipient']

            if 'mosaics' not in tx['transaction']:
                # ver1 tx
                r['coin'] = {'nem:xem': tx['transaction']['amount']}

            else:
                # ver2 tx
                mux = round(tx['transaction']['amount'] / 1000000)
                r['coin'] = {}
                for mosaic in tx['transaction']['mosaics']:
                    mosaic_name = mosaic['mosaicId']['namespaceId'] + ':' + mosaic['mosaicId']['name']
                    r['coin'][mosaic_name] = mosaic['quantity'] * mux

            r['fee'] = tx['transaction']['fee']

            r = self.decode_msg(r, tx['transaction'])

            r['signature'] = tx['transaction']['signature']
        return r

    def decode_msg(self, r, tran):
        if 'payload' in tran['message']:
            if tran['message']['payload'][:2] == 'fe' and tran['message']['type'] == 1:
                # 任意の16進コード
                r['message'] = tran['message']['payload']
                r['message_type'] = 3

            elif tran['message']['type'] == 1:
                # 通常メッセージ
                try:
                    msg_hex = tran['message']['payload'].encode('utf-8')
                    r['message'] = unhexlify(msg_hex).decode('utf-8')
                    r['message_type'] = 1
                except:
                    r['message'] = tran['message']['payload']
                    r['message_type'] = 3

            elif tran['message']['type'] == 2:
                # 暗号化メッセージ
                msg_hex = tran['message']['payload'].encode()
                try:
                    r['message'] = decrypt(sk=self.your_sk, pk=tran['signer'], enc=unhexlify(msg_hex))
                    r['message_type'] = 2
                except:
                    r['message'] = msg_hex.decode()
                    r['message_type'] = 4

            else:
                raise Exception("unknown message type %s" % tran['message']['type'])

        else:
            r['message'] = ''
            r['message_type'] = 0

        return r

    def pk2ck(self, pk):
        return get_address(pk, main_net=self.main_net)


class TransactionReformError(Exception): pass
