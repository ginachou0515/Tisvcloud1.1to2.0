"""
!/usr/bin/env python
-*- coding: utf-8 -*-
@File  : section_1968_trans1.1.py
@Author: GinaChou
@Date  : 2023/1/11
"""

import pandas as pd
import os
from datetime import datetime
import numpy as np

def ReadExcel(file, sheet= 0):
    return pd.read_excel(file, sheet_name=sheet, header=None) #想要自行設定標題
    # return pd.read_excel(file, encoding="utf-8", sheet_name=sheet)

def OutputExcel(dataframe, name, sheet="工作表1"):
    Result_Path = "./output"  # 開啟檔案
    if not os.path.exists(Result_Path):
        os.makedirs(Result_Path)
    Result_Name = Result_Path + "/" + name + ".xlsx"
    # excel_writer ： ExcelWriter目標路徑
    writer = pd.ExcelWriter(Result_Name)
    # writer = pd.ExcelWriter(Result_PATH, engine='xlsxwriter')
    dataframe.to_excel(writer, sheet_name=sheet, index=False, encoding="utf-8")
    writer.save()
    print("成功產出:" + Result_Name)
    # columns參數用於指定生成的excel中列的順序
    # raw_df.to_excel(writer, columns=['char','num'], index=False,encoding='utf-8',sheet_name='Sheet')
    # header :指定作為列名的行，預設0，即取第一行，資料為列名行以下的資料；若資料不含列名，則設定 header = None；
    # index：預設為True，顯示index，當index=False 則不顯示行索引（名字）


if __name__ == '__main__':

    name = "section_1968_traffic_data"
    file_type = ".xlsx"
    file_name = f"{name}{file_type}"
    raw_df = ReadExcel(file_name, )

    if = raw_df[freewayId]
    df = raw_df["height"]


# OutputExcel(dataframe, name, sheet="工作表1")
