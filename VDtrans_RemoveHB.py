"""
!/usr/bin/env python 3.9
-*- coding: utf-8 -*-
@File  : VDtrans_RemoveHB.py
@Author: GinaChou
@Date  : 2024/12/18
"""

import os
import requests
import xmltodict
import xml.etree.ElementTree as ET

def download_xml(url, output_file):
    """
    下載 XML 並儲存至本地檔案。
    :param url: XML 網址
    :param output_file: 儲存檔案名稱
    """
    response = requests.get(url)
    with open(output_file, 'wb') as file:
        file.write(response.content)

def url_xml_dict(url):
    """
    讀取並解析線上 XML 為字典格式。
    :param url: XML 網址
    :return: XML 轉換成 Python 字典
    """
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    return xmltodict.parse(response.text)

def combine(Infos, url):
    """
    合併區域 XML 資料。
    :param Infos: XML 根節點 <Infos>
    :param url: 區域 XML 網址
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
        expressway_id = stop.get("@expresswayId", "")

        # 移除公總管理的特定設備
        if expressway_id in ["62", "64", "66", "68", "72", "74", "74A", "78", "82", "84", "86"]:
            print(f"跳過公總管理設備（Expressway {expressway_id}）：{stop['@eqId']}")
            continue

        # 設定 locationtype
        location = "1" if "RS" in stop["@eqId"] else "5"

        # 建立 Info 節點
        Info = ET.Element(
            'Info',
            {
                "vdid": "nfb" + stop["@eqId"],
                "routeid": "0",
                "roadsection": "0",
                "locationpath": "0",
                "startlocationpoint": "0",
                "endlocationpoint": "0",
                "roadway": "單向",
                "vsrnum": stop["@lanes"],
                "vdtype": stop["@vd_category"],
                "locationtype": location,
                "px": stop["@longitude"],
                "py": stop["@latitude"]
            }
        )
        Infos.append(Info)
    print(f"已完成區域中心 {center_code} 的處理")

if __name__ == '__main__':
    # 定義各區域的 URL
    url_dict = {
        'N': "https://tisv.tcloud.freeway.gov.tw/xml/cloud_10/10_1day_eq_config_data.xml",
        'C': "https://tisv.tcloud.freeway.gov.tw/xml/cloud_30/30_1day_eq_config_data.xml",
        'P': "https://tisv.tcloud.freeway.gov.tw/xml/cloud_20/20_1day_eq_config_data.xml",
        'S': "https://tisv.tcloud.freeway.gov.tw/xml/cloud_40/40_1day_eq_config_data.xml"
    }

    # 建立 XML 根節點
    first_url = next(iter(url_dict.values()))
    first_data = url_xml_dict(first_url)
    update_time = first_data["file_attribute"].get("@time", "unknown")

    root = ET.Element(
        'XML_Head',
        attrib={
            "version": "1.1",
            "listname": "VD靜態資訊",
            "updatetime": update_time,
            "interval": "86400"
        }
    )
    Infos = ET.SubElement(root, 'Infos')

    # 合併各區資料
    for region, url in url_dict.items():
        combine(Infos, url)

    # 確保輸出目錄存在
    output_dir = os.path.join(os.path.dirname(__file__), 'VD')
    os.makedirs(output_dir, exist_ok=True)

    # 輸出合併後的 XML
    output_file = os.path.join(output_dir, "vd_info_0000.xml")
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

    print(f"合併完成，輸出檔案：{output_file}")


## os.path.dirname(os.path.abspath(__file__))
## os.path.abspath(__file__)返回的是.py檔案的絕對路徑。