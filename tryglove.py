class Embedding(object):
    def __init__(self,vocab_file,vectors_file):
        with open(vocab_file, 'r') as f:
            words = [x.rstrip().split(' ')[0] for x in f.readlines()]

        with open(vectors_file, 'r') as f:
            vectors = {}
            for line in f:
                vals = line.rstrip().split(' ')
                vectors[vals[0]] = [float(x) for x in vals[1:]]

        vocab_size = len(words)
        vocab = {w: idx for idx, w in enumerate(words)}
        ivocab = {idx: w for idx, w in enumerate(words)}

        vector_dim = len(vectors[ivocab[0]])
        W = np.zeros((vocab_size, vector_dim))
        for word, v in vectors.items():
            if word == '<unk>':
                continue
            W[vocab[word], :] = v

        # normalize each word vector to unit variance
        W_norm = np.zeros(W.shape)
        d = (np.sum(W ** 2, 1) ** (0.5))
        W_norm = (W.T / d).T

        self.W = W_norm
        self.vocab = vocab
        self.ivocab = ivocab

def find_similar_words(embed,text,refs,thresh):

    C = np.zeros((len(refs),embed.W.shape[1]))

    for idx, term in enumerate(refs):
        if term in embed.vocab:
            C[idx,:] = embed.W[embed.vocab[term], :]


    tokens = text.split(' ')
    scores = [0.] * len(tokens)
    found=[]

    for idx, term in enumerate(tokens):
        if term in embed.vocab:
            vec = embed.W[embed.vocab[term], :]
            cosines = np.dot(C,vec.T)
            score = np.mean(cosines)
            scores[idx] = score
            if (score > thresh):
                found.append(term)
    print(scores)

    return found

vocab_file ="/path/to/vocab_file"
vectors_file ="/path/to/vectors_file"

embed = Embedding(vocab_file,vectors_file)

cuisine_refs = ["mexican","chinese","french","british","american"]
threshold = 0.2

text = "I want to find an indian restaurant"

cuisines = find_similar_words(embed,cuisine_refs,text,threshold)
print(cuisines)