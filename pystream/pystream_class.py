# -*- coding: UTF-8 -*-

import requests
import re
import cv2
import configparser
import time
import os

from urllib.parse import urlparse


class Box(object):
    def __init__(self, *args, **kwargs):

        cf = configparser.ConfigParser()
        cf.read("config.conf")
        self.url = cf.get("main", "url")
        self.user = cf.get("main", "name")
        self.password = cf.get("main", "passwd")
        self.headers = None
        if self.url:
            self.url = get_base_url(self.url)
        else:
            print('[ERR]没有网址!')

            return False

        if cf.has_option("main", "token"):
            self.token = cf.get("main", "token")
            self.extime = cf.getint("main", "expiredtime")
            if self.extime > time.time():
                self.headers = {'Content-Type': 'application/json', 'token': self.token}
        if self.user and self.password and not self.headers:
            self.token = self._token()
            self.extime = time.time()+3600*24
            self.headers = {'Content-Type': 'application/json', 'token': self.token}
            cf.set("main", "token", self.token)
            cf.set("main", "expiredtime", "%d" % self.extime)
            with open('config.conf', 'w') as configfile:
                cf.write(configfile)
        if not self.headers:
            print('[ERR]无法登陆!')
            return False

    def channel(self):
        channel_data = self.url_fetch(self.url + '/mobile/live/index')
        try:
            return channel_data['data']['lists']
        except Exception as e:
            print('[ERR]无法获取频道数据：', e)
            return None

    def list(self, channel):
        ch_json = {'name': channel['json']}
        stream_data = self.url_fetch(self.url + '/mobile/live/anchors', json=ch_json)
        try:
            streams = {}
            for stream in stream_data['data']['lists']:
                title = re.sub(r'\W', '', stream['title'])
                streams[title] = stream
                streams[title]['pic'] = 'static/'+channel['name']+'/'+title+'.jpg'
                self._capture(url=stream['play_url'], path=streams[title]['pic'])

            return streams
        except Exception as e:
            print('[ERR]无法获取列表数据：', e)
            return None

    def _capture(self, url, path):
        if url:
            if path:
                imgpath = os.path.join(os.getcwd(), path)
                if not os.path.exists(os.path.dirname(imgpath)):
                    if not os.makedirs(os.path.dirname(imgpath)):
                        print('[ERR]无法创建下载目录:', imgpath)
                        return False
                vidcap = cv2.VideoCapture(url)
                success, image = vidcap.read()
                if success:
                    cv2.imwrite(imgpath, image)   # save frame as JPEG file
                    return True
        return False

    def _token(self):
        try:
            req = requests.post(self.url + '/mobile/user/login',
                                         json={'username': self.user, 'password': self.password})
            token_data = req.json()
            print('[INFO]登录成功,Token：', token_data['data']['token'])
            return token_data['data']['token']
        except Exception as e:
            print('[ERR]登录错误：', e)
            return None

    def url_fetch(self, url, json=None):
        try:
            req = requests.post(url, json=json, headers=self.headers)
        except Exception as e:
            print('[ERR]%s访问失败:%s' % (url, e))
        try:
            return req.json()
        except Exception as e:
            print('[ERR]%s的%s转JSON失败:%s' % (url, req, e))
            return None


def get_base_url(url):
    uri = urlparse(url)
    return uri.scheme + '://' + uri.netloc
