#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024-08-14 9:59
# @Author  : 1o00
# @Site    : 
# @File    : log.py
# @Software: PyCharm


import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)
