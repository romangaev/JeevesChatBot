# coding: utf-8
# more examples: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/README.md
from pymongo import MongoClient
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
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

def idle_main(bot, update):
    response_dic = get_message(update.message.chat_id, update.message.text)

    bot.sendMessage(update.message.chat_id, text=response_dic["text"])
    logging.info("echoing some message...")

def slash_start(bot, update):
    bot.sendMessage(update.message.chat_id, text="Hello! I'm Jeeves, English learning bot!")
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
    logging.info("starting polling")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

