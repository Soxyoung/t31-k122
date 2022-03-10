# coding:utf-8
import requests
import json
from datetime import datetime
import time
from datetime import timedelta
from datetime import timezone
import sys

headers = {
    'Host': 'api.369cx.cn',
    'content-type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IiIsInJvbGUiOiJWaXNpdG9yLFVzZXIiLCJuYW1laWQiOiI4NzEyODkiLCJqdGkiOiI4YmE4ZGI3OC02ZGM3LTQzYjYtYThkNi1hYTFhZTAxNDNiN2UiLCJuYmYiOjE2NDYzOTY1NzYsImV4cCI6MTY0ODk4ODU3NiwiaWF0IjoxNjQ2Mzk2NTc2LCJpc3MiOiJ3ZWIuMzY5Y3guY24iLCJhdWQiOiJhcGkud2ViLjM2OWN4LmNuIn0.NqbGCiV18il_oyj9AeT7K-6R6C58hBRjADjbH9PntkxYuvbEDfSjNZEIOZ5BT5jH9Ff6UoE-QGDiiZm0u8EoM3gNVMLGXxBMaMVYRb6l5IPxGq3B36AR1PUoMbnXZnmUufqMI5QGuQpPoat3hwN5apVDXPRm8EIch97SaHGqErW0yUWXEWf6mAZsik7L0soCumkFCNN2HFxxf7bGLuK8APfXKYa7m5J50eAsIgSdko2DzyQMza242ABpSmHXUCHVSPev_AGfxIoNa-m7y23k5gsefsVBgvcftRIojX4bavtoHBKtLbVdobBKN1NkQzhQApu9jV0wKpyFZOBM36guYw',
    'CityId': '2500',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.18(0x18001231) NetType/WIFI Language/zh_CN',
    'Referer': 'https://servicewechat.com/wx358ad33429ed6508/32/page-frame.html',
}

SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)

def scan(LINE, stations, SRC, DEST, dict):
    response = requests.get('https://api.369cx.cn/v2/Bus/GetBussesByLineId/' + str(LINE), headers=headers)
    info = json.loads(response.text)
    result = info['result']
    for bus in result:
        no = bus['stationNo']
        src_station = stations[no]
        key = bus['name']
        val = bus['siteTime']
        if (src_station['name'] == SRC and dict.get(key) == None):
            dict[key] = val
            site_time = datetime.fromtimestamp(bus['siteTime'], SHA_TZ).strftime('%H:%M:%S')
            print(site_time, bus['name'], src_station['name'], bus['velocity'], bus['quJian'])
        if (src_station['name'] == DEST and dict.get(key) != None):
            then = dict.pop(key)
            delta = (val - then)
            minute = int( delta / 60)
            site_time = datetime.fromtimestamp(bus['siteTime'], SHA_TZ).strftime('%H:%M:%S')
            print(site_time, bus['name'], src_station['name'], bus['velocity'], bus['quJian'], minute , "m" , (delta % 60) , "s" )

def research(LINE, SRC, DEST, LINE1, SRC1, DEST1, start_time, end_time):

    response = requests.get('https://api.369cx.cn/v2/Line/GetRealTimeLineInfo/' + str(LINE), headers=headers)
    info = json.loads(response.text)
    stations = info['result']['stations']

    response = requests.get('https://api.369cx.cn/v2/Line/GetRealTimeLineInfo/' + str(LINE1), headers=headers)
    info = json.loads(response.text)
    stations1 = info['result']['stations']

    dict_k163 = {}
    dict_308 = {}

    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    beijing_now = utc_now.astimezone(SHA_TZ).strftime("%H:%M")
    print(beijing_now)
#     print("-------------------------------------------------")
#     print(LINE, SRC, DEST, stations)
#     print("-------------------------------------------------")
#     print(LINE1, SRC1, DEST1, stations1)
#     print("-------------------------------------------------")

    if (0 != info['status']['code']):
        exit(0)

    while True:

        if (beijing_now > end_time):
            break
        if (start_time > beijing_now):
            time.sleep(10)
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
            beijing_now = utc_now.astimezone(SHA_TZ).strftime("%H:%M")
            continue
        else:
            begin = time.time()

            scan(LINE, stations, SRC, DEST, dict_k163)
            scan(LINE1, stations1, SRC1, DEST1, dict_308)

            end = time.time()
            sleep_times = begin + 10.0 - end
            if (sleep_times <= 0.0):
                sleep_times = 9.5
            time.sleep(sleep_times)
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
            beijing_now = utc_now.astimezone(SHA_TZ).strftime("%H:%M")

if __name__ == '__main__':

    _LINE = sys.argv[1]
    _SRC = sys.argv[2]
    _DEST = sys.argv[3]

    _LINE1 = sys.argv[4]
    _SRC1 = sys.argv[5]
    _DEST1 = sys.argv[6]

    _start_time = sys.argv[7]
    _end_time = sys.argv[8]

    print(_LINE, _SRC, _DEST, _LINE1, _SRC1, _DEST1, _start_time, _end_time)
    research(_LINE, _SRC, _DEST, _LINE1, _SRC1, _DEST1, _start_time, _end_time)
