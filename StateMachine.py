import json
import os
import random
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
        with open('intents.json') as json_data:
            self.intents = json.load(json_data)

        # classify the intent and get a new state
        intent_matrix = classify(message)
        intent = intent_matrix[0][0]
        confidence = intent_matrix[0][1]
        new_state = ''
        number_of_intent = 0
        response = {}
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
            if confidence < 0.4:
                response["text"] = "Not sure what you mean"
            elif intent == 'dictopen':
                response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses'])
                user_vocab_collection = StateMachine.db.user_vocab_collection
                result = user_vocab_collection.posts.find_one({'user_id': self.user_id})

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
            else:
                response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses'])

            print(confidence)
            print('StateMachineState:' + self.state)
            # dont forget to change the state
            self.state = new_state
            print('StateMachineState:' + self.state)

        elif self.state == 'dictadd':
            response["text"] = self.dict_add_transitions(message, intent, confidence, new_state)
        elif self.state == 'listening':
            response = self.listening_transitions(message, intent, confidence, new_state)
        elif self.state == 'dictclean':
            response = self.dictclean_transitions(message, intent, confidence, new_state)
        # elif self.state == 'listening':
        # response = self.listening_transitions(message, intent, confidence, new_state)

        return response

    def dictclean_transitions(self, sentence, intent, confidence, new_state):
        response ={}
        if intent == 'confirmation' or "yes" in sentence.lower():
            # DBQUERY
            user_vocab_collection = StateMachine.db.user_vocab_collection
            user_vocab_collection.posts.update_one({'user_id': self.user_id},
                                                   {"$set": {'vocabulary': []}})

            response["text"]='Done. Those words were cleared...Literally...And no one will ever find their grave...'
            response["attachment"] = "http://www.noiseaddicts.com/samples_1w72b820/3727.mp3"

        elif intent == 'rejection' or "no" in sentence.lower():
            response["text"] = 'Okay. Let\'s have a spare on these words and keep them until we need... For a while.'

        self.state = ''
        return response




    def listening_transitions(self, sentence, intent, confidence, new_state):
        response = {}
        number_of_intent = 0
        for every in self.intents['intents']:
            if every['tag'] == 'listening':
                break
            number_of_intent += 1

        if self.state == '':
            response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses'])
        else:

            podcasts = []
            if "sports" in sentence.lower() or "football" in sentence.lower():
                podcasts = subscriptions.get_podcasts('football')
            elif "english" in sentence.lower() or "learning" in sentence.lower():
                podcasts = subscriptions.get_podcasts('english')
            elif "politics" in sentence.lower() or "government" in sentence.lower():
                podcasts = subscriptions.get_podcasts('politics')
            elif "science" in sentence.lower() or "research" in sentence.lower():
                podcasts = subscriptions.get_podcasts('politics')
            elif "analytics" in sentence.lower() or "longreads" in sentence.lower():
                podcasts = subscriptions.get_podcasts('longreads')
            elif "technology" in sentence.lower() or "tech" in sentence.lower():
                podcasts = subscriptions.get_podcasts('technology')
            elif "global" in sentence.lower() or "society" in sentence.lower() or "environment" in sentence.lower():
                podcasts = subscriptions.get_podcasts('global')
            else:
                response["text"] = "Hm...Sorry, I don't have anything about it"
                return response

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
                            # TODO implement subscription
                            "type": "postback",
                            "title": "Subscribe",
                            "payload": "DEVELOPER_DEFINED_PAYLOAD"
                        }
                    ]
                })
                response["elements"]=elements
                self.state=""
        return response


    def oxford_dic_transitions(self, message):
        self.data["word_id"] = word_tokenize(message.replace("'", "").replace('"', ""))[-1].lower()
        print("word_id")
        print(self.data["word_id"])
        response = {"text": "no_text"}
        if (self.data["word_id"].isalpha()):
            number_of_intent = 0
            for every in self.intents['intents']:
                if every['tag'] == 'oxford_dic':
                    break
                number_of_intent += 1

            # response["text"] = random.choice(self.intents['intents'][number_of_intent]['responses'])
            query_result = OxfordDictionary.oxford_dic_request(self.data["word_id"])
            response["text"] = query_result["text"]
            response["attachment"] = query_result["attachment"]
            if not response["text"] == "I don't know this word":
                response["buttons"] = self.intents['intents'][number_of_intent]['buttons']
            self.data["examples"] = query_result["examples"]

            print("Attachment url:")
            print(response["attachment"])
        return response

    def dict_add_transitions(self, sentence, intent, confidence, new_state):
        print('inside dict add method')
        print(self.data)
        number_of_intent = 0
        for every in self.intents['intents']:
            if every['tag'] == 'dictadd':
                break
            number_of_intent += 1
        respond = 'I didn\'t get you'
        # if we are entering dictadd context

        if self.state == '' and new_state == 'dictadd':
            print('inside entering dict add context')
            # retrieving the word to add
            pos_results = pos_tag(word_tokenize(sentence.lower()))
            index_vocab = 0
            for i in range(0, len(pos_results)):
                if pos_results[i][0] == 'dictionary' or pos_results[i][0] == 'vocabulary':
                    index_vocab = i
                    break
            index_prep = 0
            index_begin = 0
            for i in range(index_vocab, 0, -1):
                if pos_results[i][1] == 'IN' or pos_results[i][1] == 'TO':
                    index_prep = i
                if pos_results[i][1] == 'VB':
                    index_begin = i + 1
                    break
            word_to_add = ''
            for i in range(index_begin, index_prep):
                word_to_add = word_to_add + pos_results[i][0] + ' '
            if word_to_add.__contains__('something') or word_to_add.__contains__('a word') or word_to_add.__contains__(
                    'word'):
                word_to_add = ''

            # change the state
            self.state = 'dictadd'
            print("word to add:" + word_to_add)
            # if we didnt find the word then ask for the word
            if word_to_add == '':
                respond = random.choice(self.intents['intents'][number_of_intent]['responses_if_not_given'])
            else:
                self.data['dictadd'] = word_to_add
                respond = random.choice(self.intents['intents'][number_of_intent][
                                            'responses_if_word_given']) + " Add to your dictionary:" + word_to_add + ". Right?"
        # if will get some confirmation
        elif self.state == 'dictadd' and self.data:
            print('inside dictadd+data')
            if intent == 'confirmation' or sentence.lower == "yes":
                # DBQUERY
                user_vocab_collection = StateMachine.db.user_vocab_collection
                user_vocab_collection.posts.update_one({'user_id': self.user_id},
                                                       {"$push": {'vocabulary': self.data['dictadd']}}, upsert=True)

                respond = self.data['dictadd'] + ' added!'
                self.data = {}
                self.state = ''
            elif intent == 'rejection' or sentence.lower == "no":
                # user wants some other word
                self.data = {}
                respond = random.choice(self.intents['intents'][number_of_intent]['responses_if_not_given'])
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
            respond = sentence + ' - added!'
            print(type(respond))
        else:
            respond = 'I dont know'
        return respond

    def printing_state(self):
        print(self.state)

    def change_state(self, state):
        self.state = state
