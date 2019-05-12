_url = 'http://m.1y666.com:2100/20190405/DOaNWGWQ/index.m3u8'

all_url = _url.split('/')
url_pre = '/'.join(all_url[:-1]) + '/'
url_next = all_url[-1]
print(all_url)
print(url_pre)
print(url_next)
