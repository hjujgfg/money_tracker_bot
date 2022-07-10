import os
import pickle
from enum import Enum
from os.path import exists
from typing import List

from hjujgfg.exceptions.exceptions import NoWalletException
from hjujgfg.model.money import Wallet, MoneyCapsule, Transaction


class State(Enum):
    ADDING_CAPSULE = 1,


class WalletDataAccessorInterface:

    def check_wallet_exists(self, chat_id: int) -> bool:
        pass

    def save_wallet(self, chat_id: int, wallet: Wallet) -> None:
        pass

    def get_wallet(self, chat_id: int) -> Wallet:
        pass

    def get_capsule(self, chat_id: int, capsule_name: str) -> MoneyCapsule:
        pass

    def check_state_exists(self, chat_id: int):
        pass

    def get_state(self, chat_id: int):
        pass

    def save_state(self, chat_id: int, state):
        pass

    def drop_state(self, chat_id: int):
        pass

    def save_transactions(self, chat_id: int, transactions: List[Transaction]):
        pass

    def get_transactions(self, chat_id: int) -> List[Transaction]:
        pass


class FileWalletDataAccessor(WalletDataAccessorInterface):

    @staticmethod
    def _get_chat_wallet_file(chat_id: int):
        return f'data/wallets/{chat_id}.m'

    @staticmethod
    def _get_chat_state_file(chat_id: int):
        return f'data/states/{chat_id}.json'

    @staticmethod
    def _get_transactions_file(chat_id: int):
        return f'data/transactions/{chat_id}.m'

    def check_wallet_exists(self, chat_id: int):
        wallet_file_path = FileWalletDataAccessor._get_chat_wallet_file(chat_id)
        return exists(wallet_file_path)

    def save_wallet(self, chat_id: int, wallet: Wallet) -> None:
        with open(self._get_chat_wallet_file(chat_id), 'wb') as f:
            pickle.dump(wallet, f)
            # json.dump(wallet.__dict__, f, default=lambda o: o.__dict__, indent=4)

    def get_wallet(self, chat_id: int):
        if not self.check_wallet_exists(chat_id):
            raise NoWalletException()

        with open(self._get_chat_wallet_file(chat_id), 'rb') as f:
            return pickle.load(f)
            # json_dict = json.load(f)
            # return Wallet.from_json_dict(json_dict)

    def get_capsule(self, chat_id: int, capsule_name: str):
        pass

    def check_state_exists(self, chat_id: int):
        state_file_path = self._get_chat_state_file(chat_id)
        return exists(state_file_path)

    def get_state(self, chat_id: int):
        if self.check_state_exists(chat_id):
            with open(self._get_chat_state_file(chat_id), 'rb') as f:
                return pickle.load(f)
        return None

    def save_state(self, chat_id: int, state):
        with open(self._get_chat_state_file(chat_id), 'wb') as f:
            return pickle.dump(state, f)

    def drop_state(self, chat_id: int):
        if self.check_state_exists(chat_id):
            os.remove(self._get_chat_state_file(chat_id))

    def save_transactions(self, chat_id: int, transactions: List[Transaction]):
        with open(self._get_transactions_file(chat_id), 'wb') as f:
            pickle.dump(transactions, f)

    def get_transactions(self, chat_id: int) -> List[Transaction]:
        transactions_file_path = FileWalletDataAccessor._get_transactions_file(chat_id)
        if not exists(transactions_file_path):
            return []
        with open(self._get_transactions_file(chat_id), 'rb') as f:
            return pickle.load(f)
