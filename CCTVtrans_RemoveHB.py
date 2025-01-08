"""
!/usr/bin/env python
-*- coding: utf-8 -*-
@File  : CCTVtrans_RemoveHB.py.py
@Author: GinaChou
@Date  : 2025/01/07
"""

import requests
import xmltodict
import os
import xml.etree.ElementTree as ET

# 公路路線與 freewayId 對應表
FREEWAY_ID_MAPPING = {
    "20620": "62",
    "20640": "64",
    "20660": "66",
    "20680": "68",
    "20720": "72",
    "20740": "74",
    "20741": "74A",
    "20780": "78",
    "20820": "82",
    "20840": "84",
    "20860": "86",
}


def download_xml(url, output_file):
    """
    下載 XML 文件並保存
    :param url: XML 文件的 URL
    :param output_file: 保存的檔案路徑
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.text.strip() == "":
            raise ValueError("下載的 XML 文件為空")
        if not response.text.strip().startswith("<?xml"):
            raise ValueError("下載的內容不是有效的 XML 文件")

        with open(output_file, 'wb') as file:
            file.write(response.content)
        print(f"下載完成：{output_file}")
    except requests.RequestException as e:
        print(f"下載失敗：{e}")
    except ValueError as ve:
        print(f"下載失敗：{ve}")


def url_xml_dict(url):
    """
    讀取並解析線上 XML 文件
    :param url: XML 文件的 URL
    :return: 轉換成 Python 字典格式的 XML 資料
    """
    try:
        html = requests.get(url)
        html.encoding = html.apparent_encoding
        data = xmltodict.parse(html.text)
        return data
    except Exception as e:
        print(f"解析 XML 時發生錯誤：{e}")
        return None


def should_exclude(stop):
    """
    判斷是否需要排除設備
    :param stop: 單個設備的資料
    :return: (bool, str) - True 表示排除，並返回排除訊息
    """
    if stop["@enabled"] == "0":  # 不啟用的設備
        return True, "不啟用的設備"

    freeway_id = stop.get("@freewayId", "")
    if freeway_id in FREEWAY_ID_MAPPING:  # 判斷是否屬於指定 freewayId
        highway = FREEWAY_ID_MAPPING[freeway_id]
        return True, f"移除公總管理 台{highway}設備"

    return False, ""  # 不排除


def create_info_element(stop):
    """
    創建單個設備的 XML 元素
    :param stop: 單個設備的資料
    :return: 設備的 XML 元素
    """
    return ET.Element(
        "Info",
        {
            "cctvid": "nfb" + str(stop["@eqId"]),
            "roadsection": "0",
            "locationpath": "0",  # 避免錯誤，設置預設值
            "startlocationpoint": "0",
            "endlocationpoint": "0",
            "px": str(stop["@longitude"]),
            "py": str(stop["@latitude"]),
        },
    )


def main():
    # 定義 XML 的 URL
    url = "https://tisv.tcloud.freeway.gov.tw/xml/cloud_00/1day_cctv_config_data_https.xml"

    # 建立 CCTV 資料夾
    output_dir = os.path.join(os.path.dirname(__file__), "CCTV")
    os.makedirs(output_dir, exist_ok=True)

    # 定義下載與輸出檔案名稱
    download_file = os.path.join(output_dir, "1day_cctv_config_data_https.xml")
    output_file = os.path.join(output_dir, "cctv_info_0000.xml")

    # 下載 XML 文件
    download_xml(url, download_file)

    # 解析 XML 文件
    data = url_xml_dict(url)
    if not data:
        print("無法處理 XML，程式結束。")
        return

    # 創建 XML 根節點
    info = data["cctvinfo"]
    stops = info["cctv"]

    root = ET.Element(
        "XML_Head",
        attrib={
            "version": "1.1",
            "listname": "CCTV靜態資訊",
            "updatetime": info["@time"],
            "interval": "86400",
        },
    )
    Infos = ET.SubElement(root, "Infos")

    # 過濾與添加設備資訊
    for stop in stops:
        exclude, message = should_exclude(stop)
        if exclude:
            print(f"排除設備：{stop['@eqId']} - {message}")
            continue
        Info = create_info_element(stop)
        Infos.append(Info)

    # 輸出 XML 檔案
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"{info['@time']} - 輸出更新 CCTV 檔：{output_file}")


if __name__ == "__main__":
    main()