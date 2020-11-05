import logging

from cert_issuer.errors import InsufficientFundsError
from cert_issuer.models import TransactionHandler
from cert_issuer.signer import FinalizableSigner


class EthereumSCTransactionHandler(TransactionHandler):
    def __init__(self, connector, tx_cost_constants, secret_manager, issuing_address, prepared_inputs=None):
        self.connector = connector
        self.tx_cost_constants = tx_cost_constants
        self.secret_manager = secret_manager
        self.issuing_address = issuing_address
        # input transactions are not needed for Ether
        self.prepared_inputs = prepared_inputs

    def ensure_balance(self):
        self.balance = self.connector.get_balance(self.issuing_address)

        transaction_cost = self.tx_cost_constants.get_recommended_max_cost()
        logging.info('Total cost will be %d wei', transaction_cost)

        if transaction_cost > self.balance:
            error_message = 'Please add {} wei to the address {}'.format(
                transaction_cost - self.balance, self.issuing_address)
            logging.error(error_message)
            raise InsufficientFundsError(error_message)

    def revoke_transaction(self, blockchain_bytes, app_config):
        return self.make_transaction(blockchain_bytes, app_config, "revoke_hash")

    #Outdated Function: TODO - REMOVE
    #def issue_transaction(self, blockchain_bytes, app_config):
    #    return self.make_transaction(blockchain_bytes, app_config, "issue_hash")

    def issue_transaction(self, recipient_address, token_uri, blockchain_bytes, app_config):
        return self.make_transaction(app_config, "createCertificate", recipient_address, token_uri, blockchain_bytes)

    def update_token_uri(self, token_id, token_uri, app_config):
        return self.make_transaction(app_config, "updateTokenURI", token_id, token_uri)

    def make_transaction(self, app_config, method, *argv):
        prepared_tx = self.connector.create_transaction(method, *argv)
        signed_tx = self.sign_transaction(prepared_tx)

        logging.info('Broadcasting transaction to the blockchain...')

        txid = self.broadcast_transaction(signed_tx)
        return txid

    def sign_transaction(self, prepared_tx):
        # stubbed from BitcoinTransactionHandler

        with FinalizableSigner(self.secret_manager) as signer:
            signed_tx = signer.sign_transaction(prepared_tx)

        logging.info('signed Ethereum trx = %s', signed_tx)
        return signed_tx

    def broadcast_transaction(self, signed_tx):
        txid = self.connector.broadcast_tx(signed_tx)
        return txid

    def get_event_args(self, tx_hash, event):
        return self.connector(tx_hash, event)
