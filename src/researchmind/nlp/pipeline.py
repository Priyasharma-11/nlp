"""Inspectable NLP stages; never silently substitute missing language models."""
import re
import unicodedata
from functools import lru_cache
from collections import Counter
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

TOKEN = re.compile(r"[^\W_]+(?:[.\-+/#][^\W_]+)*\+*", re.UNICODE)
def normalize(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', text)).strip()
def tokens(text): return TOKEN.findall(normalize(text))
def lexical_tokens(text): return [t.casefold() for t in tokens(text)]
@lru_cache(maxsize=2)
def language_model(name='en_core_web_sm'):
    import spacy
    return spacy.load(name)
def inspect(text):
    words=tokens(text); lower=[w.casefold() for w in words]
    stop=[w for w in lower if w not in ENGLISH_STOP_WORDS or w in {'no','not','nor','never'}]
    out={'normalized':normalize(text),'tokens':words,'lowercase':lower,'filtered':stop,
         'stems':[PorterStemmer().stem(w) for w in stop], 'warnings':[]}
    try:
        import nltk
        out['sentences']=nltk.sent_tokenize(text)
    except LookupError:
        out['sentences']=re.split(r'(?<=[.!?])\s+',normalize(text)); out['warnings'].append('Punkt unavailable; sentence boundaries use a simple heuristic.')
    try:
        doc=language_model()(text)
        out['pos']=[(t.text,t.pos_) for t in doc if not t.is_space]
        out['lemmas']=[(t.text,t.lemma_) for t in doc if not t.is_space]
        out['entities']=[(e.text,e.label_,e.start_char,e.end_char) for e in doc.ents]
    except (OSError,ImportError):
        out['warnings'].append('spaCy English model unavailable; POS and NER not run.')
        try: out['lemmas']=[(w,WordNetLemmatizer().lemmatize(w)) for w in stop]
        except LookupError: out['warnings'].append('WordNet unavailable; lemmatization not run.')
    out['ngrams']={n:Counter(tuple(lower[i:i+n]) for i in range(len(lower)-n+1)).most_common(30) for n in (1,2,3)}
    return out

def representations(texts):
    """Fit on the supplied corpus, not on an unrelated model."""
    if not any(tokens(t) for t in texts): raise ValueError('No indexable text.')
    opts=dict(tokenizer=lexical_tokens, token_pattern=None, lowercase=False, ngram_range=(1,3),max_features=20000)
    bow=CountVectorizer(**opts); tf=TfidfVectorizer(**opts)
    return (bow.get_params(), bow.fit_transform(texts), bow.get_feature_names_out(), tf.fit_transform(texts), tf.get_feature_names_out())

def topics(texts, n=3, method='NMF'):
    if len(texts)<2: raise ValueError('At least two documents required.')
    if method not in ('NMF','LDA'): raise ValueError('Unknown topic model.')
    vec=(TfidfVectorizer if method=='NMF' else CountVectorizer)(stop_words='english',max_features=10000)
    x=vec.fit_transform(texts); n=min(int(n),*x.shape)
    if n<1: raise ValueError('No topic features.')
    model=NMF(n_components=n,init='nndsvda',random_state=42,max_iter=400) if method=='NMF' else LatentDirichletAllocation(n_components=n,random_state=42)
    weights=model.fit_transform(x); names=vec.get_feature_names_out()
    return [[str(names[i]) for i in row.argsort()[-8:][::-1] if row[i]>0] for row in model.components_], weights

def classify(texts, labels):
    """User-labelled corpus; stratified held-out evaluation, no fabricated labels."""
    counts=Counter(labels)
    if len(texts)!=len(labels) or len(counts)<2 or min(counts.values())<4: raise ValueError('Provide at least four labelled papers per class, two classes minimum.')
    if len(set(texts))!=len(texts): raise ValueError('Remove identical texts before evaluation.')
    test_size=max(len(counts),round(len(texts)*.25))
    a,b,y,z=train_test_split(texts,labels,test_size=test_size,random_state=42,stratify=labels)
    model=make_pipeline(TfidfVectorizer(ngram_range=(1,2)),LogisticRegression(max_iter=1000,random_state=42))
    model.fit(a,y); pred=model.predict(b); order=sorted(counts)
    return model, {'report':classification_report(z,pred,labels=order,output_dict=True,zero_division=0), 'confusion':confusion_matrix(z,pred,labels=order).tolist(),'labels':order,'train_size':len(a),'test_size':len(b)}

def scientific_entities(text, lexicon):
    """Exact, boundary-aware user-supplied scientific terminology; not trained NER."""
    if not isinstance(lexicon,dict): raise ValueError('Lexicon must map entity types to term lists.')
    results=[]
    for label,terms in lexicon.items():
        if not isinstance(terms,list) or not all(isinstance(t,str) for t in terms): raise ValueError('Each entity type requires a list of strings.')
        for term in set(terms):
            if term.strip():
                for match in re.finditer(r'(?<!\w)'+re.escape(term)+r'(?!\w)',text,re.I):
                    results.append({'text':match.group(),'type':label,'start':match.start(),'end':match.end(),'method':'user lexicon'})
    return sorted(results,key=lambda r:(r['start'],r['end'],r['type']))

def word_vectors(texts, word):
    """Exploratory locally trained Word2Vec, not a pretrained scientific model."""
    try: from gensim.models import Word2Vec
    except ImportError as exc: raise ValueError('Install the optional word2vec dependency first.') from exc
    sentences=[lexical_tokens(t) for t in texts]; sentences=[s for s in sentences if s]
    if not sentences: raise ValueError('No indexable text.')
    model=Word2Vec(sentences=sentences,vector_size=50,min_count=1,workers=1,seed=42,epochs=20)
    if word.casefold() not in model.wv: raise ValueError('Word not present in corpus vocabulary.')
    return model.wv.most_similar(word.casefold(),topn=min(10,len(model.wv)-1)) if len(model.wv)>1 else []
