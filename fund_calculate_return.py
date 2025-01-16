import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
import os 
import argparse

# 定投日期列表计算
def fetch_invest_dates(start_date, end_date, freq, day_offset):
    if freq == 'M':
        invest_dates = pd.date_range(start_date, end_date, freq='MS') + pd.DateOffset(days=day_offset - 1)
        freq_desc = f"每月第{day_offset}日"
    if freq == 'Q':
        invest_dates = pd.date_range(start_date, end_date, freq='QS') + pd.DateOffset(days=day_offset - 1)
        freq_desc = f"每季度第{day_offset}日"
    if freq == 'Y':
        invest_dates = pd.date_range(start_date, end_date, freq='YS') + pd.DateOffset(days=day_offset - 1)
        freq_desc = f"每年第{day_offset}日"
    if freq == 'W':
        invest_dates = pd.date_range(start_date, end_date, freq='W-MON') + pd.DateOffset(days=day_offset -1)
        freq_desc = f"每周第{day_offset}日"

    return invest_dates.strftime('%Y-%m-%d').to_list(), freq_desc


# 下载基金历史净值数据
def fetch_fund_net_value(fund_code):
    page_index = 1
    page_size = 20
    all_data = []
    total_count = None
    try:
        with tqdm(desc="Fetching data", unit="page") as pbar:
            while True:
                url = f"https://api.fund.eastmoney.com/f10/lsjz?fundCode={fund_code}&pageIndex={page_index}&pageSize={page_size}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/515.15.4 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
                    "Referer": "https://fundf10.eastmoney.com/",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "X-Requested-With": "XMLHttpRequest"
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # 检查请求是否成功，如果不成功将抛出 HTTPError
                data = response.json()
                if "Data" in data and "LSJZList" in data["Data"]:
                    page_data = data["Data"]["LSJZList"]
                    if not page_data:
                        break
                    if total_count is None:
                        total_count = data.get("TotalCount", len(all_data))
                    all_data.extend(page_data)
                    page_index += 1
                    pbar.update(1)
                    pbar.total = (total_count + page_size - 1) // page_size
                else:
                    break
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None
    df = pd.DataFrame(all_data)
    return df

# 保存数据到Excel
def save_to_excel(df, filename):
    if df is not None:
        try:
            df.to_excel(filename, index=False)
            print(f"数据已成功保存到 {filename}")
        except Exception as e:
            print(f"保存 Excel 文件时出错: {e}")
    else:
        print("没有数据可保存")

# 模拟基金定投
def simulate_dollar_cost_averaging(df, amount, invest_dates,end_date):
    """
    模拟定投操作
    :param df: 包含净值数据的 DataFrame
    :param amount: 每次定投的金额
    :param invest_dates: 定投日期列表，格式为 ['YYYY-MM-DD']
    :return: 最终资产总值，总投入金额
    """
    total_investment = 0
    total_shares = 0
    for date in invest_dates:
        # 找到最近的净值数据
        net_value = df[df["FSRQ"] >= date]["DWJZ"].iloc[-1]
        shares = amount / net_value
        total_shares += shares
        total_investment += amount
    final_net_value = df[df["FSRQ"] == end_date]["DWJZ"].iloc[0]
    final_asset_value = total_shares * final_net_value
    return final_asset_value, total_investment, total_shares, final_net_value

# 计算定投收益率
def calculate_return(final_asset_value, total_investment):
    """
    计算收益率
    :param final_asset_value: 最终资产总值
    :param total_investment: 总投入金额
    :return: 收益率
    """
    return (final_asset_value - total_investment) / total_investment * 100


if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="基金定投回测脚本")
    parser.add_argument("fund_code", type=str, help="基金代码,必填")
    parser.add_argument('--start_date', type=str, default='2023-01-01', help='开始日期，非必填')
    parser.add_argument('--end_date', type=str, default='2024-12-31', help='结束日期，非必填')
    parser.add_argument('--amount', type=int, default=1000, help='每次定投金额，非必填')
    parser.add_argument('--freq', type=str, default='M', help='定投频率，非必填')
    parser.add_argument('--day_offset', type=int, default=1, help='频率偏移，非必填')
    args = parser.parse_args()

    # 修改定投参数
    fund_code = args.fund_code # 基金代码
    start_date = args.start_date # 开始日期
    end_date = args.end_date # 结束日期
    freq = args.freq # 定投频率
    amount = args.amount  # 每次定投金额
    day_offset = args.day_offset # 定投频率偏移

    file_path=f"/Users/xxx/Downloads/fund/fund_net_values_{fund_code}.xlsx" # 文件保存路径

    invest_dates, freq_desc = fetch_invest_dates(start_date, end_date, freq, day_offset)  # 定投日期列表
    # 判断文件是否存在，不再重复下载
    if not os.path.exists(file_path):
        df_download = fetch_fund_net_value(fund_code) # 下载数据
        save_to_excel(df_download, file_path) # 保存数据
    else:
        print("文件已经存在，不再重复下载。")

    df = pd.read_excel(file_path) # 读取文件
    final_asset_value, total_investment, total_shares, final_net_value = simulate_dollar_cost_averaging(df, amount, invest_dates, end_date) # 模拟定投
    return_rate = calculate_return(final_asset_value, total_investment) # 计算定投总收益率
    # 返回计算结果
    print(f"基金{fund_code}在{start_date}至{end_date}期间{freq_desc}定投{amount}元回测结果如下:")
    print("########################################")
    print(f"定投总投入  : {total_investment}元")
    print(f"期末基金份额: {total_shares:.4f}份")
    print(f"期末基金净值: {final_net_value}")
    print(f"期末资产总值: {final_asset_value:.4f}元")
    print(f"定投总收益率: {return_rate:.2f}%")
    print("########################################")
