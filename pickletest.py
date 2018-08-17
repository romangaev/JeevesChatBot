import re

import requests
from bs4 import BeautifulSoup

url = "https://www.theguardian.com/podcasts/rss"

resp = requests.get(url)

soup = BeautifulSoup(resp.content, features="xml")

#print(soup)
tag=''
items = soup.findAll('category', text=re.compile('.*%s.*' % tag, re.IGNORECASE))
print(items[0].parent)

'''
news_items = []

for item in items:
    news_item = {}
    news_item['title'] = item.title.text
    news_item['description'] = item.description.text
    news_item['link'] = item.link.text
    news_item['image'] = item.content['url']
    news_items.append(news_item)

print(news_items)'''