#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
spider.py
~~~~~~~~~~

This module is a spider program which can get product information in 'taobao.com' with
specified keyword. It search 10 pages. get the product information on it and meantime
save the information into a MongoDB database.
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
from pymongo import MongoClient
from config import *

driver = webdriver.PhantomJS(service_args=SERVICE_ARGS)
driver.set_window_size(1920, 1080)
wait = WebDriverWait(driver, 10)
client = MongoClient(MONGO_URL)
db = client[MONGO_DB]


def search():
    """
    Search the information with a keyword in 'taobao.com' and get the result page.
    """
    print('Searching...')
    driver.get('https://www.taobao.com/')
    try:
        input_search = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )
        btn_search = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
        )
        input_search.send_keys(KEYWORD)
        btn_search.click()
    except TimeoutException:
        return search()


def next_page(page_num):
    """
    Go to next page with a specified page number.
    :param page_num: A int which is the page number.
    """
    print('Go to next page...')
    try:
        input_jump = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )
        btn_jump_submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > ' +
                                        'span.btn.J_Submit'))
        )
        input_jump.clear()
        input_jump.send_keys(page_num)
        btn_jump_submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > ' +
                                              'li.item.active > span'), str(page_num))
        )
    except TimeoutException:
        next_page(page_num)


def parse_itemlist(itemlist):
    """
    Parse the product list and get the valid information.
    :param itemlist: A string which is a part of html code contents the product list.
    :return: A generator(a list of dict) which contents the valid information of products.
    """
    print('Parsing the page...')
    try:
        doc = pq(itemlist)
        items = doc('.m-itemlist .items .item').items()
        for item in items:
            product = {
                'img': item.find('.pic .img').attr('src'),
                'price': item.find('.price').text(),
                'deal_cnt': int(item.find('.deal-cnt').text()[:-3]),
                'title': item.find('.title').text(),
                'link': item.find('.title .J_ClickStat').attr('href'),
                'shop': item.find('.shop').text()
            }
            yield product
    except Exception:
        print('Parse the item list fail!')


def get_page(page_num):
    """
    Get the page with specified page number.
    :param page_num: A int which is the page number.
    :return: A string which is a part of html code contents the product list.
    """
    if page_num == 1:
        search()
    else:
        next_page(page_num)
    itemlist = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist'))
    )
    return itemlist.get_attribute('innerHTML')


def save_to_mongo(item):
    """
    Save the information to the MongoDB database.
    :param item: A list which contents the product information.
    :except:print 'Fail to save' when meeting any exception.
    """
    try:
        if db[MONGO_TABLE].insert(item):
            print('Successfully save:', item)
    except Exception:
        print('Fail to save', item)


def main():
    """
    The main func.
    """
    for i in range(1, 11):
        page = get_page(i)
        for item in parse_itemlist(page):
            save_to_mongo(item)


if __name__ == '__main__':
    main()



