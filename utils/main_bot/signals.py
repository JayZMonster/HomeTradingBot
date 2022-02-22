from pandas import DataFrame
from numpy import where


class Signal:

    def __init__(self,
                 data: DataFrame,
                 lags: int,
                 stoch_ranges: tuple = (20, 80),
                 rsi_trigger: int = 50,
                 macd_trigger: int = 0,
                 ):
        self.data = data
        self.lags = lags
        self.stoch_ranges = stoch_ranges
        self.rsi_trigger = rsi_trigger
        self.macd_trigger = macd_trigger

    def get_trigger(self, buy=True):
        data_mask = DataFrame()

        for i in range(int(self.lags) + 1):
            if buy:
                mask = (self.data['%K'].shift(i) < self.stoch_ranges[0]) \
                       & (self.data['%D'].shift(i) < self.stoch_ranges[0])
            else:
                mask = (self.data['%K'].shift(i) > self.stoch_ranges[1]) \
                       & (self.data['%D'].shift(i) > self.stoch_ranges[1])
            data_mask = data_mask.append(mask, ignore_index=True)

        return data_mask.sum(axis=0)

    def decide(self):
        self.data['Buy_trigger'] = where(self.get_trigger(), 1, 0)
        self.data['Sell_trigger'] = where(self.get_trigger(False), 1, 0)

        self.data['Buy'] = where(
            self.data.Buy_trigger
            & (self.data['%K'].between(self.stoch_ranges[0], self.stoch_ranges[1]))
            & (self.data['%D'].between(self.stoch_ranges[0], self.stoch_ranges[1]))
            & (self.data.rsi > self.rsi_trigger) & (self.data.macd > self.macd_trigger), 1, 0
        )
        self.data['Sell'] = where(
            self.data.Sell_trigger
            & (self.data['%K'].between(self.stoch_ranges[0], self.stoch_ranges[1]))
            & (self.data['%D'].between(self.stoch_ranges[0], self.stoch_ranges[1]))
            & (self.data.rsi < self.rsi_trigger) & (self.data.macd < self.macd_trigger), 1, 0
        )

        # --- BACKTEST ---
        # long_buy_dates, long_sell_dates = [], []
        #
        # for i in range(len(self.data) - 1):
        #     if self.data.Long.iloc[i]:
        #         long_buy_dates.append(self.data.iloc[i+1].name)
        #         for num, j in enumerate(self.data.Short[i:]):
        #             if j:
        #                 long_sell_dates.append(self.data.iloc[num+1+i].name)
        #                 break
        #
        # cut_long = len(long_buy_dates) - len(long_sell_dates)
        # if cut_long:
        #     long_buy_dates = long_buy_dates[:-cut_long]
        # long_frame = pd.DataFrame({'Buy': long_buy_dates, 'Sell': long_sell_dates, 'Type': ['Long']*len(long_buy_dates)})
        #
        # actuals = long_frame[long_frame.Buy > long_frame.Sell.shift(1)]
        # print(actuals)
        # buy_prices_long = self.data.loc[actuals[actuals['Type'] == 'Long'].Buy].Open
        #
        # sell_prices_long = self.data.loc[actuals[actuals['Type'] == 'Long'].Sell].Open
        #
        # long_profit = (sell_prices_long.values - buy_prices_long.values)/buy_prices_long.values
        #
        # print(long_profit)
        # print('Profit long: ', (long_profit+1).prod())
