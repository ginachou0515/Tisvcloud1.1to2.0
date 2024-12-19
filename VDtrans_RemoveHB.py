"""
!/usr/bin/env python 3.9
-*- coding: utf-8 -*-
@File  : VDtrans_RemoveHB.py
@Author: GinaChou
@Date  : 2024/12/18
"""
import requests
import xmltodict
import os
import xml.etree.ElementTree as ET


def url_xml_dict(url):
    """讀取並解析線上 XML
    url: XML 網址
    return: 轉換成 Python 的字典格式
    """
    html = requests.get(url)
    html.encoding = html.apparent_encoding  # 解決編碼不一致問題
    data = xmltodict.parse(html.text)
    return data


def get_center_code(url):
    """根據 URL 判斷區域代碼"""
    if "cloud_10" in url:
        return "N"
    elif "cloud_30" in url:
        return "C"
    elif "cloud_20" in url:
        return "P"
    elif "cloud_40" in url:
        return "S"
    else:
        return "Unknown"


def combine_zone(vd_data, url):
    """合併各區 VD 的 XML"""
    data = url_xml_dict(url)
    center_code = get_center_code(url)

    print(f"正在處理 {center_code} 區域的資料...")
    stops = data["file_attribute"]["oneday_eq_config_data"]["vd_data"]["vd"]

    for stop in stops:
        # 移除公總管理的特定設備
        if stop["@expresswayId"] in ["62", "64", "66", "68", "72", "74", "74A", "78", "82", "84", "86"]:
            print(f"跳過設備（Expressway {stop['@expresswayId']}）：{stop['@eqId']}")
            continue

        # 建立 VD 節點
        vd = ET.Element(
            "vd",
            {
                "eqId": stop["@eqId"],
                "freewayId": stop["@freewayId"],
                "expresswayId": stop["@expresswayId"],
                "directionId": stop["@directionId"],
                "milepost": stop["@milepost"],
                "interchange": stop["@interchange"],
                "eq_location": stop["@eq_location"],
                "vd_category": stop["@vd_category"],
                "lanes": stop["@lanes"],
                "px": stop["@longitude"],
                "py": stop["@latitude"],
                "uniqueId": stop["@uniqueId"],
            },
        )
        vd_data.append(vd)

    print(f"完成 {center_code} 區域的處理。")


if __name__ == "__main__":
    # 定義各區域的 URL
    URL_N = "https://tisv.tcloud.freeway.gov.tw/xml/cloud_10/10_1day_eq_config_data.xml"
    URL_C = "https://tisv.tcloud.freeway.gov.tw/xml/cloud_30/30_1day_eq_config_data.xml"
    URL_P = "https://tisv.tcloud.freeway.gov.tw/xml/cloud_20/20_1day_eq_config_data.xml"
    URL_S = "https://tisv.tcloud.freeway.gov.tw/xml/cloud_40/40_1day_eq_config_data.xml"

    # 讀取初始資料
    zone = URL_N
    data = url_xml_dict(zone)
    info = data["file_attribute"]

    # 建立 XML 樹的根節點
    root = ET.Element(
        "file_attribute",
        attrib={
            "file_name": info["@file_name"],
            "control_center_id": info["@control_center_id"],
            "time": info["@time"],
        },
    )
    child1 = ET.SubElement(root, "oneday_eq_config_data")
    vd_data = ET.SubElement(child1, "vd_data")

    # 合併各區資料
    combine_zone(vd_data, URL_N)
    combine_zone(vd_data, URL_C)
    combine_zone(vd_data, URL_P)
    combine_zone(vd_data, URL_S)

    # 將結果輸出為 XML 文件
    output_path = os.path.join(
        os.path.dirname(__file__), "vd", "vd_oneday_eq_config_data.xml"
    )
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    print(f"合併完成，輸出檔案位置：{output_path}")

## os.path.dirname(os.path.abspath(__file__))
## os.path.abspath(__file__)返回的是.py檔案的絕對路徑。