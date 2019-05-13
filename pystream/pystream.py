# -*- coding: UTF-8 -*-

import os
import re
from urllib import request
import requests
import time
import threading
import hashlib
# import m3u8
# import json
# import zlib
# from bs4 import BeautifulSoup


class MyThread (threading.Thread):

    def __init__(self, uid, url, name, path, filetype):
        threading.Thread.__init__(self)
        self.uid = uid
        self.url = url
        self.name = name
        self.path = path
        self.filetype = filetype
        self.__running = threading.Event()
        self.__running.set()

    def run(self):

        try:
            print('[INFO]正在缓存第%s号:%s 地址:%s' % (self.uid, self.name, self.url))
            filename = os.path.join(self.path, self.name + '-' +
                                    time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.' + self.filetype)
            r = requests.get(self.url, stream=True)
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
                    if not self.__running.isSet():
                        print('[INFO]第%d号:%s缓存终止,结束退出.' % (self.uid, self.name))
                        return True
            print('[INFO]第%s号%s 地址:%s缓存结束.' % (self.uid, self.name, self.url))
            return True

        except Exception as e:
            print('[INFO]第%s号%s 地址:%s缓存保存错误:%s' % (self.uid, self.name, self.url, e))
            return False

    def stop(self):
        self.__running.clear()  # 设置running为false


def stream_url_fetch(url, upjson=None, headers=None):

    if not headers['token']:
        try:
            server_url = '/'.join(url.split('/')[:-1]) + '/'
            token_data = requests.post(server_url+'user/login',
                                       json={'username': '1428579', 'password': '123456'})
            headers['token'] = token_data['data']['token']
            print('[INFO]登录成功,Token：', headers['token'])
        except Exception as e:
            print('[INFO]登录错误：', e)
            return False

    try:
        req = requests.post(url, json=upjson, headers=headers)
    except Exception as e:
        print('[INFO]%s访问失败:%s' %(url, e))
    try:
        return req.json()
    except Exception as e:
        print('[INFO]%s转JSON失败:%s' %(url, e))
        return ""


def stream_channel(url):

    channel_data = stream_url_fetch(url + 'live/index')

    channels = channel_data['data']['lists']

    return channels


def stream_get_list(data, stream_list, blackchannel, blacklist):

    m1 = hashlib.md5()
    for stream in data['data']['lists']:
        filename = stream['play_url'].split('/')[-1]
        print(filename)
        m1.update(filename.encode("utf-8"))
        uid = m1.hexdigest()
        if ((uid not in [d['uid'] for d in stream_list]) and
            (re.sub(r'\..*$|json|\W', '', stream['platform_name']) not in blackchannel) and
                (re.sub(r'\W', '', stream['title']) not in blacklist) and
                (re.sub(r'\W', '', stream['title']) not in [d['name'] for d in stream_list])):
            if re.search('.flv', stream['play_url']):
                stream_list.append({'uid': uid,
                                    'type': 'flv',
                                    'channel': re.sub(r'\..*$|json|\W', '', stream['platform_name']),
                                    'name': re.sub(r'\W', '', stream['title']),
                                    'url': stream['play_url']})
            if re.search('.m3u8', stream['play_url']):
                stream_list.append({'uid': uid,
                                    'type': '.m3u8',
                                    'channel': re.sub(r'\..*$|json|\W', '', stream['platform_name']),
                                    'name': re.sub(r'\W', '', stream['title']),
                                    'url': stream['play_url']})


def download_file(uid, url, name, path, filetype):

    try:
        print('[INFO]正在缓存%d直播:%s' % (uid, name))
        filename = os.path.join(path, name + '-' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.'+filetype)
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        print('[INFO]第%d号:%s缓存结束' % (uid, name))
        return True

    except Exception as e:
        print('[INFO]%s 地址:%s缓存保存错误:%s' % (name, url, e))
        return False


def stream_save(url, name, path):

    try:
        print('[INFO]正在缓存直播:',name)
        name = name + '-' + time.strftime("%Y%m%d%H%M%S", time.localtime())
        request.urlretrieve(url, os.path.join(path, name + '.flv'))
        print('[INFO]%s缓存结束' %name)

    except Exception as e:
        print('[INFO]%s缓存保存错误:%s' %(name, e))
        return False


def main():

    stream_path = os.path.join(os.getcwd(), 'stream')
    if not os.path.exists(stream_path):
        if not os.makedirs(stream_path):
            print('无法创建下载目录:', stream_path)
            return False

    url = 'http://jbp.qrjdfh.cn'

    stream_list = []
    threads = []
    blackchannel = ["xinzhilians"]
    with open('blacklist.txt', 'r') as f:
        blacklist = [re.sub(r'\W', '', line) for line in f.readlines()]
    token = None
    headers = {'Content-Type': 'application/json', 'token': token}

    try:
        for channel in channels:
                upjson = {'name': channel['name']}
                stream_data = stream_url_fetch(url+'live/anchors', upjson=upjson, headers=headers)
                stream_get_list(stream_data, stream_list, blackchannel, blacklist)

        for stream in stream_list:
            threads.append(MyThread(stream['uid'], stream['url'],
                                    stream['name'] + '-' + stream['channel'], stream_path, stream['type']))
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

    # print(time.strftime("%Y%m%d%H%M%S", time.localtime()))

    main()
