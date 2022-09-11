#%%
import requests
import time
import random
from bs4 import BeautifulSoup
import pandas as pd

def getCodeList():
    """ 抓出現在股票的Code清單
    
    目前僅支援上市股票的編號

    Returns:
        List : 
        [...
            '8442', '8443', '8454', '8462', '8463',
            '8464', '8466', '8467', '8473', '8478', '8480',
            '8481', '8482', '8488', '8499', '8926', '8940',...
        ]
    """
    # 證券一覽表
    public_code_url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    ans = requests.get(public_code_url)

    # 分類
    bs_ans = BeautifulSoup(ans.text, "html.parser")
    code_list = bs_ans.find_all("td")

    # stock_data_list紀錄全部資料，目前暫時未使用
    stock_data_list = []
    index_list = []

    # 找出撈出資料中，Table的欄位總共有幾個，用來作為後續擷取的每一欄位基礎單位
    for data_str in code_list[0:20]:
        if "股票" in data_str.text:
            break
        index_list.append(data_str.text.replace(" ", ""))
    
    # 計算Table offset
    item_size = len(index_list)
    temp_list = None

    # Code清單
    stock_code_list = []
    for data_str, i in zip(code_list[item_size+1:], range(len(code_list) - item_size - 1)):
        if i % item_size == 0:
            stock_data_list.append(temp_list)
            temp_list = []

        # Code 清單過濾規則，找到出現 \u3000 ，並且只擷取前4碼
        if data_str.text.find("\u3000") == 4:
            stock_code_list.append(data_str.text[:4])

        temp_str = data_str.text.replace("\u3000", " ")
        temp_list.append(temp_str)

    return stock_code_list

import time
import pandas as pd
import requests
import io
import datetime

type_twe_dict = {
    
    '01': '水泥工業',
    '02': '食品工業',
    '03': '塑膠工業',
    '04': '紡織纖維',
    '05': '電機機械',
    '06': '電器電纜',
    '07': '化學生技醫療',
    '08': '玻璃陶瓷',
    '09': '造紙工業',
    '10': '鋼鐵工業',
    '11': '橡膠工業',
    '12': '汽車工業',
    '13': '電子工業',
    '14': '建材營造',
    '15': '航運業',
    '16': '觀光事業',
    '17': '金融保險',
    '18': '貿易百貨',
    '20': '其他',
    '21': '化學工業',
    '22': '生技醫療業',
    '23': '油電燃氣業',
    '24': '半導體業',
    '25': '電腦及週邊設備業',
    '26': '光電業',
    '27': '通信網路業',
    '28': '電子零組件業',
    '29': '電子通路業',
    '30': '資訊服務業',
    '31': '其他電子業'}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def requests_get(*args1, **args2):
    i = 3
    while i >= 0:
        try:
            return requests.get(*args1, **args2)
        except (ConnectionError, requests.ReadTimeout) as error:
            print(error)
            print('retry one more time after 60s', i, 'times left')
            time.sleep(60)
        i -= 1
    return pd.DataFrame()

def crawlType(date, previous_days = 7):
    """取得目前對應種類的股票編號，包括上市上櫃。

    Args:
        date (datetime.date): 要確認哪一天的狀況，可以排除上市下市變化。
        previous_days (int, optional): 如果當天是假日，可以往前數n天。 Defaults to 7.

    Returns:
        Dict : 每個種類的股票編號
    """
    
    df_dict = dict()
    key = list(type_twe_dict.keys())[0]
    for times in range(previous_days):
        datestr = date.strftime('%Y%m%d')
        try:
            res = requests_get('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date='\
                            +datestr+'&type=%s' % key, headers=headers)
            if len(res.text) > 0:
                break
            
            print("date {date} is holidy, check next date".format(date = datestr))
            previous_days -= 1
            date = date - datetime.timedelta(days=1)
            time.sleep(5)
        except:
            return{}
        
    for key, key_counter in zip(type_twe_dict.keys(), range(len(type_twe_dict.keys()))):
        print("crawl type... key = %s   (%d/%d)    "%(type_twe_dict[key], key_counter+1, len(type_twe_dict.keys())+1),end='\r')
        time.sleep(5)
        try:
            res = requests_get('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date='\
                            +datestr+'&type=%s' % key, headers=headers)
                
            df = pd.read_csv(io.StringIO(res.text.replace('=','')), header=1)
            table = res.text[res.text.find('(') + 1 : res.text.find(')')]
            data = {
            '證券代號' : df['(元,股)'][1:-5],
            '證券名稱' : df['Unnamed: 1'][1:-5]
            }

            new_df = pd.DataFrame(data)
            df_dict.update({table : new_df})
        except:
            return {}
    print("crawl type... Finish                             ")
    return df_dict

if __name__ == "__main__":
    stock_code_list = getCodeList()
    print(stock_code_list)