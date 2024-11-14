import time
import pandas as pd
from tigeropen.common.consts import (Language,        # 语言
                                Market,           # 市场
                                BarPeriod,        # k线周期
                                QuoteRight)       # 复权类型
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.quote.domain.filter import OptionFilter

import tigerUtil

#current_dt = '2024-11-13'
#symbbols = ['AAPL','BIDU']
#quarter_start_date = Util.get_quarter_start_date(current_dt)
#previous_quarter_start_date = Util.get_previous_quarter_start_date(current_dt)  # 输出: 2024-07-01
#two_previous_quarters_start_date = Util.get_two_previous_quarters_start_date(current_dt)  # 输出: 2024-04-01

#stock_max_chg_dict = Util.getQuarterMaxChg(symbbols,previous_quarter_start_date,quarter_start_date)
#print(stock_max_chg_dict)


bars = tigerUtil.quote_client.get_bars("AAPL", period=BarPeriod.DAY,
                             begin_time="2024-11-13 00:00:00",
                             end_time="2024-11-13 00:00:00")



stock_price = tigerUtil.quote_client.get_stock_briefs(["AAPL"])

# 查询行情函数会返回一个包含当前行情快照的pandas.DataFrame对象，见返回示例。具体字段含义参见get_stock_briefs方法说明
#print(bars)

#expiration = Util.quote_client.get_option_expirations(symbols=['AAPL'])
#print(expiration)
#option_filter = OptionFilter(implied_volatility_min=0.5, implied_volatility_max=0.9, delta_min=0, delta_max=1,
#                         open_interest_min=100, gamma_min=0.005, theta_max=-0.05, in_the_money=True)
#option_filter = OptionFilter()
#option_chain = Util.quote_client.get_option_chain('AAPL', '2024-11-08', option_filter=option_filter)
#print(option_chain)