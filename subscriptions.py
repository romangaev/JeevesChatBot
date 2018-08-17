import re

import requests
from bs4 import BeautifulSoup

BBC = {'rss_url':"http://feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss",
'img_url':'https://pbs.twimg.com/profile_images/540543625071820800/9Pdrd-66.png'}
THEGUARDIAN_FOOTBALL ={'rss_url':"https://audioboom.com/channels/4746648.rss",
'img_url':'https://i.guim.co.uk/img/media/fb35ddef61264c6c9fe193bcae0019049e9362a5/0_0_1400_1400/master/1400.jpg?w=1920&q=55&auto=format&usm=12&fit=max&s=2546f4326244c3099ae402cd43cf66ff'}
THEGUARDIAN_POLITICS ={'rss_url':"https://audioboom.com/channels/1215206.rss",
'img_url':'https://i.guim.co.uk/img/media/e065c92a043d28bd723abf13302ea7794c507b26/0_0_7320_2798/master/7320.jpg?w=620&q=20&auto=format&usm=12&fit=max&dpr=2&s=519898f1f7ea2a864d40570cc65fc6c6'}
THEGUARDIAN_SCIENCE ={'rss_url':"https://audioboom.com/channels/1215215.rss",
'img_url':'https://images.theabcdn.com/i/22242894/2000x500/c'}
THEGUARDIAN_LONGREADS ={'rss_url':"https://audioboom.com/channels/988547.rss",
'img_url':'https://images.theabcdn.com/i/22243651/2000x500/c'}
THEGUARDIAN_TECHNOLOGY ={'rss_url':"https://audioboom.com/channels/1215222.rss",
'img_url':'https://images.theabcdn.com/i/22243219/2000x500/c'}
THEGUARDIAN_GLOBAL ={'rss_url':"https://audioboom.com/channels/1215181.rss",
'img_url':'https://images.theabcdn.com/i/24302550/2000x500/c'}
def get_podcasts(tag):

        if(tag=="english"):
            src=BBC
        elif(tag=='football'):
            src=THEGUARDIAN_FOOTBALL
        elif (tag == 'politics'):
            src = THEGUARDIAN_POLITICS
        elif (tag == 'science'):
            src = THEGUARDIAN_SCIENCE
        elif (tag == 'longreads'):
            src = THEGUARDIAN_LONGREADS
        elif (tag == 'technology'):
            src = THEGUARDIAN_TECHNOLOGY
        elif (tag == 'global'):
            src = THEGUARDIAN_GLOBAL
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