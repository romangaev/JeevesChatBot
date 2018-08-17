import re

import requests
from bs4 import BeautifulSoup

BBC = {'rss_url':"http://feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss",
'img_url':'https://pbs.twimg.com/profile_images/540543625071820800/9Pdrd-66.png'}
THEGUARDIAN_FOOTBALL ={'rss_url':"https://audioboom.com/channels/4746648.rss",
'img_url':'https://i.guim.co.uk/img/media/fb35ddef61264c6c9fe193bcae0019049e9362a5/0_0_1400_1400/master/1400.jpg?w=1920&q=55&auto=format&usm=12&fit=max&s=2546f4326244c3099ae402cd43cf66ff'}

def get_podcasts(tag):

        if(tag=="english"):
            src=BBC
        elif(tag=='football'):
            src=THEGUARDIAN_FOOTBALL
        else:
            src = THEGUARDIAN_FOOTBALL

        resp = requests.get(src['rss_url'])
        soup = BeautifulSoup(resp.content, features="xml")

        items = soup.findAll('item')
        news_items = []

        for item in items:
                news_item = {}
                news_item['title'] = item.title.text
                news_item['description'] = item.description.text
                news_item['link'] = item.link.text
                news_item['img'] = src['img_url']
                news_items.append(news_item)

        return news_items