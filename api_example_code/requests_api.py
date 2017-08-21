
# coding: utf-8

# # requests API
# ## requests.get

# In[32]:


# different between .text & .json()
import requests

data = {
    'name' : 'Damon To',
    'age' : 20
}
rp = requests.get('http://httpbin.org/get', params = data)
print(type(rp.text))
print(rp.text)
print('----------------------------------------------------------------')
print(type(rp.json()))
print(rp.json())


# ### 抓取网页

# In[11]:


import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}
rp = requests.get('https://www.zhihu.com/explore', headers = headers)
# 正则表达式处理
pattern = re.compile('explore-feed.*?question_link.*?>(.*?)</a>', re.S)
titles = re.findall(pattern, rp.text)
print(titles)


# ### 抓取二进制数据

# In[13]:


import requests

rp = requests.get('https://www.github.com/favicon.ico')
with open('favicon.ico', 'wb') as f:
    f.write(rp.content)
    f.close()
#run the code and get a Github ico file


# ## requests.post

# In[15]:


import requests

data = {
    'name' : 'Damon To',
    'age' : 20
}
rp = requests.post('http://httpbin.org/post', data = data)
print(rp.text)


# ## requests 高级使用
# ### 文件上传

# In[16]:


import requests

files = {'file' : open('favicon.ico', 'rb')}
rp = requests.post('http://httpbin.org/post', files = files)
print(rp.text)


# ### Cookie 处理

# In[25]:


import requests

params = {'username' : 'Ryan', 'password' : 'password'}
rp = requests.post('http://pythonscraping.com/pages/cookies/welcome.php', params)
print('Cookie is set to:')
print(rp.cookies.get_dict())
print('-------------------')
print('Going to profile page...')
rp = requests.get('http://pythonscraping.com/pages/cookies/profile.php', cookies = rp.cookies)
print(rp.text)


# ### 会话维持
# 使用 session 持续跟踪会话信息(包括：cookie, header, HTTP 协议信息等等)

# In[27]:


import requests

session = requests.session()

params = {'username' : 'Ryan', 'password' : 'password'}
s = session.post('http://pythonscraping.com/pages/cookies/welcome.php', params)
print('Cookie is set to:')
print(s.cookies.get_dict())
print('-------------------')
print('Going to profile page...')
s = session.get('http://pythonscraping.com/pages/cookies/profile.php')
print(s.text)


# ### HTTP 基本接入认证

# In[28]:


import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('rayn', 'password')
rp = requests.post('http://pythonscraping.com/pages/auth/login.php', auth = auth)
print(rp.text)

