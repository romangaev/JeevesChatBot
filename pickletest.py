import nltk


message = 'tell me about "separation"'

print(nltk.word_tokenize(message.replace("'","").replace('"',""))[-1].lower())