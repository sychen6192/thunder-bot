from lxml import html
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import re
import time
import datetime
import requests
import sys
import logging

pre = time.strftime('%Y-%m-%d %H-%M-%S')
# 基礎設定
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[logging.FileHandler('./log/'+pre+'.log', 'w', 'utf-8'), ])

# 定義 handler 輸出 sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# 設定輸出格式
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# handler 設定輸出格式
console.setFormatter(formatter)
# 加入 hander 到 root logger
logging.getLogger('').addHandler(console)


def area(top, down, left, right, longitude, latitude):
    if longitude >= left and longitude <= right:
        if latitude <= top and latitude >= down:
            return True
        else:
            return False
    else:
        return False


def thunder(longitude, latitude):
    # res = requests.get('https://www.cwb.gov.tw/V7/js/Lightning.js')
    # soup = BeautifulSoup(res.text, 'html.parser')
    # string = str(soup)
    # web = "https://www.cwb.gov.tw" + string[19:74]
    longitude = str(longitude)
    latitude = str(latitude)
    web = "https://www.google.com/maps?q="+longitude+","+latitude
    return web


def lineNotifyMessage(msg):
    headers = {
        "Authorization": "Bearer " + 'sHnrYJ4dWEs6UGYUV5h7tayXg3noEIpxzaZb1IN7dRe',
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code


def time_diff(occ_hour, occ_min):
    occ_hour = int(occ_hour)
    occ_min = int(occ_min)
    now_time = datetime.datetime.now()
    if now_time.hour-occ_hour == -23:
        diff = 60 + (now_time.minute-occ_min)
    else:
        diff = (now_time.hour-occ_hour) * 60 + (now_time.minute-occ_min)

    return diff


chat_flag = 0
alert_list = []

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
            latitude = float(str(re.findall(r"\d{3}\.?\d* ,", des)[0]).strip(' ,'))
            longitude = float(str(re.findall(r", \d{2}\.?\d*", des)[0]).strip(', '))
            latitude_str = str(latitude)
            longitude_str = str(longitude)
            if (time_diff(occur_time[0:2], occur_time[3:5])) <= 10:
                # 給台北定位
                if area(25.2, 25, 120.4, 121.730570, longitude, latitude):
                    if longitude_str+','+latitude_str not in alert_list:
                        flag = 1
                        chat_flag = 1
                        message = '時間： ' + occur_time + '\n經緯度：(' + latitude_str + ' , ' + longitude_str + ')' + '\n' + thunder(longitude, latitude)
                        lineNotifyMessage('\n' + message)
                        alert_list.append(longitude_str+','+latitude_str)
                        logging.warning(message)

        if flag == 0 and chat_flag == 1:
            chat_flag = 0
            message = '區域內落雷警報解除!'
            alert_list = []
            lineNotifyMessage('\n' + message)
            logging.warning(message)
        elif flag == 0 and chat_flag == 0:
            message = '區域內無落雷!'
            logging.info(message)

        time.sleep(60)
    except:
        message = "Unexpected error:", sys.exc_info()[0]
        logging.error(message)
        time.sleep(10)

