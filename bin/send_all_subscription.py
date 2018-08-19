import os
from pymessenger.bot import Bot
from pymongo import MongoClient
from subscriptions import get_podcasts

MONGODB_URI = os.environ['MONGODB_URI']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
client = MongoClient(MONGODB_URI)
db = client.chatbot_db
user_subscriptions_collection = db.user_subscriptions_collection
bot = Bot(ACCESS_TOKEN)

for document in user_subscriptions_collection.posts.find():
    user_id = document['user_id']
    tags = document['tags']
    for tag in tags:
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
            'recipient':{
                'id': user_id
            },
            'notification_type':
                'REGULAR'
        }
        bot.send_raw(payload)
