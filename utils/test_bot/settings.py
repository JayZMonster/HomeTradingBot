#
lookback = '8500'  # Размер запрашеваемого набора данных (не меньше 201)
stoch_ranges = (20, 80)  # настройки стратегии не трогать
rsi_trigger = 50  # настройки стратегии не трогать
macd_trigger = 0  # настройки стратегии не трогать
window = 14  # настройки стратегии не трогать
smooth_window = 3  # настройки стратегии не трогать
lags = 5  # настройки стратегии не трогать
interval = '1h'  # настройки стратегии не трогать
_time = 'hours'
fee_size = 0.00075  # комиссия биржи
cash = 100  # кол-во денег на счету, соотношение cash / num_clerks должно быть больше 15
num_clerks = 1  # кол-во трейдинговых пар
percents = 1  # объем одной сделки от общего банка (от 0 до 1, например 0.2)
test_net = 'yes'  # режим тестовой торговли - yes, реальный режим - no
#
'52% '
tickers_list = [
        'XLMUSDT',
        'BNBBTC',
        'COTIBTC',
        'XMRBTC',
        'LINKBTC',
        'IOTABTC',
        'FTMBTC',
        'XRPBTC',
]

# 1 - api_key 2 - api_secret 3 - TG bot 4 - TG chat id
apis = ['omCVqDzk4hbmz33iTe19WhyI1lE1hy4wCBuCqqI1jShakOMqOYVQjOYBCl9rYEea',
        'ocuXZMhLM4iiTg4DPLuQKHVXiDTHC9GonTWr2OsgzcexHYAd9CmP85cX2hxGkNWG',
        '5267388557:AAEzz1Bi_vjwUxJXO8Icp5cDLszTGPkx52s',
        517321921,
        ]


