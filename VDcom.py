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
    data = xmltodict.parse(html.text)
    return data


def trans_combineV1(Infos,URL):  ##此處用不到?
    # 從內網XML轉為1.1版本，並合併各區VD的XML
    zone = URL
    data = url_xml_dict(zone)
    str = "1day_eq_config_data_"
    center = zone[zone.find(str) +
                   len(str):zone.find(str) +
                   len(str) +
                   1].upper()
    # str.upper() ##全部變成大寫
    info = data["file_attribute"]
    stops = data["file_attribute"]["oneday_eq_config_data"]["vd_data"]["vd"]
    for stop in stops:
        Info = ET.Element(
            'Info', {
                "vdid": "nfb" + stop["@eqId"],
                "roadsection": "0",
                "locationpath": "0",  # 給""會出現locationpath錯誤，推測是因為屬性
                "startlocationpoint": "0",
                "endlocationpoint": "0",
                "px": stop["@longitude"],
                "py": stop["@latitude"]})
        Infos.append(Info)
    print(f'append_to_XML1.1:{Infos}\nzone:{center}')


def combine_zone(vd_DATA,URL):
    # 合併各區vd的XML
    zone = URL
    data = url_xml_dict(zone)
    str = "1day_eq_config_data_"
    center = zone[zone.find(str) +
                   len(str):zone.find(str) +
                   len(str) +
                   1].upper()
    # str.upper() ##全部變成大寫
    info = data["file_attribute"]
    stops = data["file_attribute"]["oneday_eq_config_data"]["vd_data"]["vd"]
    for stop in stops:
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
        vd_DATA.append(vd)
    print(f'append_to_XML:{vd_DATA}\nzone:{center}')

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
            "vd_oneday_eq_config_data.xml"),encoding="utf-8")

    print(f'合併內網XML結束，輸出檔案:vd_eq_config')
