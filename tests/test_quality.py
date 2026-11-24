import pytest
from researchmind.reasoning.benchmark import run_scifact
from researchmind.reasoning.evidence import EvidenceIndex,chunk_evidence
from researchmind.documents.intelligence import Evidence
from researchmind.retrieval.search import Index,Record
from researchmind.reasoning.evaluation import citation_metrics
from researchmind.db.engine import initialize
from researchmind.services.library import Library
from researchmind.services.science import Science
from researchmind.schemas import PaperCreate
from researchmind.services.reasoning import Reasoning
import pymupdf

def test_benchmark_synthetic_format():
    docs=[{'doc_id':1,'abstract':['Synthetic apples grow.']},{'doc_id':2,'abstract':['Synthetic oranges grow.']}]
    claims=[{'id':1,'claim':'Synthetic apples grow.','evidence':{'1':[{'label':'SUPPORT','sentences':[0]}]}},{'id':2,'claim':'Zebras fly.','evidence':{}}]
    result=run_scifact(docs,claims,k=1)
    assert result['claims']==2 and result['retrieval_document_metrics']['recall']==1
    assert result['claim_metrics']['accuracy']==1 and result['human_faithfulness'] is None

def test_benchmark_unlabeled_rejected():
    with pytest.raises(ValueError): run_scifact([{'doc_id':1,'abstract':['Example']}],[{'claim':'Example'}])

def test_zero_weight_no_model():
    def unavailable(*args): raise AssertionError('No model should be loaded')
    index=Index([Record(1,'apples')],unavailable)
    assert index.search('apples','Hybrid',weight=0)[0][0].id==1

def test_stopword_hybrid_no_model():
    def unavailable(*args): raise AssertionError('No model should be loaded')
    index=EvidenceIndex(chunk_evidence([Evidence(1,'Research text','Abstract','manual')]),unavailable)
    assert index.search('the was','Hybrid')==[]

def test_ingestion_to_reasoning(tmp_path):
    sessions=initialize(tmp_path/'test.db'); lib=Library(sessions)
    pid=lib.add_paper(PaperCreate(title='Synthetic fixture'))
    with pymupdf.open() as pdf:
        page=pdf.new_page(); page.insert_text((72,72),'Results\nSynthetic accuracy was 81 percent.'); data=pdf.tobytes()
    Science(sessions).upload(pid,'fixture.pdf',data)
    originals,idx=Reasoning(sessions).corpus([pid]); hits=idx.search('accuracy'); assert hits[0][0].evidence.page==1
    from researchmind.reasoning.assistant import answer
    result=answer('accuracy',hits,originals); assert result['mode']=='extractive'
    assert citation_metrics(result['items'],{c.id for c,_ in hits})['citation_id_validity']==1
    lib.delete_paper(pid)
    with pytest.raises(ValueError): Reasoning(sessions).corpus([pid])

def test_invalid_upload_before_hash(tmp_path):
    sessions=initialize(tmp_path/'test.db')
    with pytest.raises(ValueError): Science(sessions).upload(1,'bad.pdf',b'not a pdf')
