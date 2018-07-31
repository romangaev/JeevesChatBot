

training_data = []
training_data.append({"greeting","how are you?"})
training_data.append({"greeting","how is your day?"})
training_data.append({"greeting","good day"})
training_data.append({"greeting","how is it going today?"})
training_data.append({"greeting","hi"})
training_data.append({"greeting","hey"})
training_data.append({"greeting","hello"})




training_data.append({"goodbye", "have a nice day"})
training_data.append({"goodbye", "see you later"})
training_data.append({"goodbye", "have a nice day"})
training_data.append({"goodbye", "goodbye"})

training_data.append({"english", "learning"})
training_data.append({"english", "study"})
training_data.append({"english", "English"})
training_data.append({"english", "training"})
training_data2 = zip(*training_data)


from sklearn.feature_extraction.text import CountVectorizer
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(list(training_data2)[1])
print(X_train_counts.shape)

from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
print(X_train_tfidf.shape)

from sklearn.naive_bayes import MultinomialNB
clf = MultinomialNB().fit(X_train_tfidf, list(training_data2)[0])
docs_new = ['Wanna learn something new today', 'good morning mate', 'see you later, its time to leave!']
X_new_counts = count_vect.transform(docs_new)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)
predicted = clf.predict(X_new_tfidf)
for doc, category in zip(docs_new, predicted):
    print('%r => %s' % (doc, twenty_train.target_names[category]))