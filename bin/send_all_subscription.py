import os
import pickle
import random

from bson import Binary
from pymessenger.bot import Bot
from pymongo import MongoClient

import OxfordDictionary
from app import build_menu
from subscriptions import get_podcasts
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

MONGODB_URI = os.environ['MONGODB_URI']
TG_TOKEN = os.environ['TG_TOKEN']

client = MongoClient(MONGODB_URI)
db = client.chatbot_db
user_subscriptions_collection = db.user_subscriptions_collection
user_state_collection = db.user_state_collection
podcasts_feed_collection = db.podcasts_feed_collection
phrase_of_the_day_collection = db.phrase_of_the_day_collection
#bot = Bot(ACCESS_TOKEN)
updater = Updater(TG_TOKEN)
all_tags = ["bbc", 'football', 'politics', 'science', 'longreads', 'technology', 'global']

# SEND ALL SUBSCRIPTIONS
'''for every in all_tags:
    latest = get_podcasts(every)[0]['title']
    if podcasts_feed_collection.posts.find_one({'tag': every}) is None or not latest == \
                                                                              podcasts_feed_collection.posts.find_one(
                                                                                      {'tag': every})['latest']:
        podcasts_feed_collection.posts.update_one({'tag': every}, {"$set": {'latest': latest}}, upsert=True)

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
'''
# SEND THE PHRASE OF THE DAY
dic = {"text": "404", "attachment": None, "examples": None}
type_of_phrase = ""
while dic["text"] == "404":
        types = ['idioms', 'phrasal_verbs']
        type_of_phrase = random.choice(types)
        result = phrase_of_the_day_collection.posts.find_one({'type': type_of_phrase})
        phrase = result["phrase"][result["current_number"] % len(result["phrase"])]
        # update number
        phrase_of_the_day_collection.posts.update_one({'type': type_of_phrase}, {"$inc": {'current_number': +1}}, upsert=True)
        dic = OxfordDictionary.oxford_dic_request(phrase)
        print('WORD OF THE DAY')
        print(dic)



for document in user_state_collection.posts.find():
    user_id = document["user_id"]

    text = dic["text"]
    print(text)
    buttons = [{"type": "postback",
                "title": "Examples",
                "payload": "OXFORD_DIC_EXAMPLES." + phrase},
               {"type": "postback",
                "title": "Synonyms-Antonyms",
                "payload": "OXFORD_DIC_SYNONYMS." + phrase},
               {"type": "postback",
                "title": "Pronunciation",
                "payload": "OXFORD_DIC_PRONUNCIATION." + phrase}]

    bot.sendPhoto(user_id, "https://i.ibb.co/71bh29h/pod.png")
    #bot.send_image_url(user_id, "https://image.ibb.co/kEx6oK/phrase_of_the_day.png")
    titles = [x['title'] for x in buttons]
    button_list = [InlineKeyboardButton(x, callback_data=x) for x in titles]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    bot.sendMessage(user_id, text, reply_markup=reply_markup)
    #bot.send_button_message(user_id, text, buttons)

    s_m_bytes = user_state_collection.posts.find_one({'user_id': user_id})
    user_state_machine = pickle.loads(s_m_bytes['state_machine'])
    user_state_machine.data["examples"] = dic["examples"]
    user_state_machine.data["attachment"] = dic["attachment"]
    s_m_bytes = pickle.dumps(user_state_machine)
    post = {'user_id': user_id, 'state_machine': Binary(s_m_bytes)}
    user_state_collection.posts.update_one({'user_id': user_id}, {"$set": post}, upsert=False)

