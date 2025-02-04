# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
from aea.crypto.helpers import get_address_from_public_key
from aea.crypto.ledger import LedgerApi
from aea.protocols.contract_api import ContractApiMessage
from aea.protocols.ledger_api import LedgerApiMessage

from packages.valory.skills.abstract_round_abci.contracts import Contract
from packages.valory.skills.abstract_round_abci.contracts.contract_lib import Contract_Base   
from packages.valory.skills.abstract_round_abci.contracts.contract_lib import Jsonrpc
from packages.valory.skills.abstract_round_abci.contracts.contract_lib import wait_for_transaction_confirmation
from packages.valory.skills.abstract_round_abci.contracts.contract_lib import ContractMethodApiArgs
    
import logging
    
class SimpleContract(Contract):
    """SimpleContract"""

    contract_id = "simple_contract"

    @classmethod
    def get_raw_transaction(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        **kwargs: ContractMethodApiArgs,
    ) -> ContractApiMessage:
        """Get raw transaction data for the contract."""
        return ContractApiMessage(
            performative=ContractApiMessage.Performative.RAW_TRANSACTION,
            ledger_id=ledger_api.identifier,
            contract_id=cls.contract_id,
            contract_address=contract_address,
            callable="read_value",
            value=0,
            data=b"",
        )

    @classmethod
    def get_raw_message(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        **kwargs: ContractMethodApiArgs,
    ) -> LedgerApiMessage:
        """Get a message for interacting with the contract."""
        raise NotImplementedError

    @classmethod
    def get_state(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        **kwargs: ContractMethodApiArgs,
    ) -> LedgerApiMessage:
        """Get the state of the contract."""
        read_value = Jsonrpc()
        # Implement the method to interact with the smart contract
        response = ledger_api.build_query_method_call(
            contract_id=cls.contract_id,
            contract_address=contract_address,
            method_name="readValue",
            args=[],
        )

        raise NotImplementedError

    @classmethod
    def verify_transaction(
        cls,
        ledger_api: LedgerApi,
        transaction: LedgerApiMessage,
        signed_transaction: LedgerApiMessage,
    ) -> bool:
        """Verify a transaction."""
        # Implement your transaction verification logic here
        return True
    
    @classmethod
    def send_transaction(
        cls,
        ledger_api: LedgerApi,
        transaction: LedgerApiMessage,
    ) -> LedgerApiMessage:
        """Send a transaction to the ledger."""
        # Implement your transaction sending logic here
        # This is a dummy implementation that always returns a success response.
        return LedgerApiMessage(
            performative=LedgerApiMessage.Performative.RAW_TRANSACTION,
            ledger_id=ledger_api.identifier,
            contract_id=cls.contract_id,
            transaction=transaction,
        )

def read_value(ledger_api: LedgerApi, contract_address: str) -> Optional[int]:
    try:
        response = ledger_api.get_state(
            ledger_callable="call",
            function_name="readValue",
            contract_address=contract_address,
            contract_id="simple_contract",
            args={},
        )
        
        if response.performative == LedgerApiMessage.Performative.STATE:
            value = response.state.body["readValue"]
            return value
        else:
            logging.error(f"Error retrieving the value from the smart contract: {response}")
            return None

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
