_url = '26284_4000955b87848_883e6a6f1ca988e0bb97.flv?t=1oouarkecowcwqyfeoqlymvwnqxgohubjebvddlgoavvqmhpjppxtrojfgcxsajrfxtcyzjtcmjstclisd'

all_url = _url.split('/')
url_pre = '/'.join(all_url[:-1]) + '/'
url_next = all_url[-1]
print(all_url)
print(url_pre)
print(url_next)
print(url_next.split('?')[0])