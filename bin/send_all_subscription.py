import os
import random

from pymessenger.bot import Bot
from pymongo import MongoClient

import OxfordDictionary
from subscriptions import get_podcasts

MONGODB_URI = os.environ['MONGODB_URI']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
client = MongoClient(MONGODB_URI)
db = client.chatbot_db
user_subscriptions_collection = db.user_subscriptions_collection
user_state_collection=db.user_state_collection
podcasts_feed_collection = db.podcasts_feed_collection
phrase_of_the_day_collection = db.phrase_of_the_day_collection
bot = Bot(ACCESS_TOKEN)
all_tags=["bbc",'football','politics','science','longreads','technology','global']

# SEND ALL SUBSCRIPTIONS
for every in all_tags:
    latest = get_podcasts(every)[0]['title']
    if not latest==podcasts_feed_collection.posts.find_one({'tag': every})['latest']:
            podcasts_feed_collection.posts.update_one({'tag': every}, {"$set": {'latest':latest}}, upsert=True)

            for document in user_subscriptions_collection.posts.find():
                user_id = document['user_id']
                tags = document['tags']

                for tag in tags:
                    if tag == every:
                        bot.send_text_message(user_id,
                                              "Hey! Here are some fresh stuff for you!\nDon't be lazy and improve your english every day!")
                        podcasts = get_podcasts(tag)
                        elements = []
                        elements.append({
                            "title": podcasts[0]['title'],
                            "image_url": podcasts[0]['img'],
                            "subtitle": podcasts[0]['description'],
                            "default_action": {
                                "type": "web_url",
                                "url": podcasts[0]['link'],
                                "webview_height_ratio": "tall",
                            },
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "url": podcasts[0]['link'],
                                    "title": "Listen!"
                                }, {
                                    "type": "postback",
                                    "title": 'UNSUBSCRIBE',
                                    "payload": 'UNSUBSCRIBE' + "_" + tag
                                }
                            ]
                        })

                        payload = {
                            'message': {
                                "attachment": {
                                    "type": "template",
                                    "payload": {
                                        "template_type": "generic",
                                        "elements": elements
                                    }
                                }
                            },
                            "tag":
                                "NON_PROMOTIONAL_SUBSCRIPTION",
                            'recipient': {
                                'id': user_id
                            },
                            'notification_type':
                                'REGULAR'
                        }
                        bot.send_raw(payload)

# SEND THE PHRASE OF THE DAY
for document in user_state_collection.posts.find():
    user_id = document["user_id"]
    dic={"text": "I don't know this word", "attachment": None, "examples": None}
    while not dic["text"]=="I don't know this word":
        types=['idioms','phrasal_verbs']
        type=random.choice(types)
        result = phrase_of_the_day_collection.posts.find_one({'type': type})
        phrase = result["phrase"][result["current_number"]]
        # update number
        phrase_of_the_day_collection.posts.update_one({'type': type}, {"$inc": {'current_number': +1}}, upsert=True)

        dic = OxfordDictionary.oxford_dic_request(phrase)
    text = dic["text"]
    elements = []
    elements.append({
                    "title":dic["text"].split("\n",1)[0],
                    "image_url": 'https://is1-ssl.mzstatic.com/image/thumb/Purple118/v4/2c/96/13/2c9613fb-cbbf-3910-15fd-92540ff89a16/mzl.ytnapyct.png/246x0w.jpg',
                    "subtitle": dic["text"].split("\n",1)[1],
                    "default_action": {
                        "type": "web_url",
                        "url": "",
                        "webview_height_ratio": "tall",
                    },
                    "buttons":[{"type":"postback",
                                            "title":"Examples",
                                            "payload":"OXFORD_DIC_EXAMPLES"},
                                          {"type": "postback",
                                            "title": "Synonyms-Antonyms",
                                            "payload": "OXFORD_DIC_SYNONYMS"},
                                          {"type": "postback",
                                                    "title": "Pronunciation",
                                                    "payload": "OXFORD_DIC_PRONUNCIATION"}
                                          ]
                })
    bot.send_generic_message(user_id, elements)