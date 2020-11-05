"""
Base class for building blockchain transactions to issue Blockchain Certificates.
"""
import logging
from eth_utils import is_checksum_address
from web3 import Web3
from cert_issuer.errors import BroadcastError

MAX_TX_RETRIES = 5


class Issuer:
    def __init__(self, certificate_batch_handler, transaction_handler, max_retry=MAX_TX_RETRIES):
        self.certificate_batch_handler = certificate_batch_handler
        self.transaction_handler = transaction_handler
        self.max_retry = max_retry

    def issue(self, chain, app_config, recipient_address):
        """
        Issue the certificates on the blockchain
        :return:
        """

        blockchain_bytes = self.certificate_batch_handler.prepare_batch()
        
        recipient_address = Web3.toChecksumAddress(recipient_address)
        print(is_checksum_address(recipient_address))
	    #change token_uri address
        token_uri = "https://bloxberg.org"
        #blockchain_bytes = str(blockchain_bytes, 'latin-1')
        blockchain_bytes = blockchain_bytes.hex()
        for attempt_number in range(0, self.max_retry):
            try:
                txid = self.transaction_handler.issue_transaction(recipient_address, token_uri, blockchain_bytes, app_config)
                event_args = self.transaction_handler.get_event_args(txid, 'Transfer')
                token_id = event_args['tokenId']

                self.certificate_batch_handler.finish_batch(txid, chain, app_config)
                logging.info('Broadcast transaction with txid %s', txid)
                return (txid, token_id)
            except BroadcastError:
                logging.warning(
                    'Failed broadcast reattempts. Trying to recreate transaction. This is attempt number %d',
                    attempt_number)
        logging.error('All attempts to broadcast failed. Try rerunning issuer.')
        raise BroadcastError('All attempts to broadcast failed. Try rerunning issuer.')

    def update_token_uri(self, token_id, token_uri, app_config):
        """
        Update the tokenURI for the issued certificate batch
        :return: transaction id
        """

        for attempt_number in range(0, self.max_retry):
            try:
                txid = self.transaction_handler.update_token_uri(token_id, token_uri, app_config)
                logging.info('Updating tokenURI field with ipfs link. Txid: %s', txid)
                return txid
            except BroadcastError:
                    logging.warning(
                        'Failed broadcast reattempts. Trying to recreate transaction. This is attempt number %d',
                        attempt_number)
        logging.error('All attempts to broadcast failed. Try rerunning issuer.')
        raise BroadcastError('All attempts to broadcast failed. Try rerunning issuer.')


