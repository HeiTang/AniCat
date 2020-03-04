#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup



for i in range(1000):

    url = "https://anime1.me?cat="+str(i)

    print(i,' ',end='')

    r = requests.get(url) 

    soup = BeautifulSoup(r.text, 'html.parser')

    h1_tag = soup.find_all("h1", class_="page-title")

    print(h1_tag[0].string)






 