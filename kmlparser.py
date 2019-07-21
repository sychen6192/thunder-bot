from lxml import html
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import re
import time
import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
import requests


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


line_bot_api = LineBotApi('jAitP1FSuOrVjv1BPeQJq/29pNmbTmia0WpieEB8F4c92eunvCWYt1VCRDwmCRRV9SqmwlAnWPPU3F9UwSygL3ZqIPyp/QQAANC0ETlVfuK43aKPDoC7qG6SGIPVC5iirLc/VWbJkWcv3ay/Um5LmAdB04t89/1O/w1cDnyilFU=')
user = ""
chat_flag = 0

while True:
    url = "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/O-A0039-001?Authorization=CWB-49FDAE95-161C-4F0D-B641-0DFD42B4BEF7&downloadType=WEB&format=KMZ"
    resp = urlopen(url)
    kmz = ZipFile(BytesIO(resp.read()))

    kml = kmz.open('doc.kml', 'r').read()
    kml_unicode = kmz.open('doc.kml', 'r').read().decode('utf-8')
    doc = html.fromstring(kml)
    # print(kml_unicode)
    # print('---------------------------')
    flag = 0
    # count = 0
    for pm in doc.cssselect('Document Folder Placemark'):
        des = pm.cssselect('description')[0].text_content()
        # count = count + 1
        occur_time = str(re.findall(r"\d{2}:\d{2}", des)[0])
        latitude = str(re.findall(r"\d{3}\.?\d* ,", des)[0])
        longitude = str(re.findall(r", \d{2}\.?\d*", des)[0])
        latitude = float(latitude.strip(' ,'))
        longitude = float(longitude.strip(', '))
        # print(count, occur_time, latitude, longitude)
        if (time_diff(occur_time[0:2], occur_time[3:5])) <= 10:
            if (latitude >= 120.163 and latitude <= 120.479):
                if (longitude <= 22.647 and longitude >= 22.5882) or (longitude <= 22.5784 and longitude >=22.5):
                    flag = 1
                    chat_flag = 1
                    message = '時間： ' + occur_time + '\n經緯度：(' + str(latitude) + ' , ' + str(longitude) + ')'
                    lineNotifyMessage('\n' + message)
                    print(message)

    if flag == 0 and chat_flag == 1:
        chat_flag = 0
        message = '落雷警報解除'
        lineNotifyMessage('\n' + message)
        print(message)

    time.sleep(300)