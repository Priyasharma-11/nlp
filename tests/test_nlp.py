import numpy as np
import pytest
from researchmind.nlp.pipeline import tokens, inspect, representations, topics, classify
from researchmind.retrieval.search import Index, Record
from researchmind.retrieval.evaluation import metrics,evaluate
from researchmind.services.retrieval import corpus
from researchmind.services.library import Library
from researchmind.db.engine import initialize
from researchmind.schemas import PaperCreate

# Synthetic fixtures exercise algorithms; they are not scientific publications or benchmarks.
RECORDS=[Record(1,'Transformer attention','language model attention'),Record(2,'Plant growth','soil nitrogen'),Record(3,'Attention mechanisms','neural language')]
def test_tokens(): assert 'IL-6' in tokens('IL-6 and C++') and 'C++' in tokens('IL-6 and C++')
def test_preprocessing():
    result=inspect('Models do not predict.'); assert 'not' in result['filtered']; assert result['stems']; assert result['ngrams'][2]
def test_representation():
    _,bow,features,tf,_=representations([r.text for r in RECORDS]); assert bow.shape==tf.shape and 'attention' in features
@pytest.mark.parametrize('method',['NMF','LDA'])
def test_topics(method):
    words,weights=topics([r.text for r in RECORDS],2,method); assert len(words)==2 and weights.shape==(3,2)
@pytest.mark.parametrize('method',['Keyword','TF-IDF','BM25'])
def test_lexical(method):
    index=Index(RECORDS); assert index.search('nitrogen',method)[0][0].id==2; assert not index.search('zzzz',method); assert all(r.id!=1 for r,s in index.related(1,method=method))
def test_empty(): assert Index([]).search('test')==[]
def test_dense_contract():
    # Controlled encoder, not a pretrained-model quality test.
    def fixture(texts,model,role): return np.array([[0,1] if 'soil' in t or 'nitrogen' in t else [1,0] for t in texts])
    index=Index(RECORDS,fixture); assert index.search('nitrogen','Semantic')[0][0].id==2; assert index.search('nitrogen','Hybrid')[0][0].id==2

def test_metrics():
    m=metrics([2,1],{1},2); assert m['recall']==1 and m['precision']==.5 and m['mrr']==.5
    assert evaluate(Index(RECORDS),[{'query':'nitrogen','relevant_ids':[2]}],['BM25'],1,'General MiniLM')[0]['ndcg']==1
    with pytest.raises(ValueError): metrics([],set())
def test_classifier():
    texts=[f'neural network attention {i}' for i in range(8)]+[f'plant soil agriculture {i}' for i in range(8)]; _,result=classify(texts,['AI']*8+['plants']*8); assert result['test_size']==4 and len(result['confusion'])==2
    with pytest.raises(ValueError): classify(['x'],['a'])
def test_corpus(tmp_path):
    lib=Library(initialize(tmp_path/'db.sqlite')); pid=lib.add_paper(PaperCreate(title='Synthetic test record',abstract='Unique token')); assert corpus(lib)[0].id==pid; assert Index(corpus(lib)).search('unique')[0][0].id==pid; lib.delete_paper(pid); assert corpus(lib)==[]

def test_scientific_lexicon():
    from researchmind.nlp.pipeline import scientific_entities
    text='BERT and BioBERT use MNIST.'; result=scientific_entities(text,{'METHOD':['BERT'],'DATASET':['MNIST']}); assert len(result)==2 and all(text[r['start']:r['end']]==r['text'] for r in result)

def test_word_vectors():
    pytest.importorskip('gensim')
    from researchmind.nlp.pipeline import word_vectors
    assert word_vectors(['attention neural model','attention transformer model'],'attention')
def test_scientific_ner_validation():
    from researchmind.nlp.pipeline import scientific_ner
    with pytest.raises(ValueError,match='Enter scientific text'):
        scientific_ner('', ['gene'], 'missing-model')
    with pytest.raises(ValueError,match='entity label'):
        scientific_ner('BRCA1 is a gene.', [], 'missing-model')
    with pytest.raises(ValueError,match='Threshold'):
        scientific_ner('BRCA1 is a gene.', ['gene'], 'missing-model', 1.0)

def test_scientific_ner_local_model(monkeypatch):
    from researchmind.nlp import pipeline
    class FakeModel:
        def predict_entities(self,text,labels,threshold):
            assert labels == ['gene','protein']
            assert threshold == 0.4
            return [{'text':'BRCA1','label':'gene','start':0,'end':5,'score':0.91}]
    monkeypatch.setattr(pipeline,'load_scientific_ner',lambda path: FakeModel())
    found=pipeline.scientific_ner('BRCA1 is a gene.',['gene','protein'],'/local/model',0.4)
    assert found[0]['text']=='BRCA1' and found[0]['score']==pytest.approx(0.91)
    assert found[0]['method']=='GLiNER zero-shot'
