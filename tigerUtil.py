from datetime import datetime
import time
import pandas as pd
from tigeropen.common.consts import (Language,        # 语言
                                Market,           # 市场
                                BarPeriod,        # k线周期
                                QuoteRight)       # 复权类型
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.quote.quote_client import QuoteClient

import tigerUtil

def get_client_config():
    """
    https://quant.itigerup.com/#developer 开发者信息获取
    """
    client_config = TigerOpenClientConfig()
    # 如果是windowns系统，路径字符串前需加 r 防止转义， 如 read_private_key(r'C:\Users\admin\tiger.pem')
    client_config.private_key = read_private_key('D:\\PyCharm\\quantization\\quantization\\tiger.pem')
    client_config.tiger_id = '20151243'  #TBNZ
    client_config.account = 'U100390851'   #20210412165301427
    client_config.language = Language.zh_CN  #可选，不填默认为英语'
    # client_config.timezone = 'US/Eastern' # 可选时区设置
    return client_config

# 调用上方定义的函数生成用户配置ClientConfig对象
client_config = get_client_config()

# 随后传入配置参数对象来初始化QuoteClient
quote_client = QuoteClient(client_config)


def get_quarter_start_date(current_dt):
    # 将字符串转换为日期对象
    dt = datetime.strptime(current_dt, '%Y-%m-%d')

    # 获取当前月份
    month = dt.month

    # 根据月份确定季度
    if 1 <= month <= 3:
        quarter_start_month = 1
    elif 4 <= month <= 6:
        quarter_start_month = 4
    elif 7 <= month <= 9:
        quarter_start_month = 7
    else:  # 10 <= month <= 12
        quarter_start_month = 10

        # 构建季度第一天的日期对象
    quarter_start_date = dt.replace(month=quarter_start_month, day=1)

    # 将日期对象转换为字符串
    quarter_start_str = quarter_start_date.strftime('%Y-%m-%d %H:%M:%S')

    return quarter_start_str


def get_previous_quarter_start_date(current_dt):
    # 将字符串转换为日期对象
    dt = datetime.strptime(current_dt, '%Y-%m-%d')

    # 获取当前月份
    month = dt.month

    # 确定当前季度
    if 1 <= month <= 3:
        current_quarter_start_month = 1
        previous_quarter_start_month = 10  # 上个季度是上一年的第四季度
        previous_year = dt.year - 1
    elif 4 <= month <= 6:
        current_quarter_start_month = 4
        previous_quarter_start_month = 1  # 上个季度是当年的第一季度
        previous_year = dt.year
    elif 7 <= month <= 9:
        current_quarter_start_month = 7
        previous_quarter_start_month = 4  # 上个季度是当年的第二季度
        previous_year = dt.year
    else:  # 10 <= month <= 12
        current_quarter_start_month = 10
        previous_quarter_start_month = 7  # 上个季度是当年的第三季度
        previous_year = dt.year

        # 构建上个季度第一天的日期对象
    previous_quarter_start_date = datetime(previous_year, previous_quarter_start_month, 1)

    # 将日期对象转换为字符串
    previous_quarter_start_str = previous_quarter_start_date.strftime('%Y-%m-%d %H:%M:%S')

    return previous_quarter_start_str


from datetime import datetime


def get_two_previous_quarters_start_date(current_dt):
    # 将字符串转换为日期对象
    dt = datetime.strptime(current_dt, '%Y-%m-%d')

    # 获取当前季度
    quarter = (dt.month - 1) // 3 + 1

    # 计算上上一个季度的编号
    previous_previous_quarter = quarter - 2
    if previous_previous_quarter < 1:
        previous_previous_quarter += 4  # 如果小于1，则加上4回到上一年的相应季度
        year = dt.year - 1
    else:
        year = dt.year

        # 根据季度编号确定月份
    if previous_previous_quarter == 1:
        start_month = 1
    elif previous_previous_quarter == 2:
        start_month = 4
    elif previous_previous_quarter == 3:
        start_month = 7
    elif previous_previous_quarter == 4:
        start_month = 10

        # 构建上上一个季度第一天的日期对象
    previous_previous_quarter_start_date = datetime(year, start_month, 1)

    # 将日期对象转换为字符串
    previous_previous_quarter_start_str = previous_previous_quarter_start_date.strftime('%Y-%m-%d %H:%M:%S')

    return previous_previous_quarter_start_str


def getMaxChg(symbbols,begin_time,end_time):
    stock_max_chg_dict ={}
    bars = quote_client.get_bars(symbbols, period=BarPeriod.DAY,
                             begin_time=begin_time,
                             end_time=end_time)
    bars['us_date'] = pd.to_datetime(bars['time'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    previous_row = None
    chg = 0
    for index, row in bars.iterrows():
        if previous_row is not None:
            chg = abs(((previous_row['close'] - row['close']) / previous_row['close']))
            dt = row['us_date'].strftime('%Y-%m-%d')
            if stock_max_chg_dict.get(row['symbol']) is not None:
                if(chg > stock_max_chg_dict[row['symbol']][1]):
                    stock_max_chg_dict[row['symbol']] = [dt,chg]
            else:
                stock_max_chg_dict[row['symbol']] = ['None', 0]
        previous_row = row
    return stock_max_chg_dict

def get_stock_last_info(stock_code_all_list):
    stock_last_info_dict = {}
    stock_last_df = quote_client.get_stock_briefs(stock_code_all_list, include_hour_trading=False, lang=None)
    for index, stockdf in stock_last_df.iterrows():
        stock_last_info_dict[stockdf['symbol']]=stockdf['latest_price']
    return stock_last_info_dict

def getRecentlyOption(stock,date,stock_current_price,put_call,num):
    option_chain = tigerUtil.quote_client.get_option_chain(stock,date)
    option_chain['strike'] = pd.to_numeric(option_chain['strike'], errors='coerce')
    if(put_call == 'call'):
        option_chain = option_chain[(option_chain['put_call'] == "CALL") & (option_chain['strike'] > stock_current_price)].head(num)
    elif(put_call == 'put'):
        option_chain = option_chain[(option_chain['put_call'] == "CALL") & (option_chain['strike'] < stock_current_price)].tail(num)
    return option_chain

def filterNoOption(stock_code_all_list):
    option_df = tigerUtil.quote_client.get_option_expirations(stock_code_all_list)['symbol'].drop_duplicates()
    restult_list = option_df.tolist()
    missing_stock_codes = [code for code in stock_code_all_list if code not in restult_list]
    print("没有期权的股票："+str(missing_stock_codes))
    return restult_list

def writeExcel(df,path):
    # 创建一个 XlsxWriter 工作簿对象（通过 Pandas 的 ExcelWriter），并指定引擎为 xlsxwriter
    xlsxwriter = pd.ExcelWriter(path, engine='xlsxwriter')

    # 将 DataFrame 写入工作表，不包括索引列
    df.to_excel(xlsxwriter, sheet_name='Sheet1', index=False)

    # 获取工作表对象
    worksheet = xlsxwriter.sheets['Sheet1']

    # 设置标题行的格式（绿色填充、字体等）
    header_format = xlsxwriter.book.add_format({
        'bg_color': '#C6EFCE',  # 绿色填充
        'font_name': '华文楷体',
        'font_size': 12,
        'bold': True  # 粗体
    })

    # 为工作表中的标题行设置格式
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    worksheet.set_column('M:Q', 25)
    worksheet.set_column('A:L', 13)

    # 保存并关闭 Excel 文件
    xlsxwriter.close()
