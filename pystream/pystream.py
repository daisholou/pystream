# -*- coding: UTF-8 -*-

import os
import re
import requests
import time
import threading
import hashlib
from urllib.parse import urljoin
# from urllib import request
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

            if self.filetype == 'm3u8':

                print(self.url)
                r = requests.get(self.url)
                if r.ok:
                    body = r.content.decode()
                    print('第一层:', body)
                    if "#EXTM3U" not in body:
                        raise BaseException("非M3U8的链接")

                    if "EXT-X-STREAM-INF" in body:  # 第一层
                        file_line = body.split("\n")
                        for line in file_line:
                            if '.m3u8' in line:
                                self.url = self.url.rsplit("/", 1)[0] + "/" + line  # 拼出第二层m3u8的URL

                    content = requests.get(self.url).text
                    rint('第二层:', content)
                    if content:
                        ts_list = [urljoin(self.url, n.strip()) for n in body.split('\n') if
                                   n and not n.startswith("#")]
                        len_ts_list = len(ts_list)
                        ts_list = zip(ts_list, [n for n in range(len_ts_list)])
                        print(ts_list)
            else:
                return False

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
            print('[ERR]第%d号%s 地址:%s缓存保存错误:%s' % (self.id, self.name, self.url, e))
            return False

    def stop(self):
        self.__running.clear()  # 设置running为false


def stream_url_fetch(url, upjson=None, headers=None):

    if not headers['token']:
        try:
            server_url = '/'.join(url.split('/')[:-1]) + '/'
            token_data = requests.post(server_url+'mobile/user/login',
                                       json={'username': '1428579', 'password': '123456'})
            headers['token'] = token_data['data']['token']
            print('[INFO]登录成功,Token：', headers['token'])
        except Exception as e:
            print('[ERR]登录错误：', e)
            return ""

    try:
        req = requests.post(url, json=upjson, headers=headers)
    except Exception as e:
        print('[ERR]%s访问失败:%s' %(url, e))
    try:
        return req.json()
    except Exception as e:
        print('[ERR]%s转JSON失败:%s' %(url, e))
        return ""


def stream_channel(url):

    channel_data = stream_url_fetch(url + 'mobile/live/index')

    channels = channel_data['data']['lists']

    return channels


def stream_get_list(data, platform, stream_list, blackchannel, blacklist):

    m1 = hashlib.md5()
    for stream in data['data']['lists']:
        filename = stream['play_url'].split('/')[-1]
        filename = filename.split('?')[0]
        filetype = filename.split('.')[-1]
        title = re.sub(r'\W', '', stream['title'])
        m1.update(filename.encode("utf-8"))
        uid = m1.hexdigest()

        if ((uid not in [d['uid'] for d in stream_list]) and
            (platform not in blackchannel) and
                (title not in blacklist) and
                (title not in [d['name'] for d in stream_list])):
            stream_list.append({'id': len(stream_list)+1,
                                'uid': uid,
                                'type': filetype,
                                'platform': platform,
                                'name': title,
                                'url': stream['play_url']})


# def download_file(id, url, name, path, filetype):
#
#     try:
#         print('[INFO]正在缓存%d直播:%s' % (id, name))
#         filename = os.path.join(path, name + '-' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.'+filetype)
#         r = requests.get(url, stream=True)
#         with open(filename, 'wb') as f:
#             for chunk in r.iter_content(chunk_size=1024):
#                 if chunk:  # filter out keep-alive new chunks
#                     f.write(chunk)
#                     f.flush()
#         print('[INFO]第%d号:%s缓存结束' % (id, name))
#         return True
#
#     except Exception as e:
#         print('[INFO]%s 地址:%s缓存保存错误:%s' % (name, url, e))
#         return False
#
#
# def stream_save(id, url, name, path):
#
#     try:
#         print('[INFO]正在缓存%d直播:%s' % (id, name))
#         filename = os.path.join(path, name + '-' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.flv')
#         request.urlretrieve(url, filename)
#         print('[INFO]第%d号:%s缓存结束' % (id, name))
#
#     except Exception as e:
#         print('[ERR]%s 地址:%s缓存保存错误:%s' % (name, url, e))
#         return False


def main():

    stream_path = os.path.join(os.getcwd(), 'stream')
    if not os.path.exists(stream_path):
        if not os.makedirs(stream_path):
            print('[ERR]无法创建下载目录:', stream_path)
            return False

    url = 'http://jbp.qrjdfh.cn/'

    stream_list = []
    threads = []

    # 获取黑名单
    blackchannel = ["xinzhilians"]

    with open('blacklist.txt', 'r',encoding='utf-8') as f:
        blacklist = [re.sub(r'\W', '', line) for line in f.readlines()]

    # 设置token
    token = '18bccf560c88fb5c90895ea18c329076'
    headers = {'Content-Type': 'application/json', 'token': token}

    try:

        channel_data = stream_url_fetch(url + 'mobile/live/index', headers=headers)

        if channel_data:
            channels = channel_data['data']['lists']
        else:
            print('[ERR]无法获取列表数据!')
            return False
        channels = list(set(channels))
        print(channels)

        for channel in channels:
                upjson = {'name': channel['name']}
                platform = re.sub(r'\..*$|json|\W', '', channel['name'])
                stream_data = stream_url_fetch(url+'mobile/live/anchors', upjson=upjson, headers=headers)
                stream_get_list(stream_data, platform, stream_list, blackchannel, blacklist)

        for stream in stream_list:
            threads.append(MyThread(stream['id'], stream['url'],
                                    stream['name'] + '-' + stream['platform'], stream_path, stream['type']))
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

    # except Exception as e:
    #     print('获取列表数据错误：', e)
    #     return False

    finally:
        active_threads = threads
        while len(active_threads) > 0:
            for t in active_threads:
                if t.is_alive():
                    t.stop()
                else:
                    active_threads.remove(t)
            print('[INFO]仍在缓存直播:')
            print([(myT.id, myT.name) for myT in active_threads])
            time.sleep(10)
        time.sleep(50)


if __name__ == '__main__':

    # print(time.strftime("%Y%m%d%H%M%S", time.localtime()))

    main()
