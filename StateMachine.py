import json
import random

class StateMachine:

    def __init__(self, state):
        self.state=state
        self.data={}

    def state_respond(self,intent,confidence,new_state):
        with open('intents.json') as json_data:
            intents = json.load(json_data)
        response='didnt get ya'
        if confidence<0.3:
            return response
        elif intent == 'dictopen':
            response = random.choice(intents['intents'][4]['responses'])
            #DB QUERY
        elif intent == 'dictadd':
            response = random.choice(intents['intents'][5]['responses'])
            #DB QUERY
        elif intent == 'info':
            response=random.choice(intents['intents'][1]['responses'])
        elif intent == 'greeting':
            response=random.choice(intents['intents'][0]['responses'])
        return response
