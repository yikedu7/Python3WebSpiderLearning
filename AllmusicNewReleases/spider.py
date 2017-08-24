#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
spider.py
~~~~~~~~~

This module is a spider which get information about new release music from 'allmusic.com'.
You can run it directly and the you will get a output and a txt file, both of them include
the new release music information.
"""

import requests
import re
import json
from multiprocessing import Pool
from datetime import datetime
from datetime import timedelta
from requests.exceptions import RequestException

def getOnePage(url, headers):
    """
    Get all html code from the specified url
    :param url: An url string of the html you want to get
    :param headers: A dict which include the headers of requesting 'allmusic.com'
    :return: A string which include all the html code
    :raise:RequestException: An Error occurred accessing the html
    """
    try:
        rp = requests.get(url=url, headers=headers)
        if rp.status_code == 200:
            return rp.text
        return None
    except RequestException as e:
        print('Request Exception')
        return None


def parseOnePage(html):
    """
    Select the useful information from the html code
    :param html: A string which include all the html code
    :yield: A List of useful information,item of it is  [cover, artist, title, label, styles, allmusc-rating, review,
            author]
    """
    # use regular expression to get the specified information we want. It do not work well on 'artist' file, so we
    # we have to process 'artist' after it
    pattern = re.compile('album-cover">.*?img src="(.*?)".*?artist">(.*?)</div>'
                         + '.*?title">.*?>(.*?)</a>.*?label">(.*?)</div>.*?styles">.*?>(.*?)</a>.*?allmusic-rating '
                           + 'rating-allmusic-(\d+)">.*?headline-review">(.*?)<div.*?author">(.*?)</div>', re.S)
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


def getDate(html):
    """
    Get a list of 10 dates on which we should get the information
    :param html: A string which include all the html code
    :return: A List of strings mean the date(such as '20170818')
    """
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


def writeDown(content):
    """
    Write the information we get into a txt file
    :param content: A List of useful information we get from parseOnePage(html)
    """
    with open('AllmusicNewReleasesLast10Week.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(offset):
    """
    The main func.
    :param offset: A string which include a part of url we should plus after original url
    """
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
