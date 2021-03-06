import json
import os
import random

import nltk
from pymongo import MongoClient
from nltk import word_tokenize, pos_tag

import subscriptions
from tensorBot import classify
import OxfordDictionary

MONGODB_URI = os.environ['MONGODB_URI']


class StateMachine:
    client = MongoClient(MONGODB_URI)
    db = client.chatbot_db

    def __init__(self, state, user_id):
        self.state = state
        self.data = {}
        self.user_id = user_id
        self.intents = ""

    def state_respond(self, message):
        response = {}

        with open('intents.json') as json_data:
            self.intents = json.load(json_data)

        # classify the intent and get a new state
        intent_matrix = classify(message)
        if message.lower().startswith(("what is","what does")) :
            intent_matrix=[("oxford_dic",0.99)]

        print(intent_matrix)
        intent="none"
        confidence=0.0
        if not intent_matrix==[]:
            intent = intent_matrix[0][0]
            confidence = intent_matrix[0][1]

        new_state = ''
        number_of_intent = 0

        for every in self.intents['intents']:
            if every['tag'] == intent:
                new_state = every['state']
                break
            number_of_intent += 1


        print(intent)
        # first lets take a look at the states
        # if initial state is empty then there is no context - just go straight to intents
        if self.state == '':
            self.data = {}
            if confidence > 0.3 and intent == 'info':
                response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses'])
            elif confidence < 0.4:
                response["text"] = random.choice(["Эм... Не уверен, что понимаю о чем ты :)", "Что, прости? Не уверен, что я должен здесь ответить!\n Вероятно, тебе стоить попросить меня о помощи, и я подскажу, что я умею!"])
            elif intent == 'dictopen':
                response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses'])
                user_vocab_collection = StateMachine.db.user_vocab_collection
                result = user_vocab_collection.posts.find_one({'user_id': self.user_id})
                response["image"] = 'https://image.ibb.co/gT74Ce/vocab.png'
                if result is not None:
                    response["text"] += '\n'
                    response["text"] += '\n'
                    for every in result['vocabulary']:
                        response["text"] += every
                        response["text"] += '\n'

            elif intent == 'oxford_dic':
                response = self.oxford_dic_transitions(message)
            elif intent == 'listening':
                response = self.listening_transitions(message, intent, confidence, new_state)
            elif intent == 'dictadd':
                response = self.dict_add_transitions(message, intent, confidence, new_state)
            else:
                response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses'])

            print(confidence)
            print('StateMachineState:' + self.state)
            # dont forget to change the state
            self.state = new_state
            print('StateMachineState:' + self.state)

        elif self.state == 'dictadd':
            response = self.dict_add_transitions(message, intent, confidence, new_state)
        elif self.state == 'listening':
            response = self.listening_transitions(message, intent, confidence, new_state)
        elif self.state == 'dictclean':
            response = self.dictclean_transitions(message, intent, confidence, new_state)

        return response


    def listening_transitions(self, sentence, intent, confidence, new_state):
        response = {}
        tag=""
        number_of_intent = 0
        for every in self.intents['intents']:
            if every['tag'] == 'listening':
                break
            number_of_intent += 1

        if self.state == '':
            response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses'])
        else:

            podcasts = []
            if "спорт" in sentence.lower() or "футбол" in sentence.lower():
                podcasts = subscriptions.get_podcasts('football')
                tag="football"
            elif "английский" in sentence.lower() or "english" in sentence.lower() or "язык" in sentence.lower():
                podcasts = subscriptions.get_podcasts('english')
                tag = 'english'
            elif "дискавери" in sentence.lower() or "discovery" in sentence.lower():
                podcasts = subscriptions.get_podcasts('discovery')
                tag = 'discovery'
            elif "новости" in sentence.lower() or "news" in sentence.lower():
                podcasts = subscriptions.get_podcasts("news")
                tag = "news"
            else:
                response["text"] = "Упс, кажется такого у меня еще нет!"
                return response

            payload='SUBSCRIBE'
            if subscriptions.check_subscription(self.user_id,tag):
                payload ='UNSUBSCRIBE'
            print(payload)

            elements = []
            for x in range(0, 5):
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
                })
                response["elements"] = elements
                self.state=""
        return response

    def oxford_dic_transitions(self, message):
        self.data["word_id"] = get_subject_oxf(message.replace("'", "").replace('"', ""))
        print("word_id")
        print(self.data["word_id"])
        response = {"text": "Не нашлось такого слова! Проверьте грамматику -  у меня сложно с распознанием ошибок :)"}
        if (self.data["word_id"].isalpha()):
            number_of_intent = 0
            for every in self.intents['intents']:
                if every['tag'] == 'oxford_dic':
                    break
                number_of_intent += 1

            # response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses'])
            query_result = OxfordDictionary.oxford_dic_request(self.data["word_id"])
            response["text"] = query_result["text"]

            if not response["text"] == "404":
                response["buttons"] = self.intents['intents'][number_of_intent]['buttons']
            else: response["text"] = "Не нашлось такого слова! Проверьте грамматику -  у меня сложно с распознанием ошибок :)"
            self.data["examples"] = query_result["examples"]
            self.data["attachment"] = query_result["attachment"]
        return response

    def dictclean_transitions(self, sentence, intent, confidence, new_state):
        response = {}
        if intent == 'confirmation' or "yes" in sentence.lower():
            # DBQUERY
            user_vocab_collection = StateMachine.db.user_vocab_collection
            user_vocab_collection.posts.update_one({'user_id': self.user_id},
                                                   {"$set": {'vocabulary': []}})

            response["text"]='Done. Those words were cleared...Literally...And no one will ever find their grave...'
            response["attachment"] = "http://www.noiseaddicts.com/samples_1w72b820/3727.mp3"
            self.state = ""
            self.data = {}

        elif intent == 'rejection' or "no" in sentence.lower():
            response["text"] = 'Okay. Let\'s have a spare on these words and keep them until we need... For a while.'
            self.state = ""
            self.data = {}

        elif confidence > 0.7 and not intent == 'dictclean':
            self.state=""
            self.data={}
            response = self.state_respond(sentence)
            response["text"] = "Okay, as you say, no more cleaning!\n" + response["text"]
        else:
            response["text"] = "Wait, are you still going to clean your vocabulary?"
        return response

    def dict_add_transitions(self, sentence, intent, confidence, new_state):
        print('inside dict add method')
        print(self.data)
        number_of_intent = 0
        for every in self.intents['intents']:
            if every['tag'] == 'dictadd':
                break
            number_of_intent += 1
        response={}
        response["text"] = 'I didn\'t get you'
        # if we are entering dictadd context

        if self.state == '' and new_state == 'dictadd':
            print('inside entering dict add context')

            # retrieving the word to add
            word_to_add=get_subject_dicadd(sentence.replace("'", "").replace('"', ""))

            if word_to_add.__contains__('something') or word_to_add.__contains__('a word') or word_to_add.__contains__(
                    'word'):
                word_to_add = ''

            # change the state
            self.state = 'dictadd'
            print("word to add:" + word_to_add)
            # if we didnt find the word then ask for the word
            if word_to_add == '':
                response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses_if_not_given'])
            else:
                self.data['dictadd'] = word_to_add
                response["text"] = random.choice(self.intents['intents'][number_of_intent][
                                            'responses_if_word_given']) + " Add to your dictionary:" + word_to_add + ". Right?"
        # if will get some confirmation
        elif self.state == 'dictadd' and self.data:
            print('inside dictadd+data')
            if intent == 'confirmation' or sentence.lower() == "yes":
                # DBQUERY
                user_vocab_collection = StateMachine.db.user_vocab_collection
                user_vocab_collection.posts.update_one({'user_id': self.user_id},
                                                       {"$push": {'vocabulary': self.data['dictadd']}}, upsert=True)

                response["text"] = self.data['dictadd'] + ' added!'
                self.data = {}
                self.state = ''
            elif intent == 'rejection' or sentence.lower() == "no":
                # user wants some other word
                self.data = {}
                self.state = 'dictadd'
                response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses_if_not_given'])
            elif confidence>0.7 and not intent=="dictadd":
                self.state = ''
                self.data = {}
                response = self.state_respond(sentence)
                response["text"] = "Okay, as you say, no more Your Vocab!\n"+response["text"]
            else:
                response["text"] = 'I didn\'t get you. Are we adding "'+ self.data['dictadd']+'" to Your Vocab?'


        elif self.state == 'dictadd' and not self.data:
            print('inside dictadd+no data')
            # adding a word
            # DBQUERY
            user_vocab_collection = StateMachine.db.user_vocab_collection
            user_vocab_collection.posts.update_one({'user_id': self.user_id}, {"$push": {'vocabulary': sentence}},
                                                   upsert=True)
            self.data = {}
            self.state = ''
            print('almost added...' + sentence)
            response["text"] = 'Done. "'+sentence + '" - added!'
            print(type(response))
        return response

    def printing_state(self):
        print(self.state)

    def change_state(self, state):
        self.state = state

# POS and CHUNKING
def get_subject_oxf(sentence):
    import unicodedata as ud
    latin_letters = {}
    def is_latin(uchr):
        try:
            return latin_letters[uchr]
        except KeyError:
            return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

    def only_roman_chars(unistr):
        return all(is_latin(uchr)
                   for uchr in unistr
                   if uchr.isalpha())  # isalpha suggested by John Machin


    result = ""
    for every in word_tokenize(sentence.lower()):
        if only_roman_chars(every):
            result = result+every+' '


    return result.rstrip()
    '''
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
        if pos_results[0][1].startswith('W') and pos_results[1][1].startswith('V'):
            word = chunk_list[0]
        else:
            word = chunk_list[-1]


    # didnt find any chunks
    if word == 'default':
        if pos_results[0][1].startswith('W') and pos_results[1][1].startswith('V'):
            word = pos_results[2]
        else:
            word = pos_results[-1]

    result=""
    if isinstance(word,list):
        if word[0][1] == 'DT':
            word.__delitem__(0)
        for every in word:
            result+=every[0]
            result+=" "
    else:
        result=word[0]
    return result.rstrip()'''


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
    word = ""
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
        result = word
    result = result.rstrip().rsplit(' ', 1)[0]
    return result



