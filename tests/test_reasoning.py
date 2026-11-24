from dataclasses import replace
import numpy as np
from researchmind.documents.intelligence import Evidence
from researchmind.reasoning.evidence import chunk_evidence,validate_chunk,EvidenceIndex
from researchmind.reasoning.assistant import answer,verify
from researchmind.services.reasoning import Reasoning
from researchmind.analytics.trends import research_analytics
from researchmind.db.engine import initialize
from researchmind.services.library import Library
from researchmind.schemas import PaperCreate

def fixture(): return [Evidence(1,'Accuracy was 80%. The sample was small.','Results','local PDF',1,1,2),Evidence(2,'A different classifier was tested.','Methodology','local PDF',2,2,3),Evidence(1,'Accuracy reference','References','local PDF',1,3,4)]
def test_chunks():
    items=fixture(); chunks=chunk_evidence(items,3,1); assert len(chunks)>2 and all(validate_chunk(c,items) for c in chunks); assert all(c.evidence.section!='References' for c in chunks)
def test_retrieval():
    items=fixture(); idx=EvidenceIndex(chunk_evidence(items)); hits=idx.search('accuracy'); assert hits[0][0].evidence.paper_id==1; assert not idx.search('zebra')
def test_hybrid():
    def enc(texts,model,role): return np.array([[1.,0.] if 'accuracy' in x.lower() else [0.,1.] for x in texts])
    idx=EvidenceIndex(chunk_evidence(fixture()),enc); assert idx.search('accuracy','Hybrid')[0][0].evidence.paper_id==1

def test_citations():
    items=fixture(); hits=EvidenceIndex(chunk_evidence(items)).search('accuracy'); c=hits[0][0]; assert not validate_chunk(replace(c,evidence=replace(c.evidence,page=99)),items)
    assert answer('accuracy',hits,items,lambda q,h:[{'text':'test','citations':[999]}])['mode']=='extractive'
    assert answer('accuracy',hits,items,lambda q,h:[{'text':'test','citations':[c.id]}])['mode']=='generated'
    assert answer('accuracy',[],items)['mode']=='insufficient'
def test_claims():
    items=fixture(); hits=[(c,1) for c in chunk_evidence(items)]; assert verify('unrelated',hits,items)['status']=='Insufficient evidence'
    assert verify(hits[0][0].evidence.text,hits,items)['status']=='Supported'
    assert verify('claim',hits,items,lambda p,c:('contradiction',.9))['status']=='Contradicted'
    assert verify('claim',hits,items,lambda p,c:('entailment' if 'Accuracy' in p else 'contradiction',.9))['status']=='Mixed evidence'
    assert verify('claim',hits,items,lambda p,c:('entailment',.6))['status']=='Insufficient evidence'
def test_database(tmp_path):
    s=initialize(tmp_path/'test.db'); lib=Library(s); p=lib.add_paper(PaperCreate(title='Synthetic test',year=2020,abstract='Future work should investigate larger samples.'))
    originals,idx=Reasoning(s).corpus([p]); assert idx.search('samples'); data=research_analytics(s,[p]); assert data['years']=={2020:1} and data['leads'][0]['paper_id']==p
    lib.delete_paper(p); assert research_analytics(s,[p])['papers']==0

def test_evaluation():
    from researchmind.reasoning.evaluation import citation_metrics,claim_metrics,passage_metrics
    assert citation_metrics([{'citations':[1,2]}],{1},[False])['citation_id_validity']==.5
    assert citation_metrics([{'citations':[1]}],{1},[True])['human_faithfulness']==1
    assert claim_metrics(['Supported'],['Supported'])['Supported']['f1-score']==1
    hits=EvidenceIndex(chunk_evidence(fixture())).search('accuracy'); assert passage_metrics(hits,{hits[0][0].id})['recall']==1

def test_stopword_only():
    idx=EvidenceIndex(chunk_evidence(fixture())); assert not idx.search('the was')
