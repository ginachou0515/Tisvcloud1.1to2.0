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

    tree = ET.parse('Section.xml')  # 解析為ElementTree對象
    root = tree.getroot()  # 獲取根元素
    Linktree = ET.parse('SectionLink.xml')  # 解析為ElementTree對象
    Linkroot = Linktree.getroot()  # 獲取根元素
    Shapetree = ET.parse('SectionShape.xml')  # 解析為ElementTree對象
    Shaperoot = Shapetree.getroot()  # 獲取根元素

    deleted_id = []
    with open('delete.txt') as reader:
        for line in reader:
            line = line.strip()
            deleted_id.append(line)

    ns = {"LinkList": "http://ptx.transportdata.tw/standard/schema/TIX"}

    ####Section######
    for Section in root.findall('LinkList:Sections', ns):
        print(f'路段基本資訊(Section)修改')
        for SectionLink in Section.findall('LinkList:Section', ns):
            SectionID = SectionLink.find('LinkList:SectionID', ns)
            print(f'SectionID：{SectionID.text}')
            if SectionID.text in deleted_id:  # 刪除包含在deleted_id內的資料
                print(f'SectionID(del):{SectionID.text}')
                Section.remove(SectionLink)  # 删除SectionLinks下的元素標籤[非根標籤!!!!]
    tree.write('Section_modified.xml')  # 保存修改後的XML文件
    print(f'Section修改完成，輸出Section_modified.xml')

    ####SectionLink######
    for Link in Linkroot.findall('LinkList:SectionLinks', ns):
        print(f'路段基礎組合對應資訊(SectionLink)修改')
        for SectionLink in Link.findall('LinkList:SectionLink', ns):
            SectionID = SectionLink.find('LinkList:SectionID', ns)
            print(f'SectionID：{SectionID.text}')
            if SectionID.text in deleted_id:  # 刪除包含在deleted_id內的資料
                print(f'SectionID(del):{SectionID.text}')
                Link.remove(SectionLink)  # 删除SectionLinks下的元素標籤[非根標籤!!!!]
    Linktree.write('SectionLink_modified.xml')  # 保存修改後的XML文件
    print(f'SectionLink修改完成，輸出SectionLink_modified.xml')

    ####SectionShape######
    for Shape in Shaperoot.findall('LinkList:SectionShapes', ns):
        print(f'路段線型圖資資訊(SectionShape)修改')
        for SectionShape in Shape.findall('LinkList:SectionShape', ns):
            SectionID = SectionShape.find('LinkList:SectionID', ns)
            print(f'SectionID(Shape)：{SectionID.text}')
            if SectionID.text in deleted_id:  # 刪除包含在deleted_id內的資料
                print(f'SectionID(del):{SectionID.text}')
                Shape.remove(SectionShape)  # 删除SectionLinks下的元素標籤[非根標籤!!!!]
    Shapetree.write('SectionShape_modified.xml')  # 保存修改後的XML文件
    print(f'SectionShape修改完成，輸出SectionShape_modified.xml')