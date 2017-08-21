
# coding: utf-8

# # BeautifulSoup Example
# ## 基本写法(with 错误处理)

# In[4]:


from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup

def getTitle(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        return None
    try:
        bsObj = BeautifulSoup(html.read(), 'lxml')
        title = bsObj.body.h1
    except AttributeError as e:
        return None
    return title
title = getTitle('http://www.pythonscraping.com/pages/page1.html')
if title == None:
    print('Title could not be found')
else:
    print(title)


# ## find() / findAll()

# In[5]:


from urllib.request import urlopen
from bs4 import BeautifulSoup

html = urlopen('http://www.pythonscraping.com/pages/warandpeace.html')
bsObj = BeautifulSoup(html, 'lxml')
nameList = bsObj.findAll('span', {'class' : 'green'})
for name in nameList:
    print(name.get_text())


# ## 子级标签/后代标签/兄弟标签/父级标签

# In[6]:


from urllib.request import urlopen
from bs4 import BeautifulSoup

html = urlopen('http://www.pythonscraping.com/pages/page3.html')
bsObj = BeautifulSoup(html, 'lxml')

for child in bsObj.find('table', {'id' : 'giftList'}).children:
    print(child)

for sibling in bsObj.find('table', {'id' : 'giftList'}).tr.next_siblings:
    print(sibling)

print(bsObj.find('img', {'src' : '../img/gifts/img1.jpg'}).parent.previous_sibling.get_text())


# ## 使用正则表达式

# In[8]:


from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

html = urlopen('http://www.pythonscraping.com/pages/page3.html')
bsObj = BeautifulSoup(html, 'lxml')
images = bsObj.findAll('img', {'src' : re.compile('\.\.\/img\/gifts\/img.*\.jpg')})
for image in images:
    print(image['src'])


# ## 遍历单个域名

# In[10]:


#逐页面遍历维基百科，读取词条链接
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime
import random

random.seed(datetime.datetime.now())
def getLinks(articleUrl):
    html = urlopen('http://en.wikipedia.org' + articleUrl)
    bsObj = BeautifulSoup(html, 'lxml')
    return bsObj.find('div', {'id' : 'bodyContent'}).findAll('a', href = re.compile('^(/wiki/)((?!:).)*$'))
links = getLinks('/wiki/Kevin_Bacon')
while len(links) > 0:
    newArticle = links[random.randint(0, len(links) - 1)].attrs['href']
    print(newArticle)
    links = getLinks(newArticle)


# In[ ]:




