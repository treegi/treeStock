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

if __name__ == "__main__":
    stock_code_list = getCodeList()
    print(stock_code_list)