# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2023-2024 Valory AG
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

"""This module contains the class to connect to an ERC20 token contract."""

from typing import Dict

from aea.common import JSONLike
from aea.configurations.base import PublicId
from aea.contracts.base import Contract
from aea.crypto.base import LedgerApi
from aea_ledger_ethereum import EthereumApi


PUBLIC_ID = PublicId.from_str("valory/erc20:0.1.0")


class ERC20(Contract):
    """The ERC20 contract."""

    contract_id = PUBLIC_ID

    @classmethod
    def check_balance(
        cls,
        ledger_api: EthereumApi,
        contract_address: str,
        account: str,
    ) -> JSONLike:
        """Check the balance of the given account."""
        contract_instance = cls.get_instance(ledger_api, contract_address)
        balance_of = getattr(contract_instance.functions, "balanceOf")  # noqa
        token_balance = balance_of(account).call()
        wallet_balance = ledger_api.api.eth.get_balance(account)
        return dict(token=token_balance, wallet=wallet_balance)

    @classmethod
    def get_allowance(
        cls,
        ledger_api: EthereumApi,
        contract_address: str,
        owner: str,
        spender: str,
    ) -> JSONLike:
        """Check the balance of the given account."""
        contract_instance = cls.get_instance(ledger_api, contract_address)
        allowance = contract_instance.functions.allowance(owner, spender).call()
        return dict(data=allowance)

    @classmethod
    def build_deposit_tx(
        cls,
        ledger_api: EthereumApi,
        contract_address: str,
    ) -> Dict[str, bytes]:
        """Build a deposit transaction."""
        contract_instance = cls.get_instance(ledger_api, contract_address)
        data = contract_instance.encodeABI("deposit")
        return {"data": bytes.fromhex(data[2:])}

    @classmethod
    def build_withdraw_tx(
        cls,
        ledger_api: EthereumApi,
        contract_address: str,
        amount: int,
    ) -> Dict[str, bytes]:
        """Build a deposit transaction."""
        contract_instance = cls.get_instance(ledger_api, contract_address)
        data = contract_instance.encodeABI("withdraw", args=(amount,))
        return {"data": bytes.fromhex(data[2:])}

    @classmethod
    def build_approval_tx(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        spender: str,
        amount: int,
    ) -> Dict[str, bytes]:
        """Build an ERC20 approval."""
        contract_instance = cls.get_instance(ledger_api, contract_address)
        checksumed_spender = ledger_api.api.to_checksum_address(spender)
        data = contract_instance.encodeABI("approve", args=(checksumed_spender, amount))
        return {"data": bytes.fromhex(data[2:])}

    @classmethod
    def build_transfer_tx(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        recipient: str,
        amount: int,
    ) -> Dict[str, bytes]:
        """Build an ERC20 transfer."""
        contract_instance = cls.get_instance(ledger_api, contract_address)
        checksumed_recipient = ledger_api.api.to_checksum_address(recipient)
        data = contract_instance.encodeABI("transfer", args=(checksumed_recipient, amount))
        return {"data": bytes.fromhex(data[2:])}
    
    //new
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

def write_value(ledger_api: LedgerApi, contract_address: str, new_value: int) -> Optional[str]:
    try:
        transaction = ledger_api.build_transaction(
            ledger_callable="get_raw_transaction",
            function_name="writeValue",
            contract_id="simple_contract",
            contract_address=contract_address,
            new_value=new_value,
        )
        
        if transaction.performative == LedgerApiMessage.Performative.RAW_TRANSACTION:
            return transaction.raw_transaction.body["tx_hash"]
        else:
            logging.error(f"Error building transaction for writeValue: {transaction}")
            return None

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
