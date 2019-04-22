import os
import re

import requests
from bs4 import BeautifulSoup
from pymessenger import bot
from pymongo import MongoClient

MONGODB_URI = os.environ['MONGODB_URI']
client = MongoClient(MONGODB_URI)
db = client.chatbot_db
user_subscriptions_collection = db.user_subscriptions_collection

BBC = {'rss_url':"http://feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss",
'img_url':'https://pbs.twimg.com/profile_images/540543625071820800/9Pdrd-66.png'}
THEGUARDIAN_FOOTBALL ={'rss_url':"https://www.theguardian.com/football/series/footballweekly/podcast.xml",
'img_url':'https://images.theabcdn.com/i/29436324/2000x500/c'}
THEGUARDIAN_POLITICS ={'rss_url':"https://audioboom.com/channels/1215206.rss",
'img_url':'https://images.theabcdn.com/i/22243017/2000x500/c'}
THEGUARDIAN_SCIENCE ={'rss_url':"https://audioboom.com/channels/1215215.rss",
'img_url':'https://images.theabcdn.com/i/22242894/2000x500/c'}
THEGUARDIAN_LONGREADS ={'rss_url':"https://audioboom.com/channels/988547.rss",
'img_url':'https://images.theabcdn.com/i/22243651/2000x500/c'}
THEGUARDIAN_TECHNOLOGY ={'rss_url':"https://audioboom.com/channels/1215222.rss",
'img_url':'https://images.theabcdn.com/i/22243219/2000x500/c'}
THEGUARDIAN_GLOBAL ={'rss_url':"https://audioboom.com/channels/1215181.rss",
'img_url':'https://images.theabcdn.com/i/24302550/2000x500/c'}

def get_podcasts(tag):

        if(tag=="bbc"):
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
            src = THEGUARDIAN_GLOBAL

        resp = requests.get(src['rss_url'])
        soup = BeautifulSoup(resp.content, features="xml")

        items = soup.findAll('item')
        news_items = []

        for item in items:
                news_item = {}
                news_item['title'] = item.title.text
                news_item['description'] = item.description.text
                news_item['link'] = item.enclosure.url
                news_item['img'] = src['img_url']
                news_items.append(news_item)

        return news_items

def subscribe(user_id,tag):
    user_subscriptions_collection.posts.update_one({'user_id': user_id}, {"$push": {'tags': tag}}, upsert=True)

def unsubscribe(user_id,tag):
    user_subscriptions_collection.posts.update_one({'user_id': user_id}, {"$pull": {'tags': tag}}, upsert=True)

def check_subscription(user_id,tag):
    query = user_subscriptions_collection.posts.find_one({'user_id': user_id})
    return query is not None and tag in query["tags"]




