#!/usr/bin/env python3
"""
@File  : VDcombine.py
@Author: GinaChou
@Date  : 2024/12/18
"""

import requests
import xmltodict
import os
import xml.etree.ElementTree as ET


def url_xml_dict(url):
    """
    讀取並解析線上 XML
    url: XML 網址
    return: XML 轉換成 Python 的字典格式
    """
    try:
        html = requests.get(url)
        html.encoding = html.apparent_encoding  # 自動偵測解碼
        data = xmltodict.parse(html.text)
        return data
    except Exception as e:
        print(f"無法讀取 URL：{url}\n錯誤：{e}")
        return None


def combine_zone(vd_data, url):
    """
    合併各區 VD 的 XML
    vd_data: XML 的 vd_data 節點
    url: 區域的 XML 資料來源 URL
    """
    data = url_xml_dict(url)
    if not data:
        print(f"無法解析 URL：{url}")
        return

    # 使用 URL 固定部分對應區域代碼
    if "cloud_10" in url:
        center_code = "N"
    elif "cloud_30" in url:
        center_code = "C"
    elif "cloud_20" in url:
        center_code = "P"
    elif "cloud_40" in url:
        center_code = "S"
    else:
        center_code = "Unknown"  # 若 URL 無法對應，則設為 Unknown

    print(f"正在處理區域中心代碼：{center_code}")

    stops = data["file_attribute"]["oneday_eq_config_data"]["vd_data"]["vd"]
    for stop in stops:
        if stop["@expresswayId"] in ["62", "64", "66", "68", "72", "74", "74A", "78", "82", "84", "86"]:  # 移除特定公總設備
            print(f"跳過設備（Expressway {stop['@expresswayId']}）：{stop['@eqId']}")
            continue

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
    print(f"已完成區域中心 {center_code} 的處理")


if __name__ == "__main__":
    # 定義區域 XML 網址
    urls = {
        "N": "https://tisv.tcloud.freeway.gov.tw/xml/cloud_10/10_1day_eq_config_data.xml",
        "C": "https://tisv.tcloud.freeway.gov.tw/xml/cloud_30/30_1day_eq_config_data.xml",
        "P": "https://tisv.tcloud.freeway.gov.tw/xml/cloud_20/20_1day_eq_config_data.xml",
        "S": "https://tisv.tcloud.freeway.gov.tw/xml/cloud_40/40_1day_eq_config_data.xml",
    }

    # 提取第一個區域的 file_name 和 time
    first_url = list(urls.values())[0]
    first_data = url_xml_dict(first_url)
    if not first_data:
        print("無法獲取第一個區域的 XML 資料，程式終止")
        exit()

    file_name = first_data["file_attribute"]["@file_name"]
    control_center_id = first_data["file_attribute"]["@control_center_id"]
    time = first_data["file_attribute"]["@time"]

    # 創建 XML 根節點，使用第一個區域的 file_name 和 time
    root = ET.Element(
        "file_attribute",
        attrib={"file_name": file_name, "control_center_id": control_center_id, "time": time},
    )
    child1 = ET.SubElement(root, "oneday_eq_config_data")
    vd_data = ET.SubElement(child1, "vd_data")

    # 處理各區域 XML
    for region, url in urls.items():
        combine_zone(vd_data, url)

    # 確保輸出目錄存在
    output_dir = os.path.join(os.path.dirname(__file__), "vd")
    os.makedirs(output_dir, exist_ok=True)

    # 輸出合併後的 XML
    output_file = os.path.join(output_dir, "vd_oneday_eq_config_data.xml")
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

    print(f"合併內網 XML 結束，輸出檔案：{output_file}")
