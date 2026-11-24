from dataclasses import dataclass
from collections import Counter
import math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from researchmind.nlp.pipeline import lexical_tokens
from .embeddings import encode

@dataclass(frozen=True)
class Record:
    id:int
    title:str
    abstract:str=''
    year:int|None=None
    authors:str=''
    topics:str=''
    @property
    def text(self): return '\n'.join((self.title,self.abstract,self.authors,self.topics))
    @property
    def scientific_text(self): return self.title+' [SEP] '+self.abstract

class Index:
    def __init__(self, records, encoder=encode):
        self.records=list(records); self.encoder=encoder; self.words=[Counter(lexical_tokens(r.text)) for r in self.records]
        self.lengths=np.array([sum(c.values()) for c in self.words]); self.df=Counter(w for c in self.words for w in c)
        self.vectorizer=TfidfVectorizer(tokenizer=lexical_tokens,token_pattern=None,lowercase=False)
        self.matrix=self.vectorizer.fit_transform([r.text for r in self.records]) if self.df else None
        self.dense={}
    def scores(self,query,method,model,role='query'):
        q=set(lexical_tokens(query)); n=len(self.records)
        if method=='Keyword': return np.array([sum(c[w] for w in q) for c in self.words],float)
        if method=='TF-IDF': return (self.matrix @ self.vectorizer.transform([query]).T).toarray().ravel()
        if method=='BM25':
            avg=max(1,float(self.lengths.mean())); result=np.zeros(n)
            for w in q:
                idf=math.log(1+(n-self.df[w]+.5)/(self.df[w]+.5)); f=np.array([c[w] for c in self.words]); result+=idf*f*2.5/(f+1.5*(.25+.75*self.lengths/avg))
            return result
        if method=='Semantic':
            if model not in self.dense: self.dense[model]=self.encoder([r.scientific_text for r in self.records],model,'paper')
            a=np.asarray(self.dense[model]); b=np.asarray(self.encoder([query],model,role))[0]
            return (a@b)/np.maximum(1e-12,np.linalg.norm(a,axis=1)*np.linalg.norm(b))
        raise ValueError('Unknown retrieval method.')
    def search(self,query,method='BM25',model='General MiniLM',k=10,weight=.5,exclude=None,role='query'):
        if not query.strip() or self.matrix is None: return []
        if not 0<=weight<=1 or k<1: raise ValueError('Invalid ranking settings.')
        if method=='Hybrid':
            lex=self.scores(query,'BM25',model) if weight<1 else np.zeros(len(self.records)); sem=self.scores(query,'Semantic',model,role) if weight>0 else np.zeros(len(self.records))
            score=np.zeros(len(lex))
            for values,w in [(lex,1-weight),(sem,weight)]:
                for rank,i in enumerate(np.argsort(-values,kind='stable'),1):
                    if values[i]>0: score[i]+=w/(60+rank)
        else: score=self.scores(query,method,model,role)
        return [(self.records[i],float(score[i])) for i in np.argsort(-score,kind='stable') if score[i]>0 and self.records[i].id!=exclude][:k]
    def related(self,paper_id,**kwargs):
        r=next((r for r in self.records if r.id==paper_id),None)
        if r is None: raise ValueError('Paper not found.')
        return self.search(r.scientific_text,exclude=paper_id,role='paper',**kwargs)
