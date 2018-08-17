import requests
from bs4 import BeautifulSoup

BBC = {'rss_url':"http://feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss",
'img_url':'https://pbs.twimg.com/profile_images/540543625071820800/9Pdrd-66.png'}


def get_podcasts(src):
        news_items = []
        resp = requests.get(src['rss_url'])
        soup = BeautifulSoup(resp.content, features="xml")

        #print(soup)
        items = soup.findAll('item')
        print(items[0])

        news_items = []

        for item in items:
            news_item = {}
            news_item['title'] = item.title.text
            news_item['description'] = item.description.text
            news_item['link'] = item.link.text
            news_item['img'] = src['img_url']
            news_items.append(news_item)

        return news_items
