"""
!/usr/bin/env python
-*- coding: utf-8 -*-
@File  : SECTIONdel.py
@Author: GinaChou
@Date  : 2024/3/4
"""

import requests
import glob
import os
import sys
import xml.etree.ElementTree as ET
from xml.etree import ElementTree
from bs4 import BeautifulSoup


def download_xml(url):
    response = requests.get(url)
    Result_Name = "1day_cctv_config_data.xml"
    with open(Result_Name, 'wb') as file:
        file.write(response.content)


def url_xml_dict(url):
    '''讀取並解析線上xml
       url: xml網址
       return: XML轉換成Python的字典格式'''
    html = requests.get(url)
    data = xmltodict.parse(html.text)
    return data

# 讀取excel檔


def ReadExcel(file, sheet=0):
    return pd.read_excel(file, sheet_name=sheet)


if __name__ == '__main__':
    ET.register_namespace(
        '', "http://ptx.transportdata.tw/standard/schema/TIX")  # 註冊命名空間
    tree = ET.parse('SectionLink.xml')  # 解析為ElementTree對象
    root = tree.getroot()  # 獲取根元素

    deleted_id = []
    with open('delete.txt') as reader:
        for line in reader:
            line = line.strip()
            deleted_id.append(line)

    ns = {"LinkList": "http://ptx.transportdata.tw/standard/schema/TIX"}

    for Section in root.findall('LinkList:SectionLinks', ns):
        for SectionLink in Section.findall('LinkList:SectionLink', ns):
            SectionID = SectionLink.find('LinkList:SectionID', ns)
            print(f'SectionID：{SectionID.text}')
            if SectionID.text in deleted_id:  # 刪除包含在deleted_id內的資料
                print(f'SectionID(del):{SectionID.text}')
                Section.remove(SectionLink)  # 删除SectionLinks下的元素標籤[非根標籤!!!!]
    tree.write('modified.xml')  # 保存修改後的XML文件
