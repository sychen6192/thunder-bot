from lxml import html
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import re
import time
import datetime
import requests
import sys
from bs4 import BeautifulSoup
import logging

# 基礎設定
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[logging.FileHandler('output.log', 'w', 'utf-8'), ])

# 定義 handler 輸出 sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# 設定輸出格式
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# handler 設定輸出格式
console.setFormatter(formatter)
# 加入 hander 到 root logger
logging.getLogger('').addHandler(console)


def thunder():
    res = requests.get('https://www.cwb.gov.tw/V7/js/Lightning.js')
    soup = BeautifulSoup(res.text, 'html.parser')
    string = str(soup)
    web = "https://www.cwb.gov.tw" + string[19:74]
    return web


def lineNotifyMessage(msg):
    headers = {
        "Authorization": "Bearer " + 'Agyvt1uyJHomBikja7brcZRi4dDmGH84WZYDavV9XnQ',
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code


def time_diff(occ_hour, occ_min):
    occ_hour = int(occ_hour)
    occ_min = int(occ_min)
    now_time = datetime.datetime.now()
    diff = (now_time.hour-occ_hour) * 60 + (now_time.minute-occ_min)
    return diff


chat_flag = 0

while True:
    try:
        url = "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/O-A0039-001?Authorization=CWB-49FDAE95-161C-4F0D-B641-0DFD42B4BEF7&downloadType=WEB&format=KMZ"
        resp = urlopen(url)
        kmz = ZipFile(BytesIO(resp.read()))

        kml = kmz.open('doc.kml', 'r').read()
        kml_unicode = kmz.open('doc.kml', 'r').read().decode('utf-8')
        doc = html.fromstring(kml)
        # print(kml_unicode)
        # print('---------------------------')
        flag = 0
        for pm in doc.cssselect('Document Folder Placemark'):
            des = pm.cssselect('description')[0].text_content()
            occur_time = str(re.findall(r"\d{2}:\d{2}", des)[0])
            latitude = str(re.findall(r"\d{3}\.?\d* ,", des)[0])
            longitude = str(re.findall(r", \d{2}\.?\d*", des)[0])
            latitude = float(latitude.strip(' ,'))
            longitude = float(longitude.strip(', '))
            if (time_diff(occur_time[0:2], occur_time[3:5])) <= 10:
                if (latitude >= 120.163 and latitude <= 120.479):
                    if (longitude <= 22.647 and longitude >= 22.5882) or (longitude <= 22.5784 and longitude >=22.5):
                        flag = 1
                        chat_flag = 1
                        message = '時間： ' + occur_time + '\n經緯度：(' + str(latitude) + ' , ' + str(longitude) + ')' + '\n' + thunder()
                        lineNotifyMessage('\n' + message)
                        # print(datetime.datetime.now(), message)
                        logging.warning(message)

        if flag == 0 and chat_flag == 1:
            chat_flag = 0
            message = '指定區域內落雷警報解除!'
            lineNotifyMessage('\n' + message)
            # print(datetime.datetime.now(), message)
            logging.warning(message)
        elif flag == 0 and chat_flag == 0:
            message = '指定區域內無落雷!'
            # print(datetime.datetime.now(), message)
            logging.info(message)

        time.sleep(150)
    except:
        message = "Unexpected error:", sys.exc_info()[0]
        # print(message)
        logging.error(message)
        time.sleep(10)