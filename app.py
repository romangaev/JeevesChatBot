# Python libraries that we need to import for our bot
import random
import os
from flask import Flask, request
from pymessenger.bot import Bot
import StateMachine
from pymongo import MongoClient
import requests
import json


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

                        if response_dic["attachment"] is not None:

                            send_message(recipient_id, response_dic["text"])
                            bot.send_audio_url(recipient_id, response_dic["attachment"])
                        else:
                            send_message(recipient_id, response_dic["text"])
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        #response_sent_nontext = get_message()
                        #send_message(recipient_id, response_sent_nontext)
                        #bot.send_audio_url(recipient_id,)
                        post_attachment(recipient_id,"http: // audio.oxforddictionaries.com / en / mp3 / pronunciation_gb_1_8.mp3",'audio')






                        '''bot.send_image_url(recipient_id, 'https://i.ytimg.com/vi/aEtm69mLK6w/hqdefault.jpg')
                        fb_url = 'https://graph.facebook.com/v2.6/me/messages'
                        data = {
                            'recipient': '{"id":' + recipient_id + '}',
                            'message': '{"attachment":{"type":"audio", "payload":{}}}'
                        }
                        files = {
                            'filedata': (
                            'http: // audio.oxforddictionaries.com / en / mp3 / pronunciation_gb_1_8.mp3', open("http: // audio.oxforddictionaries.com / en / mp3 / pronunciation_gb_1_8.mp3", "rb"), 'audio/mp3')}
                        params = {'access_token': ACCESS_TOKEN}
                        requests.post(fb_url, params=params, data=data, files=files)'''
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

    from bson.binary import Binary
    import pickle

    print(user_id)
    print(user_state_collection.posts.find_one({'user_id': user_id}) is not None)
    # if user_id in states:
    if user_state_collection.posts.find_one({'user_id': user_id}) is not None:
        # user_state_machine = states[user_id]
        s_m_bytes = user_state_collection.posts.find_one({'user_id': user_id})
        user_state_machine = pickle.loads(s_m_bytes['state_machine'])
    else:
        user_state_machine = StateMachine.StateMachine('', user_id)
        s_m_bytes = pickle.dumps(user_state_machine)
        post = {'user_id': user_id, 'state_machine': Binary(s_m_bytes)}
        user_state_collection.posts.insert_one(post)
        # states[user_id] = StateMachine.StateMachine('')
        # user_state_machine = states[user_id]
        print(states)
    print("state before")
    user_state_machine.printing_state()
    respose_dic = user_state_machine.state_respond(message)
    print("State after")
    user_state_machine.printing_state()
    print(type(respose_dic))
    # save it back to db
    s_m_bytes = pickle.dumps(user_state_machine)
    post = {'user_id': user_id, 'state_machine': Binary(s_m_bytes)}
    user_state_collection.posts.update_one({'user_id': user_id}, {"$set": post}, upsert=False)
    return respose_dic


# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

def post_attachment(fbid, media_url, file_type,
                    is_reusable=False, messaging_type="RESPONSE", tag=None):
    """ Sends a media attachment to the specified user
    :param str fbid: User id to send the audio.
    :param str media_url: Url of a hosted media.
    :param str file_type: 'image'/'audio'/'video'/'file'.
    :param bool is_reusable: Defines the attachment to be resusable, \
    the response will have an attachment_id that can be used to \
    re-send the attachment without need to upload it again. (You can \
    use the post_reusable_attachment method to upload using the id).
    :param str messaging_type: Identifies the message type from: RESPONSE,\
    UPDATE AND MESSAGE_TAG (Default: RESPONSE, if MESSAGE_TAG, tag param \
    is required)
    :param str tag: Tag classifying the message, must be one of the \
    following `tags <https://developers.facebook.com/docs/messenger-\
    platform/send-messages/message-tags#supported_tags>`_
    :return: `Response object <http://docs.python-requests.org/en/\
    master/api/#requests.Response>`_
    :facebook docs: `/contenttypes <https://developers.facebook.\
    com/docs/messenger-platform/send-api-reference/contenttypes>`_
    """
    MESSAGES_URL = ("https://graph.facebook.com/v2.6/me/"
                    "messages?access_token={access_token}")
    url = MESSAGES_URL.format(access_token=ACCESS_TOKEN)
    payload = dict()
    payload['recipient'] = {'id': fbid}
    payload['messaging_type'] = messaging_type
    if bool(tag) or messaging_type == "MESSAGE_TAG":
        payload['tag'] = tag
    attachment_payload = dict()
    attachment_payload['url'] = media_url
    if is_reusable:
        attachment_payload['is_reusable'] = is_reusable
    attachment = {"type": file_type, "payload": attachment_payload}
    payload['message'] = {"attachment": attachment}
    data = json.dumps(payload)
    status = requests.post(url, headers=HEADER, data=data)
    return status






if __name__ == "__main__":
    app.run()
