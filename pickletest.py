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



def get_subject_dicadd(sentence):
    pos_results = pos_tag(word_tokenize(sentence.lower()))
    print(pos_results)
    chunkGram = r"""  NPH: {<RB|DT|JJ|NN.*>+<IN|TO>|<VB.*><RP.*><IN|TO>|<VB.*><IN.*><IN|TO>|<VB.*><IN|TO>}      
      PPH: {<IN><NP>}             
      VPH: {<VB.*><NP|PP|CLAUSE>+$} 
      CLAUSE: {<NP><VP>}           """
    chunkParser = nltk.RegexpParser(chunkGram)
    chunked = chunkParser.parse(pos_results)
    print(chunked)
    chunk_list = []
    word = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'NPH'):
        # print the noun phrase as a list of part-of-speech tagged words
        chunk_list.append(subtree.leaves())
    # found some chunks
    if not chunk_list == []:
            word=chunk_list[-1]
    result = ""
    if isinstance(word, list):
        if word[0][1] == 'DT':
            word.__delitem__(0)
        for every in word:
            result += every[0]
            result += " "
    else:
        result = word[0]
    result= result.rstrip().rsplit(' ', 1)[0]
    return result


print(get_subject_dicadd("I wanna add amazing to my dictionary"))