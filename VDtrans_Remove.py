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
    data = xmltodict.parse(html.text)
    return data


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

    for stop in stops: ##0322修
        if "T62" in stop["@eqId"]:#移除公總管理的設備
            print(f'不含台62：{stop["@eqId"]}')
            continue
        if "T64" in stop["@eqId"]:#移除公總管理的設備
            print(f'不含台64：{stop["@eqId"]}')
            continue
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
                "locationtype": "N(車道/路側)",  ##待思考怎麼改
                "px": stop["@longitude"],
                "py": stop["@latitude"]})

        Infos.append(Info)
    print(f'append_tree:{Infos}\nzone:{center}')

#https://www.796t.com/post/MjhucTY=.html
#https://blog.csdn.net/weixin_36708477/article/details/122547992


if __name__ == '__main__':

    URL_N = "http://210.241.131.244/xml/1day_eq_config_data_north.xml"
    URL_C = "http://210.241.131.244/xml/1day_eq_config_data_center.xml"
    URL_P = "http://210.241.131.244/xml/1day_eq_config_data_pinglin.xml"
    URL_S = "http://210.241.131.244/xml/1day_eq_config_data_south.xml"

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