"""
!/usr/bin/env python
-*- coding: utf-8 -*-
@File  : CMStrans_RemoveHB.py.py
@Author: GinaChou
@Date  : 2024/12/19
"""
import requests
import xmltodict
import os
import xml.etree.ElementTree as ET


def url_xml_dict(url):
    """讀取並解析線上 XML，將其轉換為 Python 字典格式"""
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


def trans_combine_v1(Infos, URL):
    """從內網 XML 轉為 1.1 版本，並合併各區 CMS 的 XML"""
    data = url_xml_dict(URL)
    center_code = get_center_code(URL)
    print(f"正在處理 {center_code} 區域的資料...")

    stops = data["file_attribute"]["oneday_eq_config_data"]["cms_data"]["cms"]
    for stop in stops:
        # 移除公總管理的特定設備
        if stop["@expresswayId"] in ["62", "64", "66", "68", "72", "74", "74A", "78", "82", "84", "86"]:
            print(f"跳過設備（台{stop['@expresswayId']}）：{stop['@eqId']}")
            continue

        # 建立 CMS 設備節點
        Info = ET.Element(
            "Info", {
                "cmsid": "nfb" + stop["@eqId"],
                "roadsection": "0",
                "locationpath": "0",  # 位置屬性設為 0
                "startlocationpoint": "0",
                "endlocationpoint": "0",
                "px": stop["@longitude"],
                "py": stop["@latitude"]
            }
        )
        Infos.append(Info)

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
        "XML_Head",
        attrib={
            "version": "1.1",
            "listname": "CMS靜態資訊",
            "updatetime": info["@time"],
            "interval": "86400"  # 每 24 小時更新一次
        },
    )
    Infos = ET.SubElement(root, "Infos")

    # 合併各區域資料
    trans_combine_v1(Infos, URL_N)
    trans_combine_v1(Infos, URL_C)
    trans_combine_v1(Infos, URL_P)
    trans_combine_v1(Infos, URL_S)

    # 將結果輸出為 XML 文件
    output_path = os.path.join(
        os.path.dirname(__file__), "CMS", "cms_info_0000.xml"
    )
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    print(f"合併完成，輸出檔案位置：{output_path}")

