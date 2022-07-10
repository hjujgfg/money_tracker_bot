import telebot as tbot
from telebot.types import Message
import hjujgfg.secrets_getter as secret
from hjujgfg.constants import START_COMMAND, CREATE_WALLET_COMMAND, ADD_CURRENCY_COMMAND, ADD_CAPSULE_COMMAND, \
    SHOW_WALLET_COMMAND, SPEND, ADD, SHOW_TRANSACTIONS_COMMAND
from hjujgfg.database.database import WalletDataAccessorInterface, FileWalletDataAccessor
from hjujgfg.state.state_machine import StateMachine

token = secret.get_api_token()
bot = tbot.TeleBot(token)
machine = StateMachine(bot)

data_accessor: WalletDataAccessorInterface = FileWalletDataAccessor()


def _chid(message: Message) -> int:
    return message.chat.id


def extract_command(arg):
    return arg.split()[0][1:]


@bot.message_handler(commands=[
    START_COMMAND, CREATE_WALLET_COMMAND, ADD_CURRENCY_COMMAND, ADD_CAPSULE_COMMAND, SHOW_WALLET_COMMAND, SPEND,
    ADD, SHOW_TRANSACTIONS_COMMAND
])
def start_command(message: Message):
    # state_machine.process_command(chat_id, '')
    machine.process_command(extract_command(message.text), message)


@bot.message_handler(content_types=['text'])
def handle_text_from_user(message: Message):
    machine.process_message(message)


def start_bot():
    bot.polling()
