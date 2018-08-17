import requests
from bs4 import BeautifulSoup

url = "http://feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss"

resp = requests.get(url)

soup = BeautifulSoup(resp.content, features="xml")

#print(soup)
items = soup.findAll('item')
print(items[0])
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