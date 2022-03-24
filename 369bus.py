# coding:utf-8

import smtplib #smtp服务器
from email.mime.text import MIMEText #邮件文本
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
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IiIsInJvbGUiOiJWaXNpdG9yLFVzZXIiLCJuYW1laWQiOiIxMTIzNTA0IiwianRpIjoiMDRmMTE2M2EtN2YzNS00NmI2LWFlYjgtODYyM2Y3NTA1NDM5IiwibmJmIjoxNjQ3MjM0OTUwLCJleHAiOjE2NDk4MjY5NTAsImlhdCI6MTY0NzIzNDk1MCwiaXNzIjoid2ViLjM2OWN4LmNuIiwiYXVkIjoiYXBpLndlYi4zNjljeC5jbiJ9.KvC6VzTsY3Qlyyv_4PnaqIogXB5VMLmqQP9UNf8jxqzsBdZMSoQrQW7ZloB-DxIOAokhl9dU7F-Hr8UeGRP5viLDRiCE63a93M1AOKsypIFNTz6lUdehfKa_3ZTuGK-rzB6QRxGFdrNGfaSsq3eU2nPFn9LBT5FP0RPgriPmzJ2-qtX4aykuBla-3C7uZditie1DIgozsOdv0f6tYUlXFwkrFKJBKMtXo-dRK2sh12gyMSj3L6hVdG5foj-PfbxXWg2PtDn7_3M41dj9gdBpUDaHZAJQmGRM9XkswSlcGTaVdkpor17rZGzocbvWu8PthUMi7zqnzP-OgQ2xaIx_IA',
    'CityId': '2500',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.18(0x18001231) NetType/WIFI Language/zh_CN',
    'Referer': 'https://servicewechat.com/wx358ad33429ed6508/32/page-frame.html',
}

SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)

def scan(LINE, stations, SRC, DEST, dict, LINE_NAME):
    try:
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
                # print(site_time, bus['name'], src_station['name'], bus['velocity'], bus['quJian'])
            if (src_station['name'] == DEST and dict.get(key) != None):
                then = dict.pop(key)
                delta = (val - then)
                minute = int(delta / 60)
                end_time = datetime.fromtimestamp(bus['siteTime'], SHA_TZ).strftime('%H:%M:%S')
                begin_time = datetime.fromtimestamp(then, SHA_TZ).strftime('%H:%M:%S')
                # print(site_time, bus['name'], src_station['name'], bus['velocity'], bus['quJian'], minute , "m" , (delta % 60) , "s" )
                print(begin_time, end_time, bus['name'], minute, "m", (delta % 60), "s", LINE_NAME)
    except Exception as err:
        print(err)
        print("刷新", LINE_NAME, "线路信息出错")
    finally:
        return

def research(LINE, SRC, DEST, LINE1, SRC1, DEST1, start_time, end_time):

    try:
        response = requests.get('https://api.369cx.cn/v2/Line/GetRealTimeLineInfo/' + str(LINE), headers=headers)
        info = json.loads(response.text)
        stations = info['result']['stations']
        name = info['result']['name']
    except Exception as err:
        print(err)
        print("获取线路", LINE, "站点信息出错")
        exit(0)

    try:
        response = requests.get('https://api.369cx.cn/v2/Line/GetRealTimeLineInfo/' + str(LINE1), headers=headers)
        info = json.loads(response.text)
        stations1 = info['result']['stations']
        name1 = info['result']['name']
    except Exception as err:
        print(err)
        print("获取线路", LINE1, "站点信息出错")
        exit(0)

    dict_k163 = {}
    dict_308 = {}

    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    beijing_now = utc_now.astimezone(SHA_TZ).strftime("%H:%M")
    print(beijing_now)

    delta_max = (int)(5.95*60*60)
    start = time.time()

    if (0 != info['status']['code']):
        exit(0)

    while True:
        end = time.time()
        delta = (int)(end - start)
        if (delta >= delta_max):
            print("触发超时巡检退出条件，结束运行！")
            exit(0)
        if (beijing_now > end_time):
            print("正常到达结束时间，结束运行！")
            exit(0)
        if (start_time > beijing_now):
            time.sleep(10)
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
            beijing_now = utc_now.astimezone(SHA_TZ).strftime("%H:%M")
            continue
        else:
            try:
                begin = time.time()

                scan(LINE, stations, SRC, DEST, dict_k163, name)
                scan(LINE1, stations1, SRC1, DEST1, dict_308, name1)

                end = time.time()
                sleep_times = begin + 10.0 - end
                if (sleep_times <= 0.0):
                    sleep_times = 9.5
                time.sleep(sleep_times)
                utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
                beijing_now = utc_now.astimezone(SHA_TZ).strftime("%H:%M")
            except Exception as err:
                print(err)
                time.sleep(9.5)

def sendEmail(title, content):
    mail_user = "soyounsowhat@163.com"#接收方
    recver = "soyounsowhat@163.com"#接收方
    mail_pass = "ZBPCIYOFQTOUBNGT"#邮箱密码
    sender = "soyounsowhat@163.com"#接收方
    receivers = ["soyounsowhat@163.com"]
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    mail_host = "smtp.163.com"

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 994)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
    except smtplib.SMTPException as e:
        print(e)

if __name__ == '__main__':

    _LINE = sys.argv[1]
    _SRC = sys.argv[2]
    _DEST = sys.argv[3]

    _LINE1 = sys.argv[4]
    _SRC1 = sys.argv[5]
    _DEST1 = sys.argv[6]

    _start_time = sys.argv[7]
    _end_time = sys.argv[8]

    sendEmail("hi", "hello world!" + _LINE + _SRC + _DEST + _LINE1 + _SRC1 + _DEST1 + _start_time + _end_time)
    
    print(_LINE, _SRC, _DEST, _LINE1, _SRC1, _DEST1, _start_time, _end_time)
    research(_LINE, _SRC, _DEST, _LINE1, _SRC1, _DEST1, _start_time, _end_time)
