# -*- coding: UTF-8 -*-

import os
import re
from urllib import request
import requests
import time
import threading
# import m3u8
# import json
# import zlib
# from bs4 import BeautifulSoup


class MyThread (threading.Thread):

    def __init__(self, url, name, path):
        threading.Thread.__init__(self)
        self.url = url
        self.name = name
        self.path = path

    def run(self):
        stream_save(self.url, self.name, self.path)


def stream_url_fetch(url, headers=None):

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
        req = requests.post(url,  headers=headers)
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


def stream_list(stream_data):

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
                                    'type': '.m3u8',
                                    'channel': re.sub(r'\..*$|json|\W', '', stream['platform_name']),
                                    'name': re.sub(r'\W', '', stream['title']),
                                    'url': stream['play_url']})
            i += 1




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
    stream_m3u8_list = []
    stream_flv_list = []
    threads = []
    token = None
    headers = {'Content-Type': 'application/json', 'token': token}

    try:


        for channel in channels:
            if channel['name'] == 'zzzzjsontubaobao.txt':
                upjson = {'name': channel['name']}
                stream_data = stream_url_fetch(url+'live/anchors', upjson=upjson, headers=headers)
                for stream in stream_data['data']['lists']:
                    if re.search('.flv', stream['play_url']):
                        stream_flv_list.append({'channel': channel['title'],
                                            'name': stream['title'],
                                            'url': stream['play_url']})
                    if re.search('.m3u8', stream['play_url']):
                        stream_m3u8_list.append({'channel': channel['title'],
                                            'name': stream['title'],
                                            'url': stream['play_url']})

        # threads = [MyThread() for i in range(stream_flv_list.count)]
        #
        # for t in threads:
        #     t.url  = stream_save(stream_f['url'], stream_f['channel']+'-'+stream_f['name'], stream_path)
        #     t.name =
        #     t.path =

        for stream_f in stream_flv_list:
            threads.append(MyThread(stream_f['url'], stream_f['channel'] + '-' + stream_f['name'], stream_path))
        for t in threads:
            t.start()
        # t.join()

        # for stream_m in stream_m3u8_list:
        #     stream = m3u8.Downloader(10)
        #     stream.run(stream_m['url'], stream_path+'m3u8/')

    except Exception as e:
        print('获取列表数据错误：', e)
        return False


if __name__ == '__main__':

    # print(time.strftime("%Y%m%d%H%M%S", time.localtime()))

    main()
