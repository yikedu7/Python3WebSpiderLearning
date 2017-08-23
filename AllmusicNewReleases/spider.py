import requests
import re
import json
from multiprocessing import Pool
from datetime import datetime
from datetime import timedelta
from requests.exceptions import RequestException


def getOnePage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome' +
                      '/60.0.3112.90 Safari/537.36',
        'Host': 'www.allmusic.com'
    }
    try:
        rp = requests.get(url=url, headers=headers)
        if rp.status_code == 200:
            return rp.text
        return None
    except RequestException as e:
        print('Request Exception')
        return None

def parseOnePage(html):
    pattern = re.compile('album-cover">.*?img src="(.*?)".*?artist">.*?>(.*?)</a>'
                         + '.*?title">.*?>(.*?)</a>.*?label">(.*?)</div>.*?styles">.*?>(.*?)</a>.*?allmusic-rating '
                           + 'rating-allmusic-(\d+)">.*?headline-review">(.*?)<div.*?author">(.*?)</div>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        if len(item[1]) > 50:
            artist = 'Various Artists'
        else:
            artist = item[1]
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

def getDate(html):
    pattern = re.compile('week-filter">.*?value="(.*?)".*?selected">', re.S)
    selecteDate = re.findall(pattern, html)[0]
    selecteDatetime = datetime.strptime(selecteDate, '%Y%m%d')
    date = []
    for i in range(10):
        i_timedelta = timedelta(7 * i, 0, 0)
        last_datetime = selecteDatetime - i_timedelta
        date.append(datetime.strftime(last_datetime, '%Y%m%d'))
    return date

def writeDown(content):
    with open('AllmusicNewReleasesLast10Week.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()

def main(offset):
    url = 'http://www.allmusic.com/newreleases'
    date = getDate(getOnePage(url))
    new_url = url + '/' + date[offset]
    for i in parseOnePage(getOnePage(new_url)):
        print(i)
        writeDown(i)

if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i for i in range(10)])
