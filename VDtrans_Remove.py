"""
!/usr/bin/env python 3.9
-*- coding: utf-8 -*-
@File  : VDtrans_Remove.py
@Author: GinaChou
@Date  : 2023/03/22
"""

import requests
import xmltodict
import glob
import os
import xml.etree.ElementTree as ET
from xml.etree import ElementTree

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
    html.encoding = html.apparent_encoding ##內容解碼跟編碼不一致 1130607
    data = xmltodict.parse(html.text)
    return data
#https://blog.csdn.net/lilongsy/article/details/122140098

def combine(Infos,URL):  ##修改中 0322
    # 合併各區的XML
    """
    :param Infos: 各區XML<Infos>內的資料
    :param URL: 各區的XML
    :return:
    """
    zone = URL
    data = url_xml_dict(zone)
    str = "1day_eq_config_data_"
    center = zone[zone.find(str) +
                   len(str):zone.find(str) +
                   len(str) +
                   1].upper()
    # str.upper() ##全部變成大寫
    info = data["file_attribute"]
    eqips = data["file_attribute"]["oneday_eq_config_data"]
    stops = data["file_attribute"]["oneday_eq_config_data"]["vd_data"]["vd"]

    for stop in stops: ##0526修改為以expresswayId欄位判斷，避免在尾端的被刪除，如：VD-N1-S-5-I-ES-大華系統-T62W1S
        if "62" in stop["@expresswayId"]:#移除公總管理的設備
            print(f'不含台62：{stop["@eqId"]}')
            continue
        if "64" in stop["@expresswayId"]:#移除公總管理的設備
            print(f'不含台64：{stop["@eqId"]}')
            continue
        if "66" in stop["@expresswayId"]:#移除公總管理的設備
            print(f'不含台66：{stop["@eqId"]}')
            continue
        if "68" in stop["@expresswayId"]:#移除公總管理的設備
            print(f'不含台68：{stop["@eqId"]}')
            continue
        ##2024/07/15##
        if "RS" in stop["@eqId"]:
            location = "1"
        else:
            location = "5"

        Info = ET.Element(
            'Info', {
                "vdid": "nfb" + stop["@eqId"],
                "routeid": "0",
                "roadsection": "0",
                "locationpath": "0",  # 給""會出現locationpath錯誤，推測是因為屬性
                "startlocationpoint": "0",
                "endlocationpoint": "0",
                "roadway": "單向",
                "vsrnum": stop["@lanes"],
                "vdtype": stop["@vd_category"],
                "locationtype": location,  ##待思考設置位置怎麼改 "N(車道/路側)"
                "px": stop["@longitude"],
                "py": stop["@latitude"]})

        Infos.append(Info)
    print(f'append_tree:{Infos}\nzone:{center}')

#https://www.796t.com/post/MjhucTY=.html
#https://blog.csdn.net/weixin_36708477/article/details/122547992


if __name__ == '__main__':
    # URL_N = "http://210.241.131.244/xml/1day_eq_config_data_north.xml"
    # URL_C = "http://210.241.131.244/xml/1day_eq_config_data_center.xml"
    # URL_P = "http://210.241.131.244/xml/1day_eq_config_data_pinglin.xml"
    # URL_S = "http://210.241.131.244/xml/1day_eq_config_data_south.xml"
    URL_N = "https://tisv.tcloud.freeway.gov.tw/xml/cloud_10/10_1day_eq_config_data.xml"
    URL_C = "https://tisv.tcloud.freeway.gov.tw/xml/cloud_30/30_1day_eq_config_data.xml"
    URL_P = "https://tisv.tcloud.freeway.gov.tw/xml/cloud_20/20_1day_eq_config_data.xml"
    URL_S = "https://tisv.tcloud.freeway.gov.tw/xml/cloud_40/40_1day_eq_config_data.xml"

    zone = URL_N
    data = url_xml_dict(zone)
    str = "1day_eq_config_data_"
    center = zone[zone.find(str) +
                   len(str):zone.find(str) +
                   len(str) +
                   1].upper()

    info = data["file_attribute"]
    eqips = data["file_attribute"]["oneday_eq_config_data"]
    stops = data["file_attribute"]["oneday_eq_config_data"]["vd_data"]["vd"]

    root = ET.Element(
        'XML_Head',
        attrib={
            "version": "1.1",
            "listname": "VD靜態資訊",
            "updatetime": info["@time"],
            "interval": "86400"})

    Infos = ET.SubElement(root, 'Infos')
    # print(f'Infos_tree:{Infos}')
    combine(Infos, URL_N)
    combine(Infos, URL_C)
    combine(Infos, URL_P)
    combine(Infos, URL_S)

    tree = ET.ElementTree(root)

    tree.write(
        os.path.join(
            os.path.dirname(__file__),'VD',
            "vd_info_0000.xml"),encoding="utf-8")

    print(f'{info["@time"]}\n合併結束，輸出檔案:vd_info_0000.xml')
## os.path.dirname(os.path.abspath(__file__))
## os.path.abspath(__file__)返回的是.py檔案的絕對路徑。