import json
import os
import random
from pymongo import MongoClient
from nltk import word_tokenize, pos_tag
from tensorBot import classify


class StateMachine:

    def __init__(self, state):
        self.state = state
        self.data = {}
        with open('intents.json') as json_data:
            self.intents = json.load(json_data)

    def state_respond(self, message):


        # classify the intent and get a new state
        intent_matrix = classify(message)
        intent = intent_matrix[0][0]
        confidence = intent_matrix[0][1]
        new_state = ''
        response = 'default'
        for every in self.intents['intents']:
            if every['tag'] == intent:
                new_state = every['state']

        # first lets take a look at the states
        # if initial state is empty then there is no context - just go straight to intents
        if self.state == '':

            if confidence < 0.3:
                response = "Not sure what you mean"
            elif intent == 'dictopen':
                response = random.choice(self.intents['intents'][4]['responses'])
                # DB
            elif intent == 'dictadd':

                response = self.dict_add_transitions(message,intent,confidence,new_state)

               # post = {'user_id': ['']}
              #  post[]
               # posts = db.posts
               # post_id = posts.insert_one(post).inserted_id

            elif intent == 'info':
                response = random.choice(self.intents['intents'][1]['responses'])
            elif intent == 'greeting':
                response = random.choice(self.intents['intents'][0]['responses'])
            print(response)
            print(intent)
            print('StateMachineState:'+ self.state)
            #dont forget to change the state
            self.state = new_state
            print('StateMachineState:' + self.state)
        elif self.state == 'dictadd':
            response = self.dict_add_transitions(message,intent,confidence,new_state)
        return response
    def dict_add_transitions(self, sentence, intent, confidence, new_state):
        print('inside dict add method')
        print(self.data)
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
            if word_to_add.__contains__('something') or word_to_add.__contains__('a word') or word_to_add.__contains__('word'):
                word_to_add = ''

            # change the state
            self.state = 'dictadd'
            print("word to add:"+word_to_add)
            # if we didnt find the word then ask for the word
            if word_to_add == '':
                respond = random.choice(self.intents['intents'][5]['responses_if_not_given'])
            else:
                self.data['dictadd'] = word_to_add
                respond = random.choice(self.intents['intents'][5]['responses_if_word_given']) + " Add to your dictionary:" + word_to_add +". Right?"
        # if will get some confirmation
        elif self.state == 'dictadd' and self.data:
            print('inside dictadd+data')
            if intent == 'confirmation':
                # DBQUERY

                respond = self.data['dictadd']+' added!'
                self.data = {}
                self.state = ''
            elif intent == 'rejection':
                # user wants some other word
                self.data = {}
                respond = random.choice(self.intents['intents'][5]['responses_if_not_given'])
        elif self.state == 'dictadd' and not self.data:
            print('inside dictadd+no data')
            # adding a word
            # DBQUERY
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
    def change_state(self,state):
        self.state=state








