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

ENGLISH = {'rss_url': "http://feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss",
'img_url':'https://pbs.twimg.com/profile_images/540543625071820800/9Pdrd-66.png'}
NEWS ={'rss_url': "https://podcasts.files.bbci.co.uk/p02nq0gn.rss",
'img_url':'https://ichef.bbci.co.uk/images/ic/480x480/p05z434b.jpg'}
FOOTBALL ={'rss_url':"https://podcasts.files.bbci.co.uk/p02nrsln.rss",
'img_url':'https://ichef.bbci.co.uk/images/ic/480x480/p06g7bs3.jpg'}
DISCOVERY={'rss_url':"https://podcasts.files.bbci.co.uk/p002w557.rss",
'img_url':'https://ichef.bbci.co.uk/images/ic/480x480/p05yxbbn.jpg'}


def get_podcasts(tag):

        if(tag=="english"):
            src=ENGLISH
        elif(tag=='news'):
            src=NEWS
        elif (tag == 'discovery'):
            src = DISCOVERY
        elif (tag == 'football'):
            src = FOOTBALL

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

def subscribe(user_id,tag):
    user_subscriptions_collection.posts.update_one({'user_id': user_id}, {"$push": {'tags': tag}}, upsert=True)

def unsubscribe(user_id,tag):
    user_subscriptions_collection.posts.update_one({'user_id': user_id}, {"$pull": {'tags': tag}}, upsert=True)

def check_subscription(user_id,tag):
    query = user_subscriptions_collection.posts.find_one({'user_id': user_id})
    return query is not None and tag in query["tags"]




