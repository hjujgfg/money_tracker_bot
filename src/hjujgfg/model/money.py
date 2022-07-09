import uuid
from typing import List, Dict
from uuid import UUID


class Currency:

    def __init__(self, name: str):
        self.name: str = name

    @staticmethod
    def from_json_dict(json_dict):
        return Currency(json_dict['name'])

    def __str__(self):
        return self.name


class Wallet:

    def __init__(self, chat_id):
        self.capsules: Dict[str, MoneyCapsule] = {}
        self.known_currencies: Dict[str, Currency] = {}
        self.chat_id = chat_id

    def add_capsule(self, name: str, amount: float, currency: Currency):
        capsule = MoneyCapsule(
            name, amount, currency
        )
        self.capsules[name] = capsule

    def add_currency(self, name: str):
        self.known_currencies[name] = Currency(name)

    def get_capsules(self):
        return self.capsules.keys()

    def get_capsule_info(self, name):
        return self.capsules.get(name, None)

    @staticmethod
    def from_json_dict(json_dict):
        wallet = Wallet(
            json_dict['chat_id']
        )

        for name, capsule_dict in json_dict.get('capsules', {}).items():
            wallet.capsules[name] = MoneyCapsule.from_json_dict(capsule_dict)

        for name, currency_dict in json_dict.get('known_currencies', {}).items():
            wallet.known_currencies[name] = Currency.from_json_dict(currency_dict)

        return wallet

    def __str__(self):
        capsules = list(map(lambda c: str(c), self.capsules.keys()))
        currencies = list(map(lambda c: str(c), self.known_currencies.keys()))
        if len(capsules) == 0:
            capsules = "`No Capsules yet`"
        if len(currencies) == 0:
            currencies = '`No Currencie yet`'
        return f'Currencies: {currencies}, capsules: {capsules}'


class MoneyCapsule:

    def __init__(self, name: str, amount: float, currency: Currency):
        self.name = name
        self.amount: float = amount
        self.currency: Currency = currency

    def spend(self, amount: float):
        self.amount -= amount

    @staticmethod
    def from_json_dict(json_dict):
        return MoneyCapsule(
            json_dict['name'],
            json_dict['amount'],
            Currency.from_json_dict(json_dict['currency'])
        )

    def __str__(self):
        return f'{self.name}: {self.amount} {str(self.currency)}'
