#!/usr/bin/env python3
# coding: utf-8
# Create by : https://github.com/Luke9570/ServerStatus-L
# 版本：0.1.0, 支持Python版本：2.7 to 3.9
# 支持操作系统： Linux, OSX, FreeBSD, OpenBSD and NetBSD, both 32-bit and 64-bit architectures

import requests
import time
import threading
import traceback

NODE_STATUS_URL = 'http://serverstatus/json/stats.json'
CHAT_ID = os.getenv('TG_CHAT_ID')
BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
NOTIFY_INTERVAL = os.getenv('NOTIFY_INTERVAL')  # 离线节点通知间隔，单位为秒
offline_servers = []
online_servers = {}
temp_status = {}

def send_telegram_message(text):
    # 发送Telegram消息
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        print(url, params)
        requests.get(url, params=params)
    except Exception as e:
        print("catch exception: ", traceback.format_exc())


def notify_server_status(server_name, status):
    if status == "online":
        if server_name in offline_servers:
            offline_servers.remove(server_name)
            online_servers[server_name] = 0
            text = '<b>Server Status</b>' + '\n主机上线: ' + server_name
            print(text)
            send_telegram_message(text)
        elif server_name in temp_status:
            del temp_status[server_name]
        else:
            return
    else:
        if server_name in offline_servers:
            return
        elif server_name in temp_status and (datetime.datetime.now() - temp_status[server_name]).seconds >= NOTIFY_INTERVAL:
            offline_servers.append(server_name)
            online_servers.pop(server_name, None)
            temp_status.pop(server_name, None)
            text = '<b>Server Status</b>' + '\n主机下线: ' + server_name
            print(text)
            send_telegram_message(text)
        elif server_name in temp_status:
            pass
        else:
            temp_status[server_name] = datetime.datetime.now()

def check_server_status(address):
    while True:
        r = requests.get(url=address, headers={"User-Agent": "ServerStatus/20211116"})
        try:
            jsonR = r.json()
        except Exception as e:
            print('未发现任何节点')
            continue
        for server in jsonR["servers"]:
            if not server["online4"] and not server["online6"]:
                notify_server_status(server["name"], "offline")
            else:
                notify_server_status(server["name"], "online")
        time.sleep(3)

if __name__ == '__main__':
    check_server_status(NODE_STATUS_URL)
