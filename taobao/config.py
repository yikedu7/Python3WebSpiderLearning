#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
config.py
~~~~~~~~~~

This module is a the config information of this project.
MONGO_URL: the url of database.
MONGO_DB: the name of database.
MONGO_TABLE: the name of data table.
KEYWORD: the keyword of product information you want to get.
SERVICE_ARGS: the service arguments of PhantomJS.
"""

MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_TABLE = 'sneakers'

KEYWORD = 'sneakers'

SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']