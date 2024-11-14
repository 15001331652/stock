#df = pro.us_basic()['ts_code'].dropna()
from tigeropen.quote.domain.filter import OptionFilter
import pandas as pd
import tigerUtil
import tushareUtil
from datetime import datetime
curret_dt = '20241101'
stock_list = ['NXPI','ITUB','FANG','O','AIG','TM','RACE','APO','TRI','EMR','RDY','MPC','CPNG','MPLX','CMI']
quarter_start_date = tushareUtil.get_quarter_start_date(curret_dt)
two_previous_quarters_start_date = tushareUtil.get_two_previous_quarters_start_date(curret_dt)
result_columns = ['股票代码','上两个季度最大日期','上两个季度最大涨跌幅','当前日期', '股票价格', '期权日期','期权目标价','权力金','单边本金','涨幅','单边盈利率','剩余资金','双边盈利率']
restul_list = []
for stock in stock_list:
    print(stock)
    stock_current_price = tushareUtil.pro.us_daily(ts_code=stock, start_date=curret_dt, end_date=curret_dt).iloc[0]['close']
    stock_max_chg_list = tushareUtil.getMaxChgSingle(stock, two_previous_quarters_start_date, quarter_start_date)
    stock_max_chg = stock_max_chg_list[1]
    stock_max_date =  stock_max_chg_list[0]
    recently_option = tigerUtil.quote_client.get_option_expirations([stock])
    if recently_option.shape[0] == 0:
        continue
    recently_option_date = recently_option.head(1).iloc[0]['date']
    recently_options = tigerUtil.getRecentlyOption(stock,recently_option_date,stock_current_price,'call',3)
    for index, option in recently_options.iterrows():
        powerGold = option['latest_price']
        optionPrice = option['strike']
        principal = 20000
        unilateral_principal = principal/2
        chg_array = [x * 0.01 for x in range(1, 101)]
        for chg in chg_array:
            # 单边盈利率
            unilateral_profit_chg = (stock_current_price + stock_current_price * chg - optionPrice) / powerGold
            # 剩余资金
            remaining_funds = unilateral_principal * unilateral_profit_chg
            # 双边盈利率
            bilateral_profit_chg = remaining_funds / principal
            #if(stock_current_price+stock_current_price*chg > optionPrice and chg <= stock_max_chg/100 and bilateral_profit_chg>1):
            if(stock_current_price+stock_current_price*chg > optionPrice and chg <= stock_max_chg/100 ):
                restul_list.append([stock,stock_max_date,"%.2f"%(stock_max_chg/100),datetime.strptime(curret_dt, "%Y%m%d").strftime("%Y-%m-%d"),"%.2f"%stock_current_price,recently_option_date,"%.2f"%optionPrice,"%.2f" % powerGold,"%.0f" % unilateral_principal,"%.2f"%chg,"%.2f" % unilateral_profit_chg,"%.2f" % remaining_funds,"%.2f" % bilateral_profit_chg])
resutl_df = pd.DataFrame(restul_list, columns=result_columns)
#resutl_df.to_csv('C:\\Users\\renzengtao\\Desktop\\output.csv', index=False)
tushareUtil.writeExcel(resutl_df,'C:\\Users\\renzengtao\\Desktop\\output.xlsx')
