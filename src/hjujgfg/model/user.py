import uuid

from hjujgfg.model.money import Wallet


class User:

    def __init__(self, chat_id):
        self.id = uuid.uuid4()
        self.chat_id = chat_id
        self.wallet = Wallet()



