
# coding: utf-8

# # urllib API
# ## urllib.request
# ### urllib.request.urlopen

# In[2]:


import urllib.parse
import urllib.request

#Note: 'data' shoule be 'bytes' type
#          urlopen() could be GET or POST

data = bytes(urllib.parse.urlencode({'word': 'hello'}), encoding = 'utf-8')
reponse = urllib.request.urlopen('http://httpbin.org/post', data = data)
print(reponse.read())


# In[6]:


import urllib.parse
import urllib.request
import socket

try:
    reponse = urllib.request.urlopen('http://httpbin.org/post', timeout = 0.1)
except urllib.error.URLError as e:
    if isinstance(e.reason, socket.timeout):
        print('TIME OUT')


# ### urllib.request.Request

# In[4]:


from urllib import request, parse

#Note: 'data' shoule be 'bytes' type

url = 'http://httpbin.org/post'
headers = {
    'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
    'Host' : 'httpbin.org'
}
dict = {
    'name' : 'Damon To'
}
data = bytes(parse.urlencode(dict), encoding = 'utf-8')
req = request.Request(url = url, data = data, headers = headers, method = 'POST')
response = request.urlopen(req)
print(response.read())


# ### Handler & Opener

# In[10]:


# use handler and opener to get cookie
import http.cookiejar, urllib.request

cookie = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)
response = opener.open('http://www.baidu.com')
for item in cookie:
    print(item.name+'='+item.value)


# ## urllib.error
# ### urllib.error.URLError & urllib.error.HTTPError

# In[13]:


from urllib import error, request

try:
    response = request.urlopen('https://cuiqingcai.com/index.htm')
except error.HTTPError as e:
    print(e.reason, e.code, e.headers, sep='\n')
except error.URLError as e:
    print(e.reason)
else:
    print('Request Successfully!')


# ## urllib.parse

# ### urllib.parse.urlparse

# In[3]:


from urllib.parse import urlparse

result = urlparse('http://www,baidu.com/index.html;user?id=5#comment', allow_fragments = True)
print(result)


# ### urllib.parse.urlunparse

# In[4]:


from urllib.parse import urlunparse

data = ['http', 'www.baidu.com', 'index.html', 'user', 'a=6', 'comment']
print(urlunparse(data))


# ### urllib.parse.urlsplit

# In[5]:


from urllib.parse import urlsplit

result = urlsplit('http://www,baidu.com/index.html;user?id=5#comment')
print(result)


# ### urllib.parse.urlunsplit

# In[9]:


from urllib.parse import urlunsplit

data = ['http', 'www.baidu.com', 'index.html;', 'a=6', 'comment']
print(urlunsplit(data))


# ### urllib.parse.urljoin

# In[10]:


from urllib.parse import urljoin

print(urljoin('http://www.baidu.com', 'https://cuiqingcai.com/FAQ.html'))
print(urljoin('http://www,baidu.com', '?category=2#comment'))


# ### urllib.parse.urlencode

# In[12]:


from urllib.parse import urlencode

params = {
    'name' : 'Damon',
    'age' : 22
}
base_url = 'http://www.baidu.com?'
print(base_url + urlencode(params))


# ## urllib.robotparser

# In[13]:


from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url('http://www.jianshu.com/robot.txt')
rp.read()
print(rp.can_fetch('*', 'http://www.jianshu.com/p/b67554025d7d'))
print(rp.can_fetch('*', 'http://www.jianshu.com/search?q=python&page=1&type=collections'))

