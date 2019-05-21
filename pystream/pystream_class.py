# -*- coding: UTF-8 -*-

import requests
import re
import cv2

from urllib.parse import urlparse


class Box(object):
    def __init__(self, url, token=None, *args, **kwargs):
        self.url = get_base_url(url)
        if token:
            self.token = token
        else:
            self.token = self._token()

        self.headers = {'Content-Type': 'application/json', 'token': self.token}

    def channel(self):
        channel_data = self.url_fetch(self.url + '/mobile/live/index')
        try:
            return channel_data['data']['lists']
        except Exception as e:
            print('[ERR]无法获取频道数据：', e)
            return None

    def list(self, channel):
        ch_json = {'name': channel}
        stream_data = self.url_fetch(self.url + '/mobile/live/anchors', json=ch_json)
        try:
            streams = {}
            for stream in stream_data['data']['lists']:
                title = re.sub(r'\W', '', stream['title'])
                streams[title] = stream
                streams[title]['pic'] = '/static/'+channel+'/'+title+'.jpg'
                self._capture(url=stream['play_url'], path=streams[title]['pic'])

            return streams
        except Exception as e:
            print('[ERR]无法获取列表数据：', e)
            return None

    def _capture(self, url, path):
        if url:
            if path:
                imgpath = os.path.join(os.getcwd(), path)
                if not os.path.exists(imgpath):
                    if not os.makedirs(imgpath):
                        print('[ERR]无法创建下载目录:', imgpath)
                        return False
                vidcap = cv2.VideoCapture(url)
                success, image = vidcap.read()
                if success:
                    cv2.imwrite(path, image)   # save frame as JPEG file
                    return True
        return False

    def _token(self):
        try:
            req = requests.post(self.url + '/mobile/user/login',
                                         json={'username': '1428579', 'password': '123456'})
            token_data = req.json()
            print('[INFO]登录成功,Token：', token_data['data']['token'])
            return token_data['data']['token']
        except Exception as e:
            print('[ERR]登录错误：', e)
            return None

    def url_fetch(self, url, json=None):
        try:
            if self.token:
                req = requests.post(url, json=json, headers=self.headers)
            else:
                req = requests.post(url, json=json)
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
