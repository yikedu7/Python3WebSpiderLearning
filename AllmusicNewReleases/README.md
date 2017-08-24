# README

## 项目背景

![](http://ompnv884d.bkt.clouddn.com/spider1.png)

[AllMusic](http://www.allmusic.com/) 是一个关于音乐的元数据资料库，在1991年由流行文化维护者Michael Erlewine与数学家兼哲学博士Vladimir Bogdanov创立，目的是成为音乐消费者的导览。[AllMusic New Releases](http://www.allmusic.com/newreleases) 是 AllMusic 为用户提供的一项内容推荐服务，以周为频次向用户推荐本周的新音乐/新专辑，甚至你可以通过邮件的形式来订阅该内容。

对于中重度音乐爱好者或习惯聆听新音乐的人群，[AllMusic New Releases](http://www.allmusic.com/newreleases) 提供了很优秀的推荐服务。作为一个严谨专业音乐资料库，AllMusic 提供十分专业且全面的音乐信息。于此同时，AllMusic 有一个由若干专家乐评人组成的内容团队，每周推荐的都是一些比较具有音乐性或话题性的专辑，同时也提供十分专业的乐评

作为一名 AllMusic 的用户，我对其中的内容质量十分满意，但是使用过程中还是有一些不好的体验：

1. 由于服务器架设在国外，虽然没有被墙，但是网页加载十分缓慢。
2. AllMusic 在去年接入广告服务，需要安装对应的广告插件才能正常访问。

学习了 Python 的基本爬虫技术后，我决定尝试一下通过爬虫技术来规避这个问题。基本思路是：爬取最近10周的 AllMusic New Releases 的内容，获取专辑图片(地址)、艺术家、专辑名、风格、厂牌、评分等基本信息，并以文本形式存储于本地，下次需要查看时可以直接查看本地文件。

## 功能实现

一个原始的爬虫实现可以分为：抓取页面 —> 信息提取 —> 格式化输出/存储，同时，由于我们需要处理10个页面，所以引入线程池来实现多线程爬虫能一定程度地优化爬虫性能。有了基本的方向之后就可以开始编写程序，这里我们使用最原始的步进式编程策略来完成。

### (一)抓取单个页面

Python 中关于实现页面抓取的一般有 `urllib` 与 `requests`， 这里我们选择 API 更加简洁的`requests` 。

```python
def getOnePage(url, headers):
    try:
        rp = requests.get(url=url, headers=headers)
        if rp.status_code == 200:
            return rp.text
        return None
    except RequestException as e:
        print('Request Exception')
        return None
```

`getOnePage()`主体上是一个`try...except...`结构，调用`requests.get()`获取指定 url 的 html 代码，并以字符串的形式返回；若获取失败则获取函数抛出的`RequestException`异常，同时要注意 Allmusic 会检查 get 方法的请求头，所以我们需要传入`headers`请求头参数。

### (二)信息析取

这里我们需要爬取两方面的信息：一是我们需要获取的New Releases 的内容；二是需要从网页中获取日期信息来构成url(当然也可以直接通过算法计算，Allmusic 的更新日期是每周的周五)。

####析取 New Releases 中的内容

![](http://ompnv884d.bkt.clouddn.com/spider2.jpg)

使用Chrome的开发者工具分析我们需要爬取的网页，观察我们关心的字段内容及其所在的标签。这里我们使用正则表达式匹配来解析，当然你也可以选择 BeautifulSoup、Pyquery 等网页解析库。

```python
def parseOnePage(html):
    # use regular expression to get the specified information we want. It do not work well on 'artist' file, so we
    # we have to process 'artist' after it
    pattern = re.compile('album-cover">.*?img src="(.*?)".*?artist">(.*?)</div>.*?title">.*?>(.*?)</a>.*?label">(.*?)</div>.*?styles">.*?>(.*?)</a>.*?allmusic-rating rating-allmusic-(\d+)">.*?headline-review">(.*?)<div.*?author">(.*?)</div>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        # process the 'artist',in order to remove the html code such as '<a>xxx</a>', I use re.split() func.
        artist = item[1].strip()
        artist = re.split('<.*?>', artist)
        artist = ''.join(artist).strip()
        yield {
            'cover': item[0],
            'artist': artist,
            'title': item[2],
            'label': item[3].strip(),
            'styles': item[4],
            'allmusic-rating': item[5],
            'review': item[6].strip(),
            'author': item[7].strip()[2:],
        }

```

这里使用正则表达式来解决确实带来了一定的麻烦，问题在于在匹配`artist`字段时由于html格式上的不统一给匹配语法带来了麻烦，无法直接用一次正则匹配解决。这里最后采用的方法是“先扩大匹配范围，然后再在后续处理中过滤不需要的内容”这种思路。首先，第一次通过`pattern`规则匹配，我们获得类似如下格式的`artist`字段：

```
...
{'artist': '<a href="http://www.allmusic.com/artist/jefre-cantu-ledesma-mn0002000220">Jefre Cantu-Ledesma</a>'}
{'artist': 'Various Artists'}
{'artist': '<a href="http://www.allmusic.com/artist/peacers-mn0003408245">Peacers</a>'}
...
```

进而，使用`re.split('<.*?>', artist)`，过滤标签即可获得文本内容：

```
...
{'artist': 'Jefre Cantu-Ledesma'}
{'artist': 'Various Artists'}
{'artist': 'Peacers'}
...
```

正则表达式的用法技巧性比较强，不停地试错和调试然后灵活地调用方法才能比较高效地解决问题。正常匹配之后，我们可以尝试添加如下`main()`函数测试单网页的爬取是否正常。

```python
def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Host': 'www.allmusic.com'
    }
    url = 'http://www.allmusic.com/newreleases' 
    print(parseOnePage(getOnePage(url, headers)))
    
if __name__ == '__main__':
  main()
```

#### 获取日期信息

若单网页能正常爬取，那么我们可以开始考虑爬取多个网页。首先分析这些网页url规律：

```
http://www.allmusic.com/newreleases/20170818
http://www.allmusic.com/newreleases/20170811
http://www.allmusic.com/newreleases/20170804
...
```

不难想到，我们只要获取所有的日期并以’YYYYMMDD‘的形式添加在基础url上，就可以得到最终的url。通过一下方法，我们可以从网页中获取日期信息：

```python
def getDate(html):
    # get the most recent date and save as a 'datetime'
    pattern = re.compile('week-filter">.*?value="(.*?)".*?selected">', re.S)
    selecteDate = re.findall(pattern, html)[0]
    selecteDatetime = datetime.strptime(selecteDate, '%Y%m%d')
    date = []
    # Allmusic update its information per week so we get information one time for every 7 days. The way to realize it
    # is changing the end of url(such as /20170818 to 20170811)
    for i in range(10):
        i_timedelta = timedelta(7 * i, 0, 0)
        last_datetime = selecteDatetime - i_timedelta
        date.append(datetime.strftime(last_datetime, '%Y%m%d'))
    return date
```

类似地，也是使用正则匹配的方法。另外，这里我在获取第一个日期字符串后，将其转为`datetime`对象，以使用`datetime`的相关方法来计算得出剩余九个需要获取的日期。

###(三)静态本地存储

```python
def writeDown(content):
    with open('AllmusicNewReleasesLast10Week.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()

```

写入txt文件中，实现本地存储。

### (四)多线程爬取

修改`main()`函数与文件入口，将爬取10个网页的线程加入线程池中，进行多线程爬取：

```python
def main(offset):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome' +
                      '/60.0.3112.90 Safari/537.36',
        'Host': 'www.allmusic.com'
    }
    url = 'http://www.allmusic.com/newreleases'
    date = getDate(getOnePage(url, headers))
    new_url = url + '/' + date[offset]
    for i in parseOnePage(getOnePage(new_url, headers)):
        print(i)
        writeDown(i)

        
if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i for i in range(10)])
```

在控制台输出，引入多线程后爬取时间缩短了2-3秒左右，性能明显提升。

## 项目总结

第一次写爬虫程序，选择了使用 requests + 正则的实现方案，主要是为了巩固基础技术。正则表达式虽然强大，但是在实现过程中确实会遇到困难。或许使用 BeautifulSoup 一个简单的标签选择就可以实现的解析，用正则来实现可能会繁琐许多，工具选择确实对实现效率有很大影响。当然，熟练地使用正则表达式，也能在很多时候很巧妙地解决问题。