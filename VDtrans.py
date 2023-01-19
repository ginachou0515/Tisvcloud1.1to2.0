"""
!/usr/bin/env python 3.9
-*- coding: utf-8 -*-
@File  : VDtrans.py
@Author: GinaChou
@Date  : 2023/01/17
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


def combine(files):  ##有問題
    xml_files = glob.glob(files +"/*.xml") #xml_files = glob.glob(files + "/*.xml")
    # xml_files = os.listdir(files)
    xml_element_tree = None
    for xml_file in xml_files:
        # if xml_file.endswith('.xml'):
            # get root
        data = ElementTree.parse(xml_file).getroot() #xml.etree.ElementTree.ParseError: no element found: line 1, column 0
        print(f'get root：{data}')
        for result in data.iter('Info'):
            if xml_element_tree is None:
                xml_element_tree = data
            else:
                xml_element_tree.extend(result)

    if xml_element_tree is not None:
        out = open("vd_info_0000.xml", "wb")
        print(out)
        print(f'tree:{ElementTree.tostring(xml_element_tree)}')
#https://www.796t.com/post/MjhucTY=.html
#https://blog.csdn.net/weixin_36708477/article/details/122547992


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

    xml_path = os.path.dirname(__file__)
    print(f'path：{xml_path}')
    # "D:\\xmlReport\\"
    combine(xml_path)

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

    for stop in stops:
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
                "locationtype": "N(車道/路側)",
                "px": stop["@longitude"],
                "py": stop["@latitude"]})

        Infos.append(Info)

    tree = ET.ElementTree(root)

    tree.write(
        os.path.join(
            os.path.dirname(__file__),
            "vd_info_0000_" + center + ".xml"),encoding="utf-8")



## os.path.dirname(os.path.abspath(__file__))
## os.path.abspath(__file__)返回的是.py檔案的絕對路徑。