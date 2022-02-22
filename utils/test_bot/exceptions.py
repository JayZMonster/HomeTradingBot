class TransactionCostMoreThanBank(Exception):

    def __init__(self, req_bank):
        self._required_bank = req_bank

    def __str__(self):
        return "You've just set your transaction cost more than your start bank. " \
               "Set your percentage to the number that is less or equals 1.00"


class MoneyIsOver(Exception):

    def __str__(self):
        return 'You have not enough money in your bank to proceed this operation!'


class TechnicalIndicatorsError(Exception):

    def __str__(self):
        return 'Error while trying to apply technical indicators.'


class MissingKeyParameter(Exception):

    def __str__(self):
        return 'Check if you stated these parameters: -api_key, -api_secret, -ticker, -invest'


class SignalError(Exception):

    def __str__(self):
        return 'Error while trying to calculate signal!'


class BinanceDataError(Exception):

    def __str__(self):
        return 'Error getting data from binance!'
