import datetime
from time import sleep

from binance import Client
from binance.enums import *
import utils.test_bot.settings as settings
import utils.test_bot.bot_api as api
from utils.test_bot.signals import Signal
from utils.test_bot.wallet import Wallet
from utils.test_bot.exceptions import *


class StochBot:

    def __init__(self,
                 api_key: str,
                 api_secret: str,
                 ticker: str,
                 cash: float,
                 percents: float,
                 fee: float,
                 test_net: str,
                 ):
        """
        Main body of trading stoch_bot.

        :param api_key: Binance API KEY
        :param api_secret: Binance API SECRET
        """
        #  Bot settings
        self.client = Client(api_key, api_secret)
        self.ticker = ticker
        self.decimals = None
        self.investments = cash
        self.fee = fee
        self.deal_type = None
        self.percents = percents
        self.test_net = test_net
        self.stoch_ranges = settings.stoch_ranges
        self.rsi_trigger = settings.rsi_trigger
        self.macd_trigger = settings.macd_trigger
        self.window = settings.window
        self.smooth_window = settings.smooth_window
        self.lags = settings.lags
        # self.strategy = strategy

        # Network settings
        self.wallet = None
        self.active_deal = False
        self.active_price = None
        self.find_decimals()
        self.init_wallet()

    def init_wallet(self):
        self.wallet = Wallet(
            start_bank=self.investments,
            fee=self.fee,
            percents=self.percents,
            ticker=self.ticker,
        )

    def init_test_net(self):
        if self.test_net and self.test_net == 'yes':
            self.test_net = True
            self.notify('Торговля ведется в тестовом режиме!')
        else:
            self.test_net = False
            self.notify('Торговля ведется в реальном режиме!')

    def find_decimals(self):
        """
        Find out how many decimals current trading asset has.
        :return:
        """
        found = False
        self.notify('Пытаюсь получить данные о торговой паре.')
        while not found:
            try:
                info = self.client.get_symbol_info(self.ticker)
                found = True
            except:
                self.notify('Ошибка, пытаюсь снова.')
                sleep(3)
                continue
        self.notify('Успешно!')
        step_size = str(info['filters'][2]['stepSize'])
        self.decimals = step_size.index('1') - 1 if step_size.index('1') != 0 else step_size.index('1')

    @staticmethod
    def notify(msg):
        print(f'{datetime.datetime.now()} System: {msg}')

    def info(self, active: bool, klines):
        if not active:
            print(f'\nПара: {self.ticker}\n'
                  f'\nИндикаторы покупки:\n'
                  f'RSI > 50: {klines["rsi"][-1] > self.rsi_trigger}\n'
                  f'MACD > Signal: {klines["macd"][-1] > self.macd_trigger}\n'
                  f'20 < Stoch.%K < 80: {self.stoch_ranges[0] < klines["%K"][-1] < self.stoch_ranges[1]}\n'
                  f'20 < Stoch.%D < 80: {self.stoch_ranges[0] < klines["%D"][-1] < self.stoch_ranges[1]}\n')
        else:
            print(f'\nПара: {self.ticker}\n'
                  f'Индикаторы продажи:\n'
                  f'RSI < 50: {klines["rsi"][-1] < self.rsi_trigger}\n'
                  f'MACD < Signal: {klines["macd"][-1] < self.macd_trigger}\n'
                  f'20 < Stoch.%K < 80: {self.stoch_ranges[0] < klines["%K"][-1] < self.stoch_ranges[1]}\n'
                  f'20 < Stoch.%D < 80: {self.stoch_ranges[0] < klines["%D"][-1] < self.stoch_ranges[1]}\n')

    def work(self):
        """
        Function that makes trades
        :return:
        """
        try:
            self.init_test_net()
            self.notify(f'\nБот работает! {self.ticker}\n')
            # Getting ticker's historical data, sometimes binance returns APIExceptions
            try:
                if not self.active_deal:
                    self.notify('Жду пока сработают индикаторы на покупку!')
                if self.active_deal:
                    self.notify('Жду пока сработают индикаторы на продажу!')
                klines = api.get_minute_data(
                    symbol=self.ticker,
                    client=self.client,
                )
            except:
                self.notify(BinanceDataError())
                self.wallet.notify_error(BinanceDataError())
                return BinanceDataError()

            # Calculating rsi, macd, stoch
            try:
                api.apply_tech_indicators(klines,
                                          window=self.window,
                                          smooth_window=self.smooth_window,
                                          )
            except:
                self.notify(TechnicalIndicatorsError())
                self.wallet.notify_error(TechnicalIndicatorsError())
                return TechnicalIndicatorsError()

            # Creating signal's instance to get buy signal
            try:
                signal = Signal(data=klines,
                                lags=self.lags,
                                stoch_ranges=self.stoch_ranges,
                                rsi_trigger=self.rsi_trigger,
                                macd_trigger=self.macd_trigger,
                                )
                signal.decide()
            except:
                self.notify(SignalError())
                self.wallet.notify_error(SignalError())
                return SignalError()

            # Notify about indicators
            for line in klines.iterrows():
                curr_values = line[1]
                print(line[0])
            # self.info(self.active_deal, klines)

                self.active_price = curr_values.Close

                # Создание новой ветки сделок
                if curr_values.Buy and self.active_deal is False:
                    self.notify(f'Покупаю по цене ${self.active_price}!')
                    self.wallet.set_quantity(self.active_price, self.decimals)
                    if not self.test_net:
                        buy_order = self.client.create_order(
                            symbol=self.ticker,
                            side=SIDE_BUY,
                            type=ORDER_TYPE_MARKET,
                            quantity=self.wallet.qty,
                        )
                        buy_price = buy_order['fills'][0]['price']
                        self.wallet.qty = buy_order['executedQty']
                        self.wallet.buy(buy_price, self.wallet.qty)
                    # Test net mode
                    if self.test_net:
                        self.wallet.buy(self.active_price, self.wallet.qty)
                    self.active_deal = True
                if curr_values.Sell and self.active_deal:
                    self.notify(f'Продаю по цене ${self.active_price}!')
                    if not self.test_net:
                        sell_order = self.client.create_order(
                            symbol=self.ticker,
                            side=SIDE_SELL,
                            type=ORDER_TYPE_MARKET,
                            quantity=self.wallet.qty,
                        )
                        sell_price = sell_order['fills'][0]['price']
                        self.wallet.sell(sell_price, self.wallet.qty)
                    if self.test_net:
                        self.wallet.sell(self.active_price)
                    self.active_deal = False
                continue
        except KeyboardInterrupt:
            self.wallet.notify_error('Произошло выключение бота!')
            # if self.active_deal is True:
            #     inp = input(f'У вас есть незавершенная сделка в паре {self.ticker},'
            #                 f' хотите ли вы ее автоматически закрыть? (да/нет)\n')
            #     if inp.lower() == 'да' or inp.lower() == 'lf':
            #         if not self.test_net:
            #             sell_order = self.client.create_order(
            #                 symbol=self.ticker,
            #                 side=SIDE_SELL,
            #                 type=ORDER_TYPE_MARKET,
            #                 quantity=self.wallet.qty,
            #             )
            #             sell_price = sell_order['fills'][0]['price']
            #             self.wallet.sell(sell_price)
            #         else:
            #             sell_price = self.active_price
            #             self.wallet.sell(sell_price)
            #         print(f'{self.wallet.qty} {self.ticker[-4]} проданы по цене ${sell_price}')
            #     else:
            #         print(f'Хорошо. Не забудьте про свои {self.wallet.qty} {self.ticker}!')
            # else:
            #     inp = str(input())
            #     print('У вас нет незаверщенных сделок. До свидания!')
            #     print(inp)


# if __name__ == '__main__':
#     bot = StochBot(api_key=settings.apis[0],
#                    api_secret=settings.apis[1],
#                    ticker='COTIUSDT',
#                    cash=settings.cash,
#                    percents=settings.percents,
#                    fee=settings.fee_size,
#                    test_net=settings.test_net,
#                    )
#     bot.work()
