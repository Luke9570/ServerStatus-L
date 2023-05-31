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


def notify_node_status(srv, flag, offline_nodes, offline_counter, online_counter, temp_status):
    # 处理节点上下线通知
    if srv not in offline_counter:
        offline_counter[srv] = 0
    if srv not in online_counter:
        online_counter[srv] = 0

    if flag == 1:  # 节点上线
        if srv in offline_nodes:
            if online_counter[srv] < 3:
                online_counter[srv] += 1
                return
            # 将节点从离线列表中移除，并发送上线通知
            offline_nodes.remove(srv)
            online_counter[srv] = 0
            text = '<b>Server Status</b>\n主机上线：' + srv
            print(text)
            send_telegram_message(text)
        elif srv in temp_status:
            del temp_status[srv]
            online_counter[srv] = 0
        else:
            return

    else:  # 节点离线
        if srv in offline_nodes:
            return
        elif srv in temp_status and temp_status[srv] >= NOTIFY_INTERVAL:
            # 将节点添加到离线列表中，并发送离线通知
            offline_nodes.add(srv)
            offline_counter[srv] = 0
            del temp_status[srv]
            text = '<b>Server Status</b>\n主机离线：' + srv
            print(text)
            send_telegram_message(text)
        elif srv in temp_status and temp_status[srv] < NOTIFY_INTERVAL:
            temp_status[srv] += 1
        else:
            temp_status[srv] = 0


def check_node_status(address, offline_nodes, offline_counter, online_counter, temp_status):
    # 检查节点状态
    try:
        r = requests.get(url=address, headers={"User-Agent": "ServerStatus/20211116"})
        r.raise_for_status()
        jsonR = r.json()
    except requests.exceptions.RequestException as e:
        print(f"请求节点状态失败：{e}")
        time.sleep(10)
        return
    except ValueError as e:
        print(f"解析节点状态失败：{e}")
        time.sleep(10)
        return
    for i in jsonR["servers"]:
        if not i["online4"] and not i["online6"]:
            notify_node_status(i["name"], 0, offline_nodes, offline_counter, online_counter, temp_status)
        else:
            notify_node_status(i["name"], 1, offline_nodes, offline_counter, online_counter, temp_status)


def run_check_node_status():
    # 多线程执行检查节点状态
    offline_nodes = set()
    offline_counter = {}
    online_counter = {}
    temp_status = {}
    while True:
        check_node_status(NODE_STATUS_URL, offline_nodes, offline_counter, online_counter, temp_status)


if __name__ == '__main__':
    threading.Timer(3, run_check_node_status).start()
