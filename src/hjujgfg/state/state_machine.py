import random
from typing import Dict

import telebot as tbot

from hjujgfg.exceptions.exceptions import LogicalError
from hjujgfg.constants import START_COMMAND, ADD_CURRENCY_COMMAND, CREATE_WALLET_COMMAND, \
    IDK_VARIATIONS, ADD_CAPSULE_COMMAND, SHOW_WALLET_COMMAND, SPEND
from hjujgfg.database.database import FileWalletDataAccessor, WalletDataAccessorInterface
from hjujgfg.state import StateInterface
from hjujgfg.state.states import StartState, AddCurrencyState, NoSuchCommandState, CreateWalletState, AddCapsuleState, \
    ShowWalletInfo, SpendMoney1


class StateMachine:

    def __init__(self, bot: tbot.TeleBot):
        self.curren_state = None
        self.bot = bot
        self.command_to_initial_state: Dict[str, StateInterface] = {
            START_COMMAND: StartState(),
            CREATE_WALLET_COMMAND: CreateWalletState(),
            SHOW_WALLET_COMMAND: ShowWalletInfo(),
            ADD_CURRENCY_COMMAND: AddCurrencyState(),
            ADD_CAPSULE_COMMAND: AddCapsuleState(),
            SPEND: SpendMoney1()
        }

        self.db: WalletDataAccessorInterface = FileWalletDataAccessor()

    def process_command(self, command: str, message: tbot.types.Message):
        chat_id = message.chat.id
        if self.db.check_state_exists(chat_id):
            self.bot.send_message(chat_id, 'Previous command seems to be not completed,'
                                           f' please redo it if you\'re still interested afterwards.'
                                           f' Now performing {command}')

        current_state = self.command_to_initial_state.get(command, NoSuchCommandState())
        result = current_state.process(message)
        next_state = current_state.next_state()
        if next_state:
            self.db.save_state(chat_id, next_state)
        else:
            self.db.drop_state(chat_id)

        if result:
            print(f'Current state: {current_state}')
            if current_state.markup:
                self.bot.send_message(
                    message.chat.id,
                    result,
                    reply_markup=current_state.markup,
                    parse_mode='markdown')
            else:
                print(f'Current state no markup: {current_state}')
                keyboard = tbot.types.ReplyKeyboardRemove(False)
                self.bot.send_message(message.chat.id, result, parse_mode='markdown', reply_markup=keyboard)

    def process_message(self, message: tbot.types.Message):
        try:
            chat_id = message.chat.id
            if not self.db.check_state_exists(chat_id):
                self.bot.send_message(chat_id, random.choice(IDK_VARIATIONS))
            else:
                current_state: StateInterface = self.db.get_state(chat_id)
                print(f'{current_state}: {message.text}')
                result = current_state.process(message=message)
                next_state = current_state.next_state()
                if next_state:
                    self.db.save_state(chat_id, next_state)
                else:
                    self.db.drop_state(chat_id)

                if result:
                    print(f'Current state: {current_state}')
                    if current_state.markup:
                        self.bot.send_message(
                            message.chat.id,
                            result,
                            reply_markup=current_state.markup,
                            parse_mode='markdown')
                    else:
                        print(f'Current state no markup: {current_state}')
                        keyboard = tbot.types.ReplyKeyboardRemove(False)
                        self.bot.send_message(message.chat.id, result, parse_mode='markdown', reply_markup=keyboard)
        except LogicalError as e:
            self.bot.send_message(message.chat.id, str(e))

