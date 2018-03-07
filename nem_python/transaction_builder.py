#!/user/env python3
# -*- coding: utf-8 -*-

from binascii import hexlify, unhexlify
from nem_ed25519.key import get_address


class TransactionBuilder:
    binary = b''
    const4bytes_blank = int(0).to_bytes(4, "little")
    const4bytes_signer = int(32).to_bytes(4, "little")
    const4bytes_address = int(40).to_bytes(4, "little")

    def encode(self, tx_dict):
        if tx_dict['type'] == 0x0101:
            if 'mosaics' in tx_dict:
                self.tx_ver2(tx_dict)
            else:
                self.tx_ver1(tx_dict)
        elif tx_dict['type'] == 0x1001:
            # multisig creation
            self.modify_multisig(tx_dict)
        elif tx_dict['type'] == 0x1004:
            # multisig transaction
            self.with_inner_tx(tx_dict)
        elif tx_dict['type'] == 0x1002:
            # sign multisig tx as cosigner
            self.sign_multisig_tx(tx_dict)
        else:
            # none transfer tx
            raise Exception("not found transaction version")
        return hexlify(self.binary).decode()

    def _common_header(self, tx_dict):
        self.binary += tx_dict['type'].to_bytes(4, "little")  # tx type 0x0101
        self.binary += tx_dict['version'].to_bytes(4, "little", signed=True)  # version 0x01000098
        self.binary += tx_dict['timeStamp'].to_bytes(4, "little")  # timestamp 0xccaa7704
        self.binary += self.const4bytes_signer  # const 0x20000000
        self.binary += unhexlify(tx_dict['signer'].encode('utf8'))  # signer 32 bytes
        self.binary += tx_dict['fee'].to_bytes(8, "little")  # fee 0xa086010000000000
        self.binary += tx_dict['deadline'].to_bytes(4, "little")  # deadline 0xdcb87704
        return

    def tx_ver1(self, tx_dict):
        self._common_header(tx_dict)
        self.binary += self.const4bytes_address            # const 28000000
        self.binary += tx_dict['recipient'].encode('utf8')  # signer 40 bytes
        self.binary += tx_dict['amount'].to_bytes(8, "little")  # amount 0x40420f0000000000

        if 'payload' in tx_dict['message'] and len(tx_dict['message']['payload']) > 0:
            msg_length = len(tx_dict['message']['payload']) // 2

            self.binary += int(msg_length + 8).to_bytes(4, "little")  # msg body 0x23000000
            self.binary += tx_dict['message']['type'].to_bytes(4, "little")  # msg type 0x01000000
            self.binary += msg_length.to_bytes(4, "little")  # msg length 0x1b000000
            self.binary += unhexlify(tx_dict['message']['payload'].encode('utf8'))  # msg payload 27

        else:
            # no message
            # Note: if the length is 0 then the following 2 fields (msg length, msg payload) do not apply.
            self.binary += self.const4bytes_blank
        return

    def tx_ver2(self, tx_dict):
        # first section same with ver1
        self.tx_ver1(tx_dict)

        """ add mosaic section """
        self.binary += len(tx_dict['mosaics']).to_bytes(4, "little")  # Number of mosaics 0x01000000

        # The following part is repeated for every mosaic in the attachment.
        # NIS bug, need mosaic order
        mosaic_dict = {e['mosaicId']['namespaceId']+e['mosaicId']['name']: e for e in tx_dict['mosaics']}
        for name in sorted(mosaic_dict.keys()):
            mosaic = mosaic_dict[name]
            namespace_id = mosaic['mosaicId']['namespaceId'].encode('utf8')
            namespace_id_len = len(namespace_id).to_bytes(4, "little")

            name = mosaic['mosaicId']['name'].encode('utf8')
            name_len = len(name).to_bytes(4, "little")

            mosaic_id_structure = namespace_id_len + namespace_id + name_len + name
            mosaic_id_structure_len = len(mosaic_id_structure).to_bytes(4, "little")

            value = mosaic['quantity'].to_bytes(8, "little")

            mosaic_structure = mosaic_id_structure_len + mosaic_id_structure + value
            mosaic_structure_len = len(mosaic_structure).to_bytes(4, "little")

            self.binary += mosaic_structure_len + mosaic_structure
        return

    def modify_multisig(self, tx_dict):
        self._common_header(tx_dict)
        self.binary += len(tx_dict['modifications']).to_bytes(4, "little")  # cosign num

        is_mainnet = tx_dict['version'] == 1744830464
        cosigners = {
            get_address(e['cosignatoryAccount'], main_net=is_mainnet):
                (e['modificationType'], e['cosignatoryAccount'])
            for e in tx_dict['modifications']}

        for account in sorted(cosigners, reverse=False):
            co_type = cosigners[account][0]
            pubkey = cosigners[account][1]
            self.binary += self.const4bytes_address  # const 0x28000000
            self.binary += co_type.to_bytes(4, "little")  # cosig type
            self.binary += self.const4bytes_signer  # const 0x20000000
            self.binary += unhexlify(pubkey.encode('utf8'))  # pubkey

        if tx_dict['minCosignatories']['relativeChange'] < 0:
            self.binary += int(4).to_bytes(4, "little")
            self.binary += tx_dict['minCosignatories']['relativeChange'].to_bytes(4, "little", signed=True)
        elif tx_dict['minCosignatories']['relativeChange'] > 0:
            self.binary += int(4).to_bytes(4, "little")
            self.binary += tx_dict['minCosignatories']['relativeChange'].to_bytes(4, "little")
        return

    def with_inner_tx(self, tx_dict):
        self._common_header(tx_dict)

        inner_tx = TransactionBuilder()
        inner_tx.encode(tx_dict['otherTrans'])
        self.binary += len(inner_tx.binary).to_bytes(4, "little")  # inner transaction length
        self.binary += inner_tx.binary
        return

    def sign_multisig_tx(self, tx_dict):
        self._common_header(tx_dict)
        self.binary += int(36).to_bytes(4, "little")  # ナニコレ？
        self.binary += self.const4bytes_signer
        self.binary += unhexlify(tx_dict['otherHash']['data'].encode('utf8'))
        self.binary += self.const4bytes_address
        self.binary += unhexlify(tx_dict['otherAccount'].encode('utf8'))
