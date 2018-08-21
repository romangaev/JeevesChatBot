from random import shuffle

import nltk
from nltk import pos_tag, word_tokenize
from pymongo import MongoClient
'''
MONGODB_URI ="mongodb://rgaev:iha492081@ds115592.mlab.com:15592/chatbot_db"
client = MongoClient(MONGODB_URI)
db = client.chatbot_db
phrase_of_the_day_collection = db.phrase_of_the_day_collection

dic =phrase_of_the_day_collection.posts.find_one({"type":"idioms"})
list=dic["phrase"]
shuffle(list)
phrase_of_the_day_collection.posts.update_one({"type":"idioms"},{ '$set':{"phrase":list}})'''



def get_subject(sentence):
    pos_results = pos_tag(word_tokenize(sentence.lower()))
    print(pos_results)
    chunkGram=r"""  NPH: {<RB|DT|JJ|NN.*>+|<VB.*><RP.*>|<VB.*><IN.*>}      
      PPH: {<IN><NP>}             
      VPH: {<VB.*><NP|PP|CLAUSE>+$} 
      CLAUSE: {<NP><VP>}           """
    chunkParser= nltk.RegexpParser(chunkGram)
    chunked = chunkParser.parse(pos_results)
    print(chunked)
    list=[]
    word=[]
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'NPH'):
        # print the noun phrase as a list of part-of-speech tagged words
        list.append(subtree.leaves())
    # found some chunks
    if not list==[]:
            word=list[-1]
    result=""
    if not word==[]:
        for item in word:
            result+=item[0]
            result+=" "

    return result.rstrip()

print(get_subject("some technology podcasts please"))