import re
import os
import time
import requests
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime
from bs4 import BeautifulSoup

# 请求用户输入Google Scholar主页的网址
journal = 'source:Public+source:Administration+source:Review'
# url_base = 'https://scholar.google.com/scholar?q='+journal+'&hl=zh-CN&as_sdt=0,5&as_ylo=2023&as_yhi=2024'
url_base = 'https://scholar.google.com/scholar?start=0&q=source:public+source:administration+source:review&hl=zh-CN&as_sdt=0,5&as_ylo=2023&as_yhi=2024'
# url_base = 'https://scholar.google.com/citations?user=_qPX-hcAAAAJ&hl=zh-CN&oi=ao'
# 定义HTTP请求头，模拟正常浏览器访问，以避免被网站阻止
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
# HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
# }

proxies = {
    'http': 'http://127.0.0.1:33210',
    'https': 'http://127.0.0.1:33210',
}

def get_soup(url):
    """
    发送HTTP请求到指定URL并获取BeautifulSoup对象。

    参数:
    - url: 要请求的网页的URL字符串。

    返回:
    - BeautifulSoup对象，用于进一步解析网页内容。

    异常:
    - HTTPError: 如果响应的状态码不是200，即请求失败。
    """
    while True:
        waiting_time = 120
        retries = 5
        for i in range(retries):
            try:
                # 定义请求头，模拟浏览器行为
                response = requests.get(url, headers=HEADERS)
                # 检查请求是否成功，如果状态码不是200，则抛出异常
                response.raise_for_status()
                # 使用BeautifulSoup解析响应内容，并返回BeautifulSoup对象
                return BeautifulSoup(response.text, 'html.parser')
            except:
                print(f"连接失败，正在重试... {i + 1}/{retries}")
                time.sleep(2)
        time.sleep(waiting_time)
        if waiting_time < 1800:
            waiting_time += 30
            print('waiting time:{}'.format(waiting_time))

# 主逻辑
def main():
    """
    主函数，从Google Scholar网站抓取指定数量的论文信息，并保存到Excel文件中。
    """
    # 一些参数
    max_numbers = 5000
    
    # 定义列名
    columns = ['年份', '期刊', '题目', '作者', '一作','中文/英文']

    # 初始化DataFrame，用于存储论文信息
    papers_df = pd.DataFrame(columns=columns)

    # Loop settings
    filename = os.path.join('lib', journal+'.csv')
    if os.path.exists(filename):
        print('Continue crawlering...')
        df = pd.read_csv(filename)

        # 获取字典的数量
        cstart = len(df)
    else:
        print('New Task...')
        cstart = 0      # Starting index of papers
    pagesize = 10  # Number of papers per page

    # 初始化一个空列表来存储每行的数据
    data_rows = []

    # 每次爬取100篇，直到爬取所有文章
    while cstart < max_numbers:
        print('already get {} papers...'.format(cstart))
        url = f'{url_base}&cstart={cstart}&pagesize={pagesize}'

        # 使用get_soup函数获取Google Scholar网页的BeautifulSoup对象
        soup = get_soup(url)

        # 找到所有表示论文的行
        rows = soup.find_all('div', class_='gs_ri')
        
        try:
            batch = []
            for row in rows:
                # 提取论文标题
                title = row.find('h3', class_='gs_rt').text
                # 提取作者信息
                authors = row.find('div', class_='gs_a').text
                # 提取第一作者
                first_author = authors.split(',')[0] if authors else 'N/A'
                # 提取发表年份和期刊信息
                journal_info = row.find('b').text
                year = re.findall(r'\d+', authors)
                journal_name = re.sub(r'[^a-zA-Z\u4e00-\u9fa5\s]', '', journal_info)

                # 判断中文还是英文
                if ',' in authors:
                    Chinese_English = '英'
                elif '，' in authors:
                    Chinese_English = '中'
                else:
                    Chinese_English = ''

                # 输出提示
                # print(f"题目：{title}\n作者：{authors}\n一作：{first_author}\n年份：{year}\n期刊：{journal_name}\n中英文：{Chinese_English}\n")
                        
                # 构造论文信息字典
                data = {
                    '年份': year,
                    '期刊': journal_name,
                    '题目': title,
                    '一作': first_author,
                    '中文/英文': Chinese_English
                }
                # 将论文信息添加到列表中
                batch.append(data)

            # 将当前批次的数据转换为 DataFrame
            df = pd.DataFrame(batch)

            if os.path.exists(filename):
                # 如果是第一段数据，写入标题
                df.to_csv(filename, index=False, mode='w', header=True)
            else:
                # 之后的段落追加数据
                df.to_csv(filename, index=False, mode='a', header=False)
            cstart += pagesize

        except:
            # 所有文献检索完成
            print(cstart)
            break

    # 输出提示
    print('文件已经生成')

if __name__ == "__main__":
    main()
