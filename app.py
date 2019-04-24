# coding: utf-8
# more examples: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/README.md
import telegram
from pymongo import MongoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Job,JobQueue
import logging
import os
import StateMachine
import OxfordDictionary
from bson.binary import Binary
import pickle
import subscriptions
import random
from datetime import time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
TG_TOKEN = os.environ['TG_TOKEN']
MONGODB_URI = os.environ['MONGODB_URI']
client = MongoClient(MONGODB_URI)
db = client.chatbot_db
user_state_collection = db.user_state_collection
states = {}

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def call_back_buttons(bot, update):
    print('CALL BACK BABY!')
    message_text = update.callback_query.data
    if update.callback_query.data == "Examples":
                s_m_bytes = user_state_collection.posts.find_one({'user_id': update.callback_query.message.chat_id})
                user_state_machine = pickle.loads(s_m_bytes['state_machine'])
                examples = ""
                if "examples" in user_state_machine.data:
                    examples = user_state_machine.data["examples"]
                else:
                    examples = OxfordDictionary.oxford_dic_request(message_text.split(".", 1)[1])["examples"]
                bot.sendMessage(update.callback_query.message.chat_id, text=examples)
    if update.callback_query.data == "Synonyms-Antonyms":
        s_m_bytes = user_state_collection.posts.find_one({'user_id': update.callback_query.message.chat_id})
        user_state_machine = pickle.loads(s_m_bytes['state_machine'])
        syn_ant = {}
        if "word_id" in user_state_machine.data:
            syn_ant = OxfordDictionary.oxford_dic_syn_ant(user_state_machine.data["word_id"])
        else:
            syn_ant = OxfordDictionary.oxford_dic_syn_ant(message_text.split(".", 1)[1])

        bot.sendMessage(update.callback_query.message.chat_id, text=syn_ant["synonyms"])
        bot.sendMessage(update.callback_query.message.chat_id, text=syn_ant["antonyms"])

    if update.callback_query.data == "Pronunciation":
        s_m_bytes = user_state_collection.posts.find_one({'user_id': update.callback_query.message.chat_id})
        user_state_machine = pickle.loads(s_m_bytes['state_machine'])
        attachment = ""
        if "attachment" in user_state_machine.data:
            attachment = user_state_machine.data["attachment"]
        else:
            attachment = OxfordDictionary.oxford_dic_request(message_text.split(".", 1)[1])[
                "attachment"]
        if attachment == "" or attachment =="Couldn't find any audio":
            bot.sendMessage(update.callback_query.message.chat_id, text="Couldn't find any pronunciation samples...")
        else:
            url = attachment
            print(url)
            bot.sendAudio(update.callback_query.message.chat_id, audio=url)

def idle_main(bot, update):
    response_dic = get_message(update.message.chat_id, update.message.text)
    if "buttons" in response_dic:
        titles = [x['title'] for x in response_dic['buttons']]
        button_list = [InlineKeyboardButton(x, callback_data=x) for x in titles]
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        bot.sendMessage(update.message.chat_id, response_dic["text"], reply_markup=reply_markup)
    elif "elements" in response_dic:
        titles = [response_dic["elements"][0]['buttons'][0]['title']]
        button_list = [InlineKeyboardButton(x, url=response_dic["elements"][0]['buttons'][0]['url']) for x in titles]
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        bot.sendPhoto(update.message.chat_id, response_dic["elements"][0]["image_url"])
        bot.sendMessage(update.message.chat_id, response_dic["elements"][0]['title'], reply_markup=reply_markup)
        logging.info("echoing some message...")
    else:
        bot.sendMessage(update.message.chat_id, text=response_dic["text"])
        logging.info("echoing some message...")
'''
    elif "image" in response_dic:
        bot.send_image_url(recipient_id, response_dic["image"])
        send_message(recipient_id, response_dic["text"])
    else:
        send_message(recipient_id, response_dic["text"])

    if "attachment" in response_dic:
        bot.send_audio_url(recipient_id, response_dic["attachment"])
 elements.append({
                    "title": podcasts[x]['title'],
                    "image_url": podcasts[x]['img'],
                    "subtitle": podcasts[x]['description'],
                    "default_action": {
                        "type": "web_url",
                        "url": podcasts[x]['link'],
                        "webview_height_ratio": "tall",
                    },
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": podcasts[x]['link'],
                            "title": "Listen!"
                        }, {
                            "type": "postback",
                            "title": payload,
                            "payload": payload+"_"+tag
                        }
                    ]
                })'''



def slash_start(bot, update):
    bot.sendMessage(update.message.chat_id, text="Привет! Я - Дживс, бот для изучения английского!\n Могу порекомендовать вам ресурсы для аудирования, подписывать на тематические подкасты и даже управлять вашим личным словарем! Попробуйте что нибудь их этого:\n- добавь <слово> в мой словарь\n- скинь что нибудь послушать на английском\n- Что значит <слово>?")
    logging.info("replying start command...")

def get_message(user_id, message):
    # sample_responses = [classify(message)]
    # return selected item to the user
    # return random.choice(sample_responses)
    respose_dic = {}


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
        respose_dic = {
            "text": "Hi! I'm English learning bot.\n You can ask for listening resources, subscribe for stuff and manage your vocabulary to learn. Try something of that:\n # add a word to my dictionary\n # give me some listening resources\n # what does /something/ mean?"}
    return respose_dic


def callback_daily(bot, job):
        # SEND THE PHRASE OF THE DAY
        phrase_of_the_day_collection = db.phrase_of_the_day_collection
        dic = {"text": "I don't know this word", "attachment": None, "examples": None}
        type_of_phrase = ""
        while dic["text"] == "I don't know this word":
            types = ['idioms', 'phrasal_verbs']
            type_of_phrase = random.choice(types)
            result = phrase_of_the_day_collection.posts.find_one({'type': type_of_phrase})
            phrase = result["phrase"][result["current_number"] % len(result["phrase"])]
            dic = OxfordDictionary.oxford_dic_request(phrase)

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

            bot.sendPhoto(user_id, "https://image.ibb.co/kEx6oK/phrase_of_the_day.png")
            titles = [x['title'] for x in buttons]
            button_list = [InlineKeyboardButton(x, callback_data=x) for x in titles]
            reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
            bot.sendMessage(user_id, text, reply_markup=reply_markup)

        # update number
        phrase_of_the_day_collection.posts.update_one({'type': type_of_phrase}, {"$inc": {'current_number': +1}},upsert=True)


def main():
    updater = Updater(TG_TOKEN)
    job = updater.job_queue
    job.run_repeating(callback_daily, interval=60, first=0)

    job.run_daily(callback_daily, time(21,3), context=None, name=None)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", slash_start), group=0)
    dp.add_handler(MessageHandler(Filters.text, idle_main))
    dp.add_handler(CallbackQueryHandler(call_back_buttons))
    logging.info("starting polling")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

