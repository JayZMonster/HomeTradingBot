from time import sleep

from utils.general import BotManager
from utils.main_bot.settings import *


if __name__ == '__main__':
    BM = BotManager(
        number_of_clerks=num_clerks,
        tickers=tickers_list[:num_clerks],
        cash=float(cash),
        fee=fee_size,
        api_key=apis[0],
        api_secret=apis[1],
        test_net=test_net,
        interval=interval,
        percents=percents,
    )
    try:
        BM.main()
    except KeyboardInterrupt:
        print('Выключение через 5 секунд!')
        sleep(5)

