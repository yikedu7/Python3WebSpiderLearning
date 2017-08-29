#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
spider.py
~~~~~~~~~~

This module is a spider which use ajax to request information from toutiao.com. In this example, it get the information
in toutiao.com with the keyword '街拍' and save it to MongoDB, also, it download the images about ’街拍‘.
"""

import json
import re
from _md5 import md5
from json import JSONDecodeError
from multiprocessing.pool import Pool
import os
import requests
from requests.exceptions import RequestException
import pymongo
from toutiao.config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


def get_index_page(offset, keyword):
    """
    Get a string with a json format which include the url of the pages about 'keyword'.
    :param offset: A int value which mean the offset on the index page now.
    :param keyword: A string which is the keyword of the information you want to get.
    :return: A string(json format) which is the response we get from index page.
    :raise: RequestException: Output 'Request index page fail!'
    """
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3,
    }
    url = 'https://www.toutiao.com/search_content/?'
    try:
        rp = requests.get(url, data)
        if rp.status_code == 200:
            return rp.text
        return None
    except RequestException:
        print('Request index page fail!')


def parse_index_page(response):
    """
    Parse the index page's response and get the detail pages' url.
    :param response: A string(json format) that include the detail pages' url.
    :return: A generator(list) which contents the url of detail pages.
    :raise: JSONDecodeError: Output 'Parse index page fail!'
    """
    try:
        json_data = json.loads(response)
        if json_data and 'data' in json_data.keys():
            for item in json_data['data']:
                if 'article_url' in item.keys():
                    yield item['article_url']
    except JSONDecodeError:
        print('Parse index page fail!')


def get_detail_page(url):
    """
    Get the detail page html code with the specified url.
    :param url: A string that is the url of the detail page you want to get.
    :return: A string which is a html code of the detail page.
    :raise: RequestException: Output 'Request detail page fail!'
    """
    try:
        rp = requests.get(url)
        if rp.status_code == 200:
            return rp.text
        return None
    except RequestException:
        print('Request detail page fail!')


def parse_detail_page(html, url):
    """
    Parse detail page and get title and image url from it.
    :param html: A string which is the html code of detail page.
    :param url: A string which is the url of detail page.
    :return: A dict including the information got from detail page.
    """
    title_pattern = re.compile('BASE_DATA.galleryInfo.*?title: \'(.*?)\',', re.S)
    gallery_pattern = re.compile('gallery: (.*?),\n    siblingList', re.S)
    try:
        title = re.findall(title_pattern, html)[0]
        gallery = re.findall(gallery_pattern, html)[0]
        if gallery:
            json_data = json.loads(gallery)
            if 'sub_images' in json_data:
                sub_images = json_data['sub_images']
                images = [item['url'] for item in sub_images]
            return {
                'url': url,
                'title': title,
                'images': images
            }
    except IndexError:
        pass


def save_to_mongo(data):
    """
    Save the data the spider get to MongoDB.
    :param data: A dict that include the information the spider get.
    :return: Return a boolean(True when successfully save and False when meeting exception)
    """
    try:
        if db[MONGO_TABLE].insert(data):
            print('save to mongoDB success:', data)
            return True
    except Exception:
        return False


def download_image(url):
    """
    Download the image and save in project folder.
    :param url: A string which is the url of image.
    :return: A boolean value(True when successfully download and False when fail)
    :raise: RequestException: Output Download image fail!'
    """
    print('Downloading: ' + url)
    try:
        rp = requests.get(url)
        if rp.status_code == 200:
            content = rp.content
            file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(content)
                    f.close()
                return True
        return None
    except RequestException:
        print('Download image fail!')
        return False


def main(offset):
    """
    The main func.
    :param offset: A int which is the offset value of index page.
    """
    response = get_index_page(offset, KEYWORD)
    for url in parse_index_page(response):
        detail_html = get_detail_page(url)
        data = parse_detail_page(detail_html, url)
        for i in data['images']:
            download_image(i)
        save_to_mongo(data)


if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i*20 for i in range(5)])