from pymongo import MongoClient

MONGODB_URI ="mongodb://rgaev:iha492081@ds115592.mlab.com:15592/chatbot_db"
client = MongoClient(MONGODB_URI)
db = client.chatbot_db
phrase_of_the_day_collection = db.phrase_of_the_day_collection

phrase_of_the_day_collection.posts.update_one({'type': 'phrasal_verbs'}, {"$set": {'current_number': 0}}, upsert=True)
phrase_of_the_day_collection.posts.update_one({'type': 'idioms'}, {"$set": {'current_number': 0}}, upsert=True)