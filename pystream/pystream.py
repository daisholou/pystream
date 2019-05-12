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


def stream_url_fetch(url, data=None, upjson=None, headers=None):

    try:
        if headers:
            req = requests.post(url, data=data, json=upjson, headers=headers)
        else:
            req = requests.post(url, data=data, json=upjson)

    except Exception as e:
        print('[INFO]%s访问失败:%s' %(url, e))
    try:
        return req.json()
    except Exception as e:
        print('[INFO]%s转JSON失败:%s' %(url, e))
        return ""


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

    stream_path = '/Users/Lou/python/works/pystream/stream/'
    if not os.path.exists(stream_path):
        if not os.makedirs(stream_path):
            print('无法创建下载目录:', stream_path)
            return False

    url = 'http://www.5588.cool/mobile/live/get_all_auto_proposed_anchors'
    stream_m3u8_list = []
    stream_flv_list = []
    threads = []
    token = None
    # token = '921bfc04cd1adfc6cab7957a9275260f'
    if not token:
        try:
            token_data = stream_url_fetch(url+'user/login', upjson={'username': '1428579', 'password': '123456'})
            token = token_data['data']['token']
            print(token)
        except Exception as e:
            print('登录错误：', e)
            return False

    # print ({'token': token})
    headers = {'Content-Type': 'application/json', 'token': token}
    try:
        channel_data = stream_url_fetch(url+'live/index')
        channels = channel_data['data']['lists']

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
