from multiprocessing import Process
from utils.main_bot.stoch_bot import StochBot


class BotManager:

    def __init__(self,
                 number_of_clerks: int,
                 tickers: list,
                 cash: float,
                 fee: float,
                 api_key: str,
                 api_secret: str,
                 test_net: str,
                 interval: str,
                 percents: float,
                 ):
        self.clerks = {}
        self.clerks_num = number_of_clerks
        self.tickers = tickers
        self.cash = float(cash) / float(self.clerks_num)
        self.fee = fee
        self.api_key = api_key
        self.api_secret = api_secret
        self.test_net = test_net
        self.interval = interval
        self.percents = percents

    def create_clerks(self):

        for i, ticker in zip(range(self.clerks_num), self.tickers):
            print(f'Bot {i}')
            bot = StochBot(
                api_secret=self.api_secret,
                api_key=self.api_key,
                ticker=ticker,
                cash=self.cash,
                fee=self.fee,
                test_net=self.test_net,
                percents=self.percents,
            )
            clerk = Process(target=bot.work)
            clerk.start()
            print(f'Process started')
            self.clerks[ticker] = [clerk, bot]
        for ck in self.tickers:
            self.clerks[ck][0].join()

    # def check_clerks(self):
    #     for ticker in self.tickers:
    #         reports = self.clerks[ticker][0].get()  # TODO Create queues for reports in each bot
    #         self.clerks[ticker][1].parse_reports(reports)  # TODO Make wallets able to write results

    def main(self):
        self.create_clerks()
