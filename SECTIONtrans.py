"""
!/usr/bin/env python
-*- coding: utf-8 -*-
@File  : SECTIONtrans.py
@Author: GinaChou
@Date  : 2024/2/23
"""

import requests
import xmltodict
import glob
import os
import pandas as pd
import numpy as np
import sys
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

# 讀取excel檔
def ReadExcel(file, sheet=0):
    return pd.read_excel(file, sheet_name=sheet)


if __name__ == '__main__':
    URL = "http://210.241.131.244/xml/section_1968_traffic_data.xml"
    # download_xml(URL)
    ### 路段名稱###.
    file_name = "道路名稱.xlsx"
    df = ReadExcel(file_name, f"道路編碼")  # 道路編碼 省道速限 國道速限
    # 轉為文字類別
    df[["RoadId"]] = df[["RoadId"]].astype(str)  # RoadId	1.1版本	交通局
    # print(df.info())
    # print(f'{type(df)}\n{df}')

    data = url_xml_dict(URL)
    info = data["file_attribute"]
    section_traffic = data["file_attribute"]["section_traffic_data"]
    traffics = data["file_attribute"]["section_traffic_data"]["traffic_data"]

    root = ET.Element(
        'XML_Head',
        attrib={
            "version": "1.1",
            "listname": "路段靜態資訊",
            "updatetime": info["@time"],
            "interval": "86400"})

    Infos = ET.SubElement(root, 'Infos')
    for traffic in traffics:  # 0526修改為以包含標頭設備判斷
        ###移除移交公總######
        # if "0" in traffic["@enabled"]: #移除不發表於1968的設備
        #     print(f'不發表於1968：{traffic["@eqId"]}')
        #     continue
        # if "CCTV-T62" in traffic["@eqId"]:#移除公總管理的設備
        #     print(f'不含台62：{traffic["@eqId"]}')
        #     continue
        # if "CCTV-T64" in traffic["@eqId"]:#移除公總管理的設備
        #     print(f'不含台64：{traffic["@eqId"]}')
        #     continue
        # if "CCTV-T66" in traffic["@eqId"]:#移除公總管理的設備
        #     print(f'不含台66：{traffic["@eqId"]}')
        #     continue
        # if "CCTV-T68" in traffic["@eqId"]:#移除公總管理的設備
        #     print(f'不含台68：{traffic["@eqId"]}')
        #     continue
        if traffic["@expresswayId"] == "0":  # 判斷國道/非國道
            roadtype = 1  # 國道
            FI = df[df['RoadId'] == traffic["@freewayId"]]  # 產出道路名稱
            RoadID = FI['1.1版本'].values[0]
            # print(f'高速公路編碼：{traffic["@freewayId"]}\tRoadId：{RoadID}')
        else:
            roadtype = 2
            RoadID = df[df['RoadId'] ==
                        traffic["@expresswayId"]]['1.1版本'].values[0]
            # print(f'快速道路編碼：{traffic["@expresswayId"]}\tRoadId：{RoadID}')
        # print(f'freewayId:{traffic["@freewayId"]}\texpresswayId:{traffic["@expresswayId"]}\t道路種類:{roadtype}')

        ##---------路段名稱-------------###
        ##起點##
        if "端" in traffic["@from_location"] or "服務區" in traffic["@from_location"] or "休息" in traffic["@from_location"] or "站" in traffic["@from_location"]:
            start = traffic["@from_location"]
        else:
            start = traffic["@from_location"] + "交流道"
        # print(f'起點：{traffic["@from_location"]}\tstart：{start}')
        ##終點##
        if "端" in traffic["@end_location"] or "服務區" in traffic["@end_location"] or "休息" in traffic["@end_location"] or "站" in traffic["@end_location"]:
            end = traffic["@end_location"]
        else:
            end = traffic["@end_location"] + "交流道"
        # print(f'終點：{traffic["@end_location"]}\tend：{end}')
        roadsection= RoadID+ "(" +  start + "到" + end +")"
        print(f'路段名稱：{roadsection}')


        Info = ET.Element(
            'Info', {
                "routeid": "nfb" + str(traffic["@locationId"]),
                "sourceid": "nfb",
                "locationpath": "0",  # 給""會出現locationpath錯誤，推測是因為屬性
                "startlocationpoint": "0",
                "endlocationpoint": "0",
                "roadsection": str(roadsection),  #
                "roadtype": str(roadtype),  # 1為高速公路、2為非高速公路expresswayId
                "fromkm": str(traffic["@from_milepost"]), # 待改02/27
                "tokm": str(traffic["@end_milepost"]), # 待改02/27
                "speedlimit": str(traffic["@section_lower_limit"])  # 待改02/27速限
            })

        Infos.append(Info)
    tree = ET.ElementTree(root)
    tree.write(
        os.path.join(
            os.path.dirname(__file__), 'Section',
            "roadlevel_test.xml"), encoding="utf-8")

    print(f'{info["@time"]}\n合併結束，輸出檔案:roadlevel_info_0000.xml')
# os.path.dirname(os.path.abspath(__file__))
# os.path.abspath(__file__)返回的是.py檔案的絕對路徑。
