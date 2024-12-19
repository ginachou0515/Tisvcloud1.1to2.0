"""
!/usr/bin/env python
-*- coding: utf-8 -*-
@File  : CMScombine.py
@Author: GinaChou
@Date  : 2024/12/19
"""
import requests
import xmltodict
import os
import xml.etree.ElementTree as ET


def url_xml_dict(url):
    """讀取並解析線上 XML，並返回解析後的字典格式資料。"""
    try:
        html = requests.get(url)
        html.encoding = html.apparent_encoding  # 處理編碼問題
        data = xmltodict.parse(html.text)
        return data
    except requests.exceptions.RequestException as e:
        print(f"獲取 URL {url} 失敗: {e}")
        return None


def trans_combineV1(Infos, url):
    """將區域的 XML 資料轉換為 1.1 版本並合併 CMS 資料。"""
    data = url_xml_dict(url)
    if data is None:
        return

    # 從 URL 中提取區域代碼
    zone_code = url.split('/')[4][:1].upper()  # 提取區域代碼 (如 'N', 'C' 等)

    stops = data["file_attribute"]["oneday_eq_config_data"]["cms_data"]["cms"]

    for stop in stops:
        # 移除不需要的設備（如公總管理設備）
        if any(code in stop["@expresswayId"] for code in ["62", "64", "66", "68"]):
            print(f'跳過設備 {stop["@eqId"]} 因為不符合條件。')
            continue

        Info = ET.Element(
            'Info', {
                "cmsid": "nfb" + stop["@eqId"],
                "roadsection": "0",
                "locationpath": "0",
                "startlocationpoint": "0",
                "endlocationpoint": "0",
                "px": stop["@longitude"],
                "py": stop["@latitude"]
            })
        Infos.append(Info)

    print(f'區域 {zone_code} 資料處理完成。')


def combine_zone(CMS_DATA, url):
    """合併來自不同區域的 CMS 資料。"""
    data = url_xml_dict(url)
    if data is None:
        return

    # 從 URL 中提取區域代碼
    zone_code = url.split('/')[4][:1].upper()  # 提取區域代碼
    stops = data["file_attribute"]["oneday_eq_config_data"]["cms_data"]["cms"]

    for stop in stops:
        if stop["@expresswayId"] in ["62", "64", "66", "68", "72", "74", "74A", "78", "82", "84", "86"]:  # 移除特定公總設備
            print(f"跳過設備（台{stop['@expresswayId']}）：{stop['@eqId']}")
            continue

        cms = ET.Element(
            'cms', {
                "eqId": stop["@eqId"],
                "freewayId": stop["@freewayId"],
                "expresswayId": stop["@expresswayId"],
                "directionId": stop["@directionId"],
                "milepost": stop["@milepost"],
                "interchange": stop["@interchange"],
                "eq_location": stop["@eq_location"],
                "cms_type": stop["@cms_type"],
                "px": stop["@longitude"],
                "py": stop["@latitude"],
                "uniqueId": stop["@uniqueId"]
            })
        CMS_DATA.append(cms)

    print(f'區域 {zone_code} CMS 資料合併完成。')


def main():
    # 設定區域對應的 URL
    url_dict = {
        'N': "https://tisv.tcloud.freeway.gov.tw/xml/cloud_10/10_1day_eq_config_data.xml",
        'C': "https://tisv.tcloud.freeway.gov.tw/xml/cloud_30/30_1day_eq_config_data.xml",
        'P': "https://tisv.tcloud.freeway.gov.tw/xml/cloud_20/20_1day_eq_config_data.xml",
        'S': "https://tisv.tcloud.freeway.gov.tw/xml/cloud_40/40_1day_eq_config_data.xml"
    }

    # 取得第一個區域的資料
    zone = url_dict['N']  # 從 N 區開始
    data = url_xml_dict(zone)
    if data is None:
        return

    info = data["file_attribute"]
    root = ET.Element(
        'file_attribute', {
            "file_name": info["@file_name"],
            "control_center_id": info["@control_center_id"],
            "time": info["@time"]
        })

    child1 = ET.SubElement(root, "oneday_eq_config_data")
    CMS_DATA = ET.SubElement(child1, 'cms_data')

    # 處理每個區域的資料
    for zone_code, url in url_dict.items():
        print(f"處理區域 {zone_code} 的資料...")
        combine_zone(CMS_DATA, url)

    # 輸出最終合併的 XML
    output_path = os.path.join(os.path.dirname(__file__), 'CMS', "cms_oneday_eq_config_data.xml")
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8")

    print(f'合併 XML 完成，輸出檔案: {output_path}')


if __name__ == '__main__':
    main()