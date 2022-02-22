import pandas as pd
import ta.trend
from binance import Client
import ta.momentum as moment

from utils.test_bot.settings import interval, lookback, _time


def get_minute_data(client: Client, symbol):
    """
    Getting historical data from binance
    :param client:
    :param symbol:
    :return: DataFrame
    """
    frame = pd.DataFrame(client.get_historical_klines(
        symbol,
        interval,
        lookback + f' {_time} ago UTC'
    ))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def apply_tech_indicators(df, window, smooth_window):
    """
    Applying technical indicators: stoch, rsi, macd
    :param smooth_window:
    :param window:
    :param df:
    :return:
    """
    df['%K'] = moment.stoch(df.High, df.Low, df.Close, window=window, smooth_window=smooth_window)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = moment.rsi(df.Close, window=window)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df.dropna(inplace=True)


# def main():
#     client = Client(api_key='omCVqDzk4hbmz33iTe19WhyI1lE1hy4wCBuCqqI1jShakOMqOYVQjOYBCl9rYEea',
#                                       api_secret='ocuXZMhLM4iiTg4DPLuQKHVXiDTHC9GonTWr2OsgzcexHYAd9CmP85cX2hxGkNWG', )
#     data = get_minute_data(client, 'BTCUSDT', '30m', '100')
#
#     apply_tech_indicators(data)
#     print(data.tail(30))
#
# if __name__ == '__main__':
#     main()
