import re

import requests
from bs4 import BeautifulSoup

url = "https://www.theguardian.com/football/series/footballweekly/podcast.xml"

resp = requests.get(url)

soup = BeautifulSoup(resp.content, features="xml")

#print(soup)
tag='sport'
items = soup.findAll('item')
news_items = []
print(items[0])
'''for item in items:
                news_item = {}
                news_item['title'] = item.parent.title.text
                news_item['description'] = item.parent.description.text
                news_item['link'] = item.parent.link.text
                news_items.append(news_item)
#print(news_items[3])

'''
