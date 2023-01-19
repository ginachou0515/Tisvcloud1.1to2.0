"""
!/usr/bin/env python 3.9
-*- coding: utf-8 -*-
@File  : CMStrans.py
@Author: GinaChou
@Date  : 2023/01/18
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


def combine(Infos,stops,center):  ##
    for stop in stops:
        Info = ET.Element(
            'Info', {
                "cmsid": "nfb" + stop["@eqId"],
                "roadsection": "0",
                "locationpath": "0",  # 給""會出現locationpath錯誤，推測是因為屬性
                "startlocationpoint": "0",
                "endlocationpoint": "0",
                "px": stop["@longitude"],
                "py": stop["@latitude"]})
        Infos.append(Info)
    print(f'append_tree:{Infos}\nzone:{center}')


if __name__ == '__main__':

    URL_N = "http://210.241.131.244/xml/1day_eq_config_data_north.xml"
    URL_C = "http://210.241.131.244/xml/1day_eq_config_data_center.xml"
    URL_P = "http://210.241.131.244/xml/1day_eq_config_data_pinglin.xml"
    URL_S = "http://210.241.131.244/xml/1day_eq_config_data_south.xml"
    # download_xml(URL_N)

    zone = URL_N
    data = url_xml_dict(zone)
    str = "1day_eq_config_data_"
    center = zone[zone.find(str) +
                   len(str):zone.find(str) +
                   len(str) +
                   1].upper()
    # str.upper() ##全部變成大寫
    info = data["file_attribute"]
    eqips = data["file_attribute"]["oneday_eq_config_data"]
    stops = data["file_attribute"]["oneday_eq_config_data"]["cms_data"]["cms"]

    root = ET.Element(
        'XML_Head',
        attrib={
            "version": "1.1",
            "listname": "CMS靜態資訊",
            "updatetime": info["@time"],
            "interval": "86400"})

    Infos = ET.SubElement(root, 'Infos')
    # print(f'Infos_tree:{Infos}')
    combine(Infos, stops, center)

    # for stop in stops:
    #     Info = ET.Element(
    #         'Info', {
    #             "cmsid": "nfb" + stop["@eqId"],
    #             "roadsection": "0",
    #             "locationpath": "0",  # 給""會出現locationpath錯誤，推測是因為屬性
    #             "startlocationpoint": "0",
    #             "endlocationpoint": "0",
    #             "px": stop["@longitude"],
    #             "py": stop["@latitude"]})
    #
    #     Infos.append(Info)

    tree = ET.ElementTree(root)

    tree.write(
        os.path.join(
            os.path.dirname(__file__),'CMS',
            "cms_info_0000.xml"),encoding="utf-8")

    # tree.write(
    #     os.path.join(
    #         os.path.dirname(__file__),
    #         "cms_info_0000_" + center + ".xml"),encoding="utf-8")

## os.path.dirname(os.path.abspath(__file__))
## os.path.abspath(__file__)返回的是.py檔案的絕對路徑。