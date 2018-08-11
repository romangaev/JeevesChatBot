import testclass
import pickle
import StateMachine
from bson.binary import Binary
from pymongo import MongoClient
MONGODB_URI = 'mongodb://rgaev:iha492081@ds115592.mlab.com:15592/chatbot_db'
client = MongoClient(MONGODB_URI)
db = client.chatbot_db
user_state_collection=db.user_state_collection
user_id='test'

newinstace = StateMachine.StateMachine("default")
newinstace.printing_state()


newinstace.change_state("dictadd")
s_m_bytes = pickle.dumps(newinstace)

post = {'user_id': user_id, 'state_machine': Binary(s_m_bytes)}
user_state_collection.posts.update_one({'user_id': user_id},{"$set": post}, upsert=False)
s_m_bytes = user_state_collection.posts.find_one({'user_id': user_id})
loaded = pickle.loads(s_m_bytes['state_machine'])
loaded.printing_state()
print(loaded.state_respond("skjbveskejsnrc"))

