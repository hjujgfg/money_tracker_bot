from typing import Optional

import telebot as tlbt
import telebot.types as types

from hjujgfg.exceptions.exceptions import NoSuchCurrencyException, NoCapsulesException, NoSuchCapsuleExcpetion
from hjujgfg.model.money import Wallet, Transaction
from hjujgfg.state import StateInterface


class NoSuchCommandState(StateInterface):

    def process(self, message: tlbt.types.Message) -> str:
        return f"I don\'t know a command {message.text}"


class StartState(StateInterface):

    def process(self, message: tlbt.types.Message) -> str:
        # return ('Hey, I can manage your spendings if you\'re not afraid '
        #        'Send "/create_wallet" command to start the process')
        return ('Hey, I can manage your spendings if you\'re not afraid.'
                ' Send /create\_wallet command to start the process')


class CreateWalletState(StateInterface):

    def process(self, message: tlbt.types.Message) -> str:
        chat_id = self._chid(message)
        exists = self.db.check_wallet_exists(chat_id)
        if exists:
            wallet = self.db.get_wallet(chat_id)
            if len(wallet.capsules) > 0:
                return f'Yo, wallet already exists with capsules: {str(wallet)}'
            else:
                return f'Yo, wallet already exists but without capsules'
        else:
            wallet = Wallet(chat_id)
            self.db.save_wallet(chat_id, wallet)
            return (f'Yo, wallet has been created, now you can add currencies you are planning to work with'
                    'To do that send me a command /add\_currency')


class ShowWalletInfo(StateInterface):

    def process(self, message: tlbt.types.Message) -> (str, Optional[tlbt.types.ReplyKeyboardMarkup]):
        chat_id = self._chid(message)
        if not self.db.check_wallet_exists(chat_id):
            return f'Yo, you don\'t have a wallet yet, please create a wallet first with /create\_wallet.'
        wallet = self.db.get_wallet(chat_id)
        currencies = ', '.join(
            list(map(lambda c: str(c), wallet.known_currencies))
        )

        capsules = '\n=============\n'.join(
            list(map(lambda c: str(c), wallet.capsules.values()))
        )
        return (f'You have following currencies:\n'
                f'*{currencies}*\n'
                f'and the **following**'
                f' capsules:\n'
                f'```\n'
                f'{capsules} '
                f'``` \n')


class AddCurrencyState(StateInterface):

    def process(self, message: tlbt.types.Message):
        chat_id = self._chid(message)
        exists = self.db.check_wallet_exists(chat_id)
        if not exists:
            return f'Yo, you don\'t have a wallet yet, please create a wallet first.'
        else:
            return 'Sure, enter its abbreviation like `USD` or `EUR`'

    def next_state(self):
        return AddCurrencyState1()


class AddCurrencyState1(StateInterface):

    def process(self, message: tlbt.types.Message) -> str:
        chat_id = self._chid(message)
        if not self.db.check_wallet_exists(chat_id):
            return 'Yo, you don\'t have a wallet yet, please run /create\_wallet command'
        wallet = self.db.get_wallet(chat_id)
        currency_name = message.text.strip().upper()
        wallet.add_currency(currency_name)
        self.db.save_wallet(chat_id, wallet)
        return (f'Yo, I\'ve added a currency {currency_name} to your wallet!,'
                f' now you can create a money capsule with this currency, just send me: '
                f'/add\_capsule. \n'
                f'Or you could add another currency if you want to')

    def next_state(self):
        return None


class AddCapsuleState(StateInterface):

    def process(self, message: tlbt.types.Message) -> str:
        chat_id = self._chid(message)
        if not self.db.check_wallet_exists(chat_id):
            return 'Yo, you don\'t have a wallet yet, please run /create\_wallet command'
        wallet = self.db.get_wallet(chat_id)
        if len(wallet.known_currencies) == 0:
            return 'Yo, you don\'t have any currencies for your wallet, please run /add\_currency command'
        else:
            return 'Cool, then enter a name for the new capsule, it\'s for you to distinguish them, should be unique.'

    def next_state(self):
        return AddCapsuleState1()


class AddCapsuleState1(StateInterface):

    def process(self, message: tlbt.types.Message) -> (str, Optional[tlbt.types.ReplyKeyboardMarkup]):
        chat_id = self._chid(message)
        self.additional_info['name'] = message.text

        wallet = self.db.get_wallet(chat_id)
        currencies = wallet.known_currencies.keys()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = list(map(lambda c: types.KeyboardButton(c), currencies))
        keyboard.add(*buttons)
        self.markup = keyboard

        return f'Great, this capsule will be known as `{message.text}`, now you need to select currency for it.'

    def next_state(self):
        next_state = AddCapsuleState2()
        next_state.additional_info['name'] = self.additional_info['name']
        return next_state


class AddCapsuleState2(StateInterface):

    def process(self, message: tlbt.types.Message) -> (str, Optional[tlbt.types.ReplyKeyboardMarkup]):
        chat_id = self._chid(message)
        if not self.db.check_wallet_exists(chat_id):
            return 'Yo, you don\'t have a wallet yet, please run /create\_wallet command'

        wallet = self.db.get_wallet(chat_id)
        selected = message.text.strip().upper()
        found = wallet.known_currencies.get(selected, None)
        if not found:
            raise NoSuchCurrencyException(
                f'There is no such currency as `{selected}` in your wallet, please add it with /add\_currency'
            )
        else:
            name = self.additional_info['name']
            self.additional_info['currency'] = found
            return (f'Okay, we have capsule `{name}` in `{selected}` currency.\n'
                    f' Now send me the amount that you have for this capsule.')

    def next_state(self):
        next_state = AddCapsuleState3()
        next_state.additional_info['name'] = self.additional_info['name']
        next_state.additional_info['currency'] = self.additional_info['currency']
        return next_state


class AddCapsuleState3(StateInterface):

    def process(self, message: tlbt.types.Message) -> (str, Optional[tlbt.types.ReplyKeyboardMarkup]):
        chat_id = self._chid(message)
        if not self.db.check_wallet_exists(chat_id):
            return 'Yo, you don\'t have a wallet yet, please run /create_wallet command'
        wallet = self.db.get_wallet(chat_id)
        try:
            amount = float(message.text.strip())
            wallet.add_capsule(
                self.additional_info['name'],
                amount,
                self.additional_info['currency']
            )
            self.db.save_wallet(chat_id, wallet)
            return 'Yo, we added a capsule to your wallet!'
        except:
            return 'Yo, you\'ve enterred something I could not parse. Please enter valid floating point number'


class ChangeBalance(StateInterface):

    def __init__(self, is_decrease: bool):
        super().__init__()
        self.additional_info['is_decrease'] = is_decrease

    def process(self, message: tlbt.types.Message) -> (str, Optional[tlbt.types.ReplyKeyboardMarkup]):
        chat_id = self._chid(message)
        if not self.db.check_wallet_exists(chat_id):
            return 'Yo, you don\'t have a wallet yet, please run /create_wallet command'

        wallet = self.db.get_wallet(chat_id)

        capsules = wallet.capsules.keys()
        if len(capsules) == 0:
            raise NoCapsulesException('You have no capsules yet, add them with /add_capsule` command')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = list(map(lambda c: types.KeyboardButton(c), capsules))
        keyboard.add(*buttons)
        self.markup = keyboard

        return f'Select a capsule to change balance of'

    def next_state(self):
        nxt = ChangeBalance2()
        nxt.additional_info['is_decrease'] = self.additional_info['is_decrease']
        return nxt


class ChangeBalance2(StateInterface):
    def process(self, message: tlbt.types.Message) -> (str, Optional[tlbt.types.ReplyKeyboardMarkup]):
        chat_id = self._chid(message)
        if not self.db.check_wallet_exists(chat_id):
            return 'Yo, you don\'t have a wallet yet, please run /create_wallet command'

        wallet = self.db.get_wallet(chat_id)
        selected = message.text.strip()
        if selected not in wallet.capsules:
            raise NoSuchCapsuleExcpetion('There is no such capsule')
        self.additional_info['selected_capsule'] = selected
        return (f'Okay, in `{selected}` you have `{wallet.capsules[selected].amount}`,'
                f'send me the amount of a transaction.')

    def next_state(self):
        next = ChangeBalance3()
        next.additional_info['selected_capsule'] = self.additional_info['selected_capsule']
        next.additional_info['is_decrease'] = self.additional_info['is_decrease']
        return next


class ChangeBalance3(StateInterface):
    def process(self, message: tlbt.types.Message) -> (str, Optional[tlbt.types.ReplyKeyboardMarkup]):
        chat_id = self._chid(message)
        if not self.db.check_wallet_exists(chat_id):
            return 'Yo, you don\'t have a wallet yet, please run /create_wallet command'
        wallet = self.db.get_wallet(chat_id)
        amount = float(message.text.strip())
        capsule = wallet.capsules[self.additional_info['selected_capsule']]
        transactions = self.db.get_transactions(chat_id)

        if self.additional_info['is_decrease']:
            capsule.spend(amount)
            transactions.append(Transaction(capsule, -amount))
        else:
            capsule.add(amount)
            transactions.append(Transaction(capsule, amount))

        self.db.save_wallet(chat_id, wallet)

        self.db.save_transactions(chat_id, transactions)
        if capsule.amount < 0.:
            return f'Done! Current amount: `{capsule.amount}`, *NOTE: it\'s below zero!*'
        else:
            return f'Done! Current amount: `{capsule.amount}`'

    def next_state(self):
        return None


class ShowTransactions(StateInterface):

    def process(self, message: tlbt.types.Message) -> (str, Optional[tlbt.types.ReplyKeyboardMarkup]):
        chat_id = self._chid(message)
        if not self.db.check_wallet_exists(chat_id):
            return 'Yo, you don\'t have a wallet yet, please run /create_wallet command'
        transactions = self.db.get_transactions(chat_id)
        parsed = '\n----------==============----------\n'\
            .join(list(map(lambda t: str(t), transactions)))

        return (f'Here is a list of your transactins:\n'
                f'``` \n'
                f'{parsed}'
                f'```')
