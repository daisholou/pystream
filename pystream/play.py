# -*- coding: UTF-8 -*-

# import cv2

import streamlink
from pystream import StreamThread

# import m3u8


movie = 'https://www.huya.com/a16789'


session = streamlink.Streamlink() #创建一个会话
try:
    streams = session.streams(movie) #在会话里输入url会返回直播的flv缓存地址
except:
    try:
        streams = streamlink.streams(movie)
    except:
        print('[INFO]该网站不存在plug接口')
        exit(0)

print('[INFO]获取了视屏流地址.....')

for k, v in streams.items():
    print(k, v)

source = None

lists = ['best', 'high', 'source', 'mobile', 'medium',  'low', 'worst']

for l in lists:
    if l in streams:
        source = streams[l].url
        print('[INFO]获得视频%s:%s' % (l, source))
        break

a = StreamThread(1, source, 'test', 'stream/m3u8/', 'm3u8')

a.run()




# if source:
#     vidcap = cv2.VideoCapture(source)
#     success, image = vidcap.read()
#     count = 0
#     while success:
#         cv2.imwrite("frame%d.jpg" % count, image)   # save frame as JPEG file
#         success, image = vidcap.read()
#         print('Read a new frame: ', success)
#         count += 1

# downloader = m3u8.Downloader(50)
# downloader.run(source, '/Users/Lou/PycharmProjects/pydemo/pystream/stream/m3u8/')
