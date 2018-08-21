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
    chunkGram = r"""  NPH: {<NN.*>|<RB|DT|JJ.*>+<NN.*>|<VB.*><RP.*>|<VB.*><IN.*>}     
          PPH: {<IN><NP>}             
          VPH: {<VB.*><NP|PP|CLAUSE>+$} 
          CLAUSE: {<NP><VP>}           """
    chunkParser = nltk.RegexpParser(chunkGram)
    chunked = chunkParser.parse(pos_results)
    print(chunked)
    chunk_list = []
    word = 'default'
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'NPH'):
        # print the noun phrase as a list of part-of-speech tagged words
        chunk_list.append(subtree.leaves())
    # found some chunks
    if not chunk_list == []:
        if pos_results[0][1] == 'WP' and pos_results[1][1] == 'VBZ':
            word = chunk_list[0]
        else:
            word = chunk_list[-1]


    # didnt find any chunks
    if word == 'default':
        if pos_results[0][1] == 'WP' and pos_results[1][1] == 'VBZ':
            word = pos_results[2]
        else:
            word = pos_results[-1]

    result=""
    if isinstance(word,list):
        for every in word:
            result+=every[0]
            result+=" "
    else:
        result=word[0]
    return result.rstrip()

print(get_subject("what does ahuenno mean"))