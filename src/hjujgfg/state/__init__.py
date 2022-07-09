from typing import Optional

from hjujgfg.database.database import WalletDataAccessorInterface, FileWalletDataAccessor
import telebot as tlbt


class StateInterface:

    def __init__(self):
        self.db: WalletDataAccessorInterface = FileWalletDataAccessor()
        self.additional_info = {}
        self.markup = None

    @staticmethod
    def _chid(message: tlbt.types.Message):
        return message.chat.id

    def process(self, message: tlbt.types.Message) -> (str, Optional[tlbt.types.ReplyKeyboardMarkup]):
        pass

    def next_state(self):
        pass
