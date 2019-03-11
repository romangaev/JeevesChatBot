# coding: utf-8
# more examples: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/README.md
import telegram
from pymongo import MongoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging
import os
import StateMachine
import OxfordDictionary
from bson.binary import Binary
import pickle
import subscriptions

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
    print(type(bot))
    print(type(update.callback_query.message))

    if update.callback_query.data == "Examples":
                message_text = update.callback_query.data
                s_m_bytes = user_state_collection.posts.find_one({'user_id': update.callback_query.message.chat_id})
                user_state_machine = pickle.loads(s_m_bytes['state_machine'])
                examples = ""
                if "examples" in user_state_machine.data:
                    examples = user_state_machine.data["examples"]
                else:
                    examples = OxfordDictionary.oxford_dic_request(message_text.split(".", 1)[1])["examples"]

                bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.chat_id, text=examples)
    if update.callback_query.data == "Synonyms-Antonyms":
                bot.edit_message_text(chat_id=update.message.chat_id, message_id=update.message.chat_id, text="Пыщь")
    if update.callback_query.data == "Pronunciation":
                bot.edit_message_text(chat_id=update.message.chat_id, message_id=update.message.chat_id, text="Пыщь")

def idle_main(bot, update):
    response_dic = get_message(update.message.chat_id, update.message.text)
    if "buttons" in response_dic:
        titles = [x['title'] for x in response_dic['buttons']]
        button_list = [InlineKeyboardButton(x, callback_data=x) for x in titles]
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        bot.sendMessage(update.message.chat_id, response_dic["text"], reply_markup=reply_markup)
        logging.info("echoing some message...")
    else:
        bot.sendMessage(update.message.chat_id, text=response_dic["text"])
        logging.info("echoing some message...")
    '''elif "elements" in response_dic:
        bot.send_generic_message(recipient_id, response_dic["elements"])
    elif "image" in response_dic:
        bot.send_image_url(recipient_id, response_dic["image"])
        send_message(recipient_id, response_dic["text"])
    else:
        send_message(recipient_id, response_dic["text"])

    if "attachment" in response_dic:
        bot.send_audio_url(recipient_id, response_dic["attachment"])
'''
    ''' elements.append({
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

def main():
    updater = Updater(TG_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", slash_start), group=0)
    dp.add_handler(MessageHandler(Filters.text, idle_main))
    dp.add_handler(CallbackQueryHandler(call_back_buttons))
    logging.info("starting polling")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

