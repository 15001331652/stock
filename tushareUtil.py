import tushare as ts
import pandas as pd
from datetime import datetime
ts.set_token('c5aa0ed8611ad55d237a3ab4ab5e3f52f7964a85d92989465015c5fa')
pro = ts.pro_api()
def get_quarter_start_date(current_dt):
    # 将字符串转换为日期对象
    dt = datetime.strptime(current_dt, '%Y%m%d')

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
    quarter_start_str = quarter_start_date.strftime('%Y%m%d')

    return quarter_start_str


def get_previous_quarter_start_date(current_dt):
    # 将字符串转换为日期对象
    dt = datetime.strptime(current_dt, '%Y%m%d')

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
    previous_quarter_start_str = previous_quarter_start_date.strftime('%Y%m%d')

    return previous_quarter_start_str

def get_two_previous_quarters_start_date(current_dt):
    # 将字符串转换为日期对象
    dt = datetime.strptime(current_dt, '%Y%m%d')

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
    previous_previous_quarter_start_str = previous_previous_quarter_start_date.strftime('%Y%m%d')

    return previous_previous_quarter_start_str

def getMaxChgBatch(stock_list,start_date,end_date):
    stock_max_chg_dict = {}
    chg = 0
    for value in stock_list:
        stock_info = pro.us_daily(ts_code=value, start_date=start_date, end_date=end_date)
        for index, row in stock_info.iterrows():
            chg = abs(row['pct_change'])
            if stock_max_chg_dict.get(row['ts_code']) is not None:
                if (chg > stock_max_chg_dict[row['ts_code']][1]):
                    stock_max_chg_dict[row['ts_code']] = [row['trade_date'], chg]
            else:
                stock_max_chg_dict[row['ts_code']] =  [row['trade_date'], chg]
    return stock_max_chg_dict

def getMaxChgSingle(stock,start_date,end_date):
    max_chg = 0
    max_date = None
    stock_info = pro.us_daily(ts_code=stock, start_date=start_date, end_date=end_date)
    for index, row in stock_info.iterrows():
        current_chg = abs(row['pct_change'])
        if (current_chg > max_chg):
            max_chg = current_chg
            max_date = row['trade_date']
    return [datetime.strptime(max_date, "%Y%m%d").strftime("%Y-%m-%d"),max_chg]

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

        # 调整列宽（这里使用自动调整列宽的方法，但也可以手动设置具体的宽度）
    for col_num, col_name in enumerate(df.columns):
        # 自动调整列宽（根据内容调整）
        # 注意：自动调整可能不会总是给出完美的结果，特别是当内容包含很长的字符串或数字时
        max_length = 100000000000
        # 计算列中每个单元格内容的长度（这里只考虑了字符串长度，对于数字可能需要额外处理）
        for cell in df[col_name]:
            try:
                # 尝试将单元格内容转换为字符串并计算长度
                cell_length = len(str(cell))
                if cell_length > max_length:
                    max_length = cell_length
            except:
                # 如果转换失败（比如非字符串类型的数据），则忽略该单元格
                pass
                # 为列设置一个稍微大于最大内容长度的宽度（这里加了10作为额外的间距）
        # 注意：这个计算方式可能需要根据实际情况进行调整
        # xlsxwriter 的列宽单位是字符宽度的1/256，所以这里乘以256得到的是以字符为单位的宽度
        worksheet.set_column(col_num, col_num, max_length * 256 + 10 * 256)

        # 另一种更简单但可能不太精确的方法是使用 autosize
    # worksheet.autosize_columns()
    # 注意：autosize_columns() 方法会根据内容自动调整所有列的宽度，但可能不如手动调整精确

    # 保存并关闭 Excel 文件
    xlsxwriter.close()
