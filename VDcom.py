"""
!/usr/bin/env python 3.9
-*- coding: utf-8 -*-
@File  : vdtrans.py
@Author: GinaChou
@Date  : 2023/01/18
"""

import requests
import xmltodict
import glob
import os
import xml.etree.ElementTree as ET
from xml.etree import ElementTree


def url_xml_dict(url):
    '''讀取並解析線上xml
       url: xml網址
       return: XML轉換成Python的字典格式'''
    html = requests.get(url)
    html.encoding = html.apparent_encoding ##內容解碼跟編碼不一致
    data = xmltodict.parse(html.text) ##1130607 ,encoding="utf-8"
    # print(f'html.text：{html.text}\ntype:{type(html.text)}')
    # print(f'data：{data}')
    return data
#https://blog.csdn.net/lilongsy/article/details/122140098

def combine_zone(vd_DATA,URL):
    # 合併各區vd的XML
    zone = URL
    data = url_xml_dict(zone)
    # print(f'data：{data}')
    str = "1day_eq_config_data_"
    center = zone[zone.find(str) +
                   len(str):zone.find(str) +
                   len(str) +
                   1].upper()
    # str.upper() ##全部變成大寫
    info = data["file_attribute"]
    stops = data["file_attribute"]["oneday_eq_config_data"]["vd_data"]["vd"]
    for stop in stops:
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
        vd = ET.Element(
            'vd', {
                "eqId":stop["@eqId"],
                "freewayId": stop["@freewayId"],
                "expresswayId":stop["@expresswayId"],
                "directionId": stop["@directionId"],
                "milepost": stop["@milepost"],
                "interchange": stop["@interchange"],
                "eq_location":stop["@eq_location"],
                "vd_category": stop["@vd_category"],
                "lanes": stop["@lanes"],
                "px": stop["@longitude"],
                "py": stop["@latitude"],
                "uniqueId": stop["@uniqueId"]
            })
        # print(f'eqId：{stop["@eqId"]}')
        vd_DATA.append(vd)
    print(f'append_to_XML:{vd_DATA}\nzone:{center}')

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
    # str.upper() ##全部變成大寫
    info = data["file_attribute"]
    eqips = data["file_attribute"]["oneday_eq_config_data"]
    stops = data["file_attribute"]["oneday_eq_config_data"]["vd_data"]["vd"]

    root = ET.Element(
        'file_attribute',
        attrib={
            "file_name": info["@file_name"],
            "control_center_id": info["@control_center_id"],
            "time": info["@time"]})

    child1 = ET.SubElement(root, "oneday_eq_config_data")
    vd_DATA = ET.SubElement(child1, 'vd_data')

    combine_zone(vd_DATA,URL_N)
    combine_zone(vd_DATA,URL_C)
    combine_zone(vd_DATA,URL_P)
    combine_zone(vd_DATA,URL_S)

    tree = ET.ElementTree(root)

    tree.write(
        os.path.join(
            os.path.dirname(__file__),'vd',
            "vd_oneday_eq_config_data.xml"),encoding="utf-8")  ##,encoding="utf-8"

    print(f'合併內網XML結束，輸出檔案:vd_eq_config')
