import re

import requests
from bs4 import BeautifulSoup

BBC = {'rss_url':"http://feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss",
'img_url':'https://pbs.twimg.com/profile_images/540543625071820800/9Pdrd-66.png'}
THEGUARDIAN ={'rss_url':"https://www.theguardian.com/podcasts/rss",
'img_url':'https://i.guim.co.uk/img/media/60594135c99432a8f1cc9d8abf03156742d56182/0_0_3103_1861/master/3103.jpg?w=1920&q=55&auto=format&usm=12&fit=max&s=ccef16dfcc538c4f08bdec9139edce75'}

def get_podcasts(src, optional_tag):
        news_items = []
        resp = requests.get(src['rss_url'])
        soup = BeautifulSoup(resp.content, features="xml")
        if(src==BBC):

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
        elif(src==THEGUARDIAN):
            tag = optional_tag
            items = soup.findAll('category', text=re.compile('.*%s.*' % tag, re.IGNORECASE))

            news_items = []

            for item in items:
                news_item = {}
                news_item['title'] = item.parent.title.text
                news_item['description'] = item.parent.description.text
                news_item['link'] = item.parent.link.text
                news_item['img'] = src['img_url']
                news_items.append(news_item)