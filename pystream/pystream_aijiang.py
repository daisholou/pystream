# -*- coding: UTF-8 -*-

import os
import re
from urllib import request
import requests
import time
import threading
from functools import reduce
from itertools import chain
# import m3u8
# import json
# import zlib
# from bs4 import BeautifulSoup


class MyThread (threading.Thread):

    def __init__(self, id, url, name, path, filetype):
        threading.Thread.__init__(self)
        self.id = id
        self.url = url
        self.name = name
        self.path = path
        self.filetype = filetype
        self.__running = threading.Event()
        self.__running.set()

    def run(self):

        try:
            print('[INFO]正在缓存第%d号:%s 地址:%s' % (self.id, self.name, self.url))
            filename = os.path.join(self.path, self.name + '-' +
                                    time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.' + self.filetype)
            r = requests.get(self.url, stream=True)
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
                    if not self.__running.isSet():
                        print('[INFO]第%d号:%s缓存终止,结束退出.' % (self.id, self.name))
                        return True
            print('[INFO]第%d号%s 地址:%s缓存结束.' % (self.id, self.name, self.url))
            return True

        except Exception as e:
            print('[INFO]第%d号%s 地址:%s缓存保存错误:%s' % (self.id, self.name, self.url, e))
            return False

    def stop(self):
        self.__running.clear()  # 设置running为false


def stream_url_fetch(url, data=None, upjson=None, headers=None):

    try:
        if headers:
            req = requests.post(url, data=data, json=upjson, headers=headers)
        else:
            req = requests.post(url, data=data, json=upjson)

    except Exception as e:
        print('[INFO]%s访问失败:%s' % (url, e))
    try:
        return req.json()
    except Exception as e:
        print('[INFO]%s转JSON失败:%s' % (url, e))
        return ""


def stream_save(id, url, name, path):

    try:
        print('[INFO]正在缓存%d直播:%s' % (id, name))
        filename = os.path.join(path, name + '-' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.flv')
        request.urlretrieve(url, filename)
        print('[INFO]第%d号:%s缓存结束' % (id, name))

    except Exception as e:
        print('[INFO]%s 地址:%s缓存保存错误:%s' % (name, url, e))
        return False


def download_file(id, url, name, path, filetype):

    try:
        print('[INFO]正在缓存%d直播:%s' % (id, name))
        filename = os.path.join(path, name + '-' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.'+filetype)
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        print('[INFO]第%d号:%s缓存结束' % (id, name))
        return True

    except Exception as e:
        print('[INFO]%s 地址:%s缓存保存错误:%s' % (name, url, e))
        return False


def main():

    stream_path = '/Users/Lou/python/works/pystream/stream/'
    if not os.path.exists(stream_path):
        if not os.makedirs(stream_path):
            print('无法创建下载目录:', stream_path)
            return False

    url = 'http://www.5588.cool/mobile/live/get_all_auto_proposed_anchors'
    stream_list = []
    threads = []
    blackchannel = ["xinzhilians"]

    # 读取黑名单
    with open('blacklist.txt', 'r') as f:
        blacklist = [re.sub(r'\W', '', line) for line in f.readlines()]

    try:
        streams_data = stream_url_fetch(url)
        streams = streams_data['data']['lists']
        i = 1

        for stream in streams:
            if ((re.sub(r'\..*$|json|\W', '', stream['platform_name']) not in blackchannel) and
                    (re.sub(r'\W', '', stream['title']) not in blacklist) and
                    (stream['play_url'] not in [d['url'] for d in stream_list]) and
                    (re.sub(r'\W', '', stream['title']) not in [d['name'] for d in stream_list])):
                if re.search('.flv', stream['play_url']):
                    stream_list.append({'id': i,
                                        'type': 'flv',
                                        'channel': re.sub(r'\..*$|json|\W', '', stream['platform_name']),
                                        'name': re.sub(r'\W', '', stream['title']),
                                        'url': stream['play_url']})
                if re.search('.m3u8', stream['play_url']):
                    stream_list.append({'id': i,
                                        'type': 'mp4',
                                        'channel': re.sub(r'\..*$|json|\W', '', stream['platform_name']),
                                        'name': re.sub(r'\W', '', stream['title']),
                                        'url': stream['play_url']})
                i += 1

        for stream_f in stream_list:
            threads.append(MyThread(stream_f['id'], stream_f['url'],
                                    stream_f['name'] + '-' + stream_f['channel'], stream_path, stream_f['type']))
        print(len(threads))
        for t in threads:
            t.start()

        count = threading.active_count()
        while count > 1:
            if not count == threading.active_count():
                count = threading.active_count()
                print(time.strftime("现在是:%Y%m%d %H:%M:%S", time.localtime()), '仍在缓存直播数:', count)
                print([myT.name for myT in threading.enumerate()])
            time.sleep(10)

    except Exception as e:
        print('获取列表数据错误：', e)
        return False

    finally:
        active_threads = threads
        while len(active_threads) > 0:
            for t in active_threads:
                if t.is_alive():
                    t.stop()
                else:
                    active_threads.remove(t)
            print('仍在缓存直播:')
            print([(myT.id, myT.name) for myT in active_threads])
            time.sleep(10)
        time.sleep(50)


if __name__ == '__main__':

    main()
