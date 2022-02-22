from datetime import datetime
import requests
from utils.main_bot.settings import apis


class Wallet:

    def __init__(self,
                 start_bank: float,
                 fee: float,
                 percents: float,
                 ticker: str
                 ):
        """
        :param start_bank: - total amount of money you've invested
        :param fee: - platform's fee size
        """
        self._start_bank = start_bank
        self.ticker = ticker
        self.fee_size = fee
        self.trades = 0
        self.qty = 0
        self.total_fee = 0
        self.shares = 0
        self.SAFETY_CONST = 0.99
        self.percents = percents
        self.start_date = datetime.now()
        self.last_timestamp = None
        self.asset = None
        self.token = apis[2]
        self.chat_id = apis[3]
        self._init_assets()

    def get_safe_money(self):
        """
        Money that were not used for trading, but were invested.
        :return:
        """
        return self._safe_money

    def get_start_bank(self):
        """
        Invested amount.
        :return:
        """
        return self._start_bank

    def get_crypto_bank(self):
        """
        Currently bought quantity of currency.
        :return:
        """
        return self.shares

    def set_quantity(self, token_price, decimals) -> None:
        """
        Calculate quantity to buy.
        :param token_price:
        :param decimals:
        :return:
        """
        self.qty = round(float(self.asset) * self.percents / float(token_price), decimals)

    def _init_assets(self) -> None:
        """
        Initializes first buy size.
        :return:
        """
        self.asset = self._start_bank * self.SAFETY_CONST
        self._safe_money = self._start_bank - self.asset

    def summary(self):
        """
        Shows summary report, with all the stats
        :return:
        """
        summary = f'\n#Сводка по #{self.ticker[:-4]}:\n'\
                  f'Общее кол-во сделок: {self.trades}\n'\
                  f'Профит: ${round(self.asset - (self._start_bank * self.SAFETY_CONST), 2)}\n'\
                  f'Профит за вычетом комиссий: ${round(self.asset - (self._start_bank * self.SAFETY_CONST) - self.total_fee, 2)}\n' \
                  f'Уплачено комиссий: ${round(self.total_fee, 2)}\n' \
                  f'Доход(%): {round((100 * self.asset - self.total_fee / (self._start_bank * self.SAFETY_CONST)) - 100, 2)}%'
        return summary

    def _notify(self, msg):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        msg_data = {
            'chat_id': self.chat_id,
            'text': msg,
            'parse_mode': 'HTML'
        }
        requests.post(url, data=msg_data)

    def notify_error(self, e):
        msg = f'#ERROR\nВозникла ошибка: {e}\n' \
              f'Бот - {self.ticker}\n' \
              f'Если это сообщение повторяется неоднократно, значит нужно чинить!\n' \
              f'Напиши челу в тг: @JayZAnsh'
        self._notify(msg)

    def notify_deal(self, deal_type, timestamp, amount, ticker, price, report=False) -> None:
        msg = f'{timestamp} #{deal_type} {amount} #{ticker} по цене ${price}\nНа сумму ${round(float(amount)*float(price), 2)}'
        self._notify(msg)

        if report:
            report_msg = self.summary()
            self._notify(report_msg)

    def buy(self, price: float, amount: float):
        self._buy(price, amount)

    def sell(self, price: float):
        self._sell(price)

    def _buy(self, price: float, amount: float) -> None:
        """
        Implements buying process, calculates fee
        :param price:
        :return:
        """
        self.shares = amount
        deal = price * self.shares
        self.asset -= deal
        self.total_fee += deal * self.fee_size
        self.notify_deal(deal_type='Куплено',
                         timestamp=datetime.now(),
                         amount=self.shares,
                         ticker=self.ticker,
                         price=price,
                         )

    def _sell(self, price: float) -> None:
        """
        Implements selling process
        :param price:
        :return:
        """
        self.trades += 1
        deal = float(self.shares) * float(price)
        self.asset += deal
        self.total_fee += deal * self.fee_size
        self.notify_deal(deal_type='Продано',
                         timestamp=datetime.now(),
                         amount=self.shares,
                         ticker=self.ticker,
                         price=price,
                         report=True,
                         )
        self.shares = 0


# if __name__ == '__main__':
#     wal = Wallet(start_bank=1000.0,
#                  fee=0.0075,
#                  percents=0.2,
#                  ticker="BTCBUSD",
#                  )
#     from exceptions import TechnicalIndicatorsError
#     wal.chat_id = 517321921
#     wal.token = '5267388557:AAEzz1Bi_vjwUxJXO8Icp5cDLszTGPkx52s'
#     wal.buy(35000, 0.5)
