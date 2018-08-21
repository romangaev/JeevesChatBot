# Python libraries that we need to import for our bot
# LATEST WORKING VERSION

import os
import random

import requests
from flask import Flask, request
from pymessenger.bot import Bot
import StateMachine
from pymongo import MongoClient
import OxfordDictionary
from bson.binary import Binary
import pickle

import subscriptions

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
MONGODB_URI = os.environ['MONGODB_URI']
client = MongoClient(MONGODB_URI)
db = client.chatbot_db
user_state_collection=db.user_state_collection
bot = Bot(ACCESS_TOKEN)
states = {}
# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):

                        response_dic = get_message(recipient_id, message['message'].get('text'))
                        if "buttons" in response_dic:
                            bot.send_button_message(recipient_id, response_dic["text"], response_dic["buttons"])
                        elif "elements" in response_dic:
                            bot.send_generic_message(recipient_id, response_dic["elements"])
                        else:
                            send_message(recipient_id, response_dic["text"])

                        if "attachment" in response_dic:
                            bot.send_audio_url(recipient_id, response_dic["attachment"])
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        bot.send_image_url(recipient_id, 'https://i.ytimg.com/vi/aEtm69mLK6w/hqdefault.jpg')
                        bot.send_audio_url(recipient_id, "http://www.noiseaddicts.com/samples_1w72b820/3727.mp3")

                # postback webhook
                if message.get("postback"):
                    # user clicked/tapped "postback" button in earlier message

                    message_text = message["postback"]["payload"]
                    # the button's payload
                    sender_id = message["sender"]["id"]
                    if message_text == "HELLO":
                        send_message(sender_id, "hello world!")
                    elif "UNSUBSCRIBE" in message_text:
                        tag = message_text.split('_')[1]
                        subscriptions.unsubscribe(sender_id, tag)
                        send_message(sender_id, "Done!")
                    elif "SUBSCRIBE" in message_text:
                        tag = message_text.split('_')[1]
                        subscriptions.subscribe(sender_id, tag)
                        send_message(sender_id, "Done!")

                    elif "OXFORD_DIC_SYNONYMS" in message_text:
                        s_m_bytes = user_state_collection.posts.find_one({'user_id': sender_id})
                        user_state_machine = pickle.loads(s_m_bytes['state_machine'])
                        syn_ant={}
                        if "word_id" in user_state_machine.data:
                            syn_ant=OxfordDictionary.oxford_dic_syn_ant(user_state_machine.data["word_id"])
                        else:
                            syn_ant=OxfordDictionary.oxford_dic_syn_ant(message_text.split(".",1)[1])
                        send_message(sender_id, syn_ant["synonyms"])
                        send_message(sender_id,syn_ant["antonyms"])

                    elif "OXFORD_DIC_EXAMPLES" in message_text:
                        s_m_bytes = user_state_collection.posts.find_one({'user_id': sender_id})
                        user_state_machine = pickle.loads(s_m_bytes['state_machine'])
                        examples=""
                        if "examples" in user_state_machine.data:
                            examples =user_state_machine.data["examples"]
                        else:
                            examples=OxfordDictionary.oxford_dic_request(message_text.split(".",1)[1])["examples"]
                        send_message(sender_id, examples)

                    elif "OXFORD_DIC_PRONUNCIATION" in message_text:
                        s_m_bytes = user_state_collection.posts.find_one({'user_id': sender_id})
                        user_state_machine = pickle.loads(s_m_bytes['state_machine'])
                        attachment =""
                        if "attachment" in user_state_machine.data:
                            attachment =user_state_machine.data["attachment"]
                        else:
                            attachment=OxfordDictionary.oxford_dic_request(message_text.split(".",1)[1])["attachment"]

                        if attachment == "":
                            send_message(sender_id, "Couldn't find any pronunciation...")
                        else:
                            url = attachment
                            print(url)
                            r = requests.get(url, allow_redirects=True)
                            open('temp.mp3', 'wb').write(r.content)
                            bot.send_file_url(sender_id,url)
                            os.remove("temp.mp3")


    # http: // audio.oxforddictionaries.com / en / mp3 / pronunciation_gb_1_8.mp3
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# chooses a random message to send to the user
def get_message(user_id, message):
    #sample_responses = [classify(message)]
    # return selected item to the user
    #return random.choice(sample_responses)
    respose_dic={}

    print(user_id)
    print(user_state_collection.posts.find_one({'user_id': user_id}) is not None)
    # if user_id in states:
    if user_state_collection.posts.find_one({'user_id': user_id}) is not None:
        # user_state_machine = states[user_id]
        s_m_bytes = user_state_collection.posts.find_one({'user_id': user_id})
        user_state_machine = pickle.loads(s_m_bytes['state_machine'])

        print("state before")
        user_state_machine.printing_state()
        respose_dic = user_state_machine.state_respond(message)
        print("State after")
        user_state_machine.printing_state()
        # save it back to db
        s_m_bytes = pickle.dumps(user_state_machine)
        post = {'user_id': user_id, 'state_machine': Binary(s_m_bytes)}
        user_state_collection.posts.update_one({'user_id': user_id}, {"$set": post}, upsert=False)
    else:
        user_state_machine = StateMachine.StateMachine('', user_id)
        s_m_bytes = pickle.dumps(user_state_machine)
        post = {'user_id': user_id, 'state_machine': Binary(s_m_bytes)}
        user_state_collection.posts.insert_one(post)
        # states[user_id] = StateMachine.StateMachine('')
        # user_state_machine = states[user_id]
        print(states)
        respose_dic ={"text": "Hi! I'm English learning bot.\n You can ask for listening resources, subscribe for stuff and manage your vocabulary to learn. Try something of that:\n # add a word to my dictionary\n # give me some listening resources\n # what does /something/ mean?"}
    return respose_dic


# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
