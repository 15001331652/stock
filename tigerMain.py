import tigerUtil
import pandas as pd
#获取tigeropen客户端
quote_client = tigerUtil.quote_client
#获取所有股票，需要控访问频次
#batch_size = 10
#symbol_names = quote_client.get_symbol_names(market=Market.US)
#stock_code_all_list = [sublist[0] for sublist in symbol_names]
#stock_code_batch_list = [stock_code_all_list[i:i + batch_size] for i in range(0, len(stock_code_all_list), batch_size)]
#获取固定股票的信息
#指定日期
curret_dt = '2024-11-11'
#获取当前季度的第一天
quarter_start_date = tigerUtil.get_quarter_start_date(curret_dt)
#获取上一个季度的第一天
previous_quarter_start_date = tigerUtil.get_previous_quarter_start_date(curret_dt)
#获取上两个季度的第一天
two_previous_quarters_start_date = tigerUtil.get_two_previous_quarters_start_date(curret_dt)
#指定需要获取的股票列表
#stock_code_all_list = ["AFRM","ANET","DUK","AVIR","ATEN","FNKO","VTGN","PHAT","SONY","IX","TU","NGR","BAX","RBA","PARAA","CNH","LAMR","WMS"]
#stock_code_all_list = ["CSCO","HNHPF","NU","NTES","DIS","SIEGY","MUFG","SMFG","BN"]
stock_code_all_list = ["AMAT","BABA","PGR","NABY","SPB","AOZOY"]
#过滤没有期权的股票
stock_code_all_list = tigerUtil.filterNoOption(stock_code_all_list)
#获取股票最新价格
stock_last_price_dict = tigerUtil.get_stock_last_info(stock_code_all_list)
#获取上季度的最大涨跌幅度
previous_quarter_max_chg_dict = tigerUtil.getMaxChg(stock_code_all_list,previous_quarter_start_date,quarter_start_date)
#获取上两个季度的最大涨跌幅度
two_previous_quarter_max_chg_dict = tigerUtil.getMaxChg(stock_code_all_list,two_previous_quarters_start_date,previous_quarter_start_date)
#获取股票最大涨跌幅
quarter_max_chg_dict = tigerUtil.getMaxChg(stock_code_all_list,two_previous_quarters_start_date,quarter_start_date)
#写入Xlxs的wheet
write_list = []
result_columns = ['股票代码','当前日期', '股票价格', '期权日期','期权目标价','权力金','单边本金','涨幅','单边盈利倍数','剩余资金','双边盈利倍数','最大涨跌幅','最大涨跌幅日期','上个季度最大涨跌幅','上个季度最大涨跌幅日期','上两个季度最大涨跌幅','上两个季度最大涨跌幅日期']
#主逻辑
for stock in stock_code_all_list:
    print("-----------"+stock+"数据生成中-----------")
    #获取股票当前价格
    stock_current_price = stock_last_price_dict[stock]
    #最大涨跌幅
    stock_max_date = quarter_max_chg_dict[stock][0]
    stock_max_chg = quarter_max_chg_dict[stock][1]
    #上一个季度涨跌幅
    previous_quarter_stock_max_date = previous_quarter_max_chg_dict[stock][0]
    previous_quarter_stock_max_chg = previous_quarter_max_chg_dict[stock][1]
    #上两个季度最大涨跌幅
    two_previous_quarter_stock_max_date = two_previous_quarter_max_chg_dict[stock][0]
    two_previous_quarter_stock_max_chg = two_previous_quarter_max_chg_dict[stock][1]
    #获取全部的期权日期
    option_date = tigerUtil.quote_client.get_option_expirations([stock])
    #获取里当前日期最近的到期日
    recently_option_date = option_date.head(1).iloc[0]['date']
    #获取到期日期权中离当前价格最近的期权
    recently_options = tigerUtil.getRecentlyOption(stock,recently_option_date,stock_current_price,'call',3)
    for index, option in recently_options.iterrows():
        #权利金
        powerGold = option['latest_price']
        #期权目标价
        optionPrice = option['strike']
        #本金
        principal = 20000
        #单边本金
        unilateral_principal = principal/2
        #从0.01涨幅开始计算相关收益
        chg_array = [x * 0.01 for x in range(1, 101)]
        for chg in chg_array:
            # 单边盈利率
            unilateral_profit_chg = (stock_current_price + stock_current_price * chg - optionPrice) / powerGold
            # 剩余资金
            remaining_funds = unilateral_principal * unilateral_profit_chg
            # 双边盈利率
            bilateral_profit_chg = remaining_funds / principal
            #涨chg后大于期权期权目标价
            #双边盈利
            if(stock_current_price+stock_current_price*chg > optionPrice and chg <= stock_max_chg and bilateral_profit_chg>0.8):
            #if(stock_current_price+stock_current_price*chg > optionPrice and chg <= stock_max_chg):
                write_list.append([stock, #股票名称
                                   curret_dt,#当前日期
                                   "%.3f"%stock_current_price,#股票价格
                                   recently_option_date,#期权日期
                                   "%.3f"%optionPrice,#期权目标价
                                   "%.3f" % powerGold,#权力金
                                   "%.0f" % unilateral_principal,#单边本金
                                   ("%.3f"%(chg*100))+'%',#涨幅
                                   "%.3f" % unilateral_profit_chg,#单边盈利倍数
                                   "%.3f" % remaining_funds,#剩余资金
                                   "%.3f" % bilateral_profit_chg,#双边盈利倍数
                                   ("%.3f" % (stock_max_chg*100))+'%',  # 最大涨跌幅
                                   stock_max_date,  # 最大日期涨跌幅
                                   ("%.2f" % (previous_quarter_stock_max_chg*100))+'%',#上个季度最大涨跌幅
                                   previous_quarter_stock_max_date, #上个季度最大涨跌幅日期
                                   ("%.2f" % (two_previous_quarter_stock_max_chg*100))+'%',  # 上两个季度最大涨跌幅
                                   two_previous_quarter_stock_max_date  # 上两个季度最大涨跌幅日期
                                   ])
#生成结果
resutl_df = pd.DataFrame(write_list, columns=result_columns)
#写入到excel中
tigerUtil.writeExcel(resutl_df,'C:\\Users\\renzengtao\\Desktop\\股票\\output.xlsx')


