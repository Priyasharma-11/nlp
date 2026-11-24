import pytest,pymupdf,json
from researchmind.db.engine import initialize
from researchmind.services.library import Library
from researchmind.services.science import Science
from researchmind.services.intelligence import Intelligence
from researchmind.documents.intelligence import analyze,summarize,Evidence
from researchmind.graph.network import build_graph,citation_rows,graph_figure
from researchmind.providers.literature import LiteratureClient
from researchmind.schemas import PaperCreate

@pytest.fixture
def corpus(tmp_path):
    s=initialize(tmp_path/'test.sqlite'); lib=Library(s); sc=Science(s)
    a=sc.save_record(LiteratureClient.openalex({'id':'https://openalex.org/W1','title':'Synthetic A','referenced_works':['https://openalex.org/W2','https://openalex.org/W3'],'cited_by_count':10,'authorships':[{'author':{'id':'A1','display_name':'Fixture author'},'institutions':[{'id':'I1','display_name':'Fixture institution'}]}],'topics':[{'display_name':'Fixture topic'}]},'2026-01-01'))
    b=sc.save_record(LiteratureClient.openalex({'id':'https://openalex.org/W2','title':'Synthetic B'},'2026-01-01'))
    with pymupdf.open() as pdf:
        p=pdf.new_page(); p.insert_text((60,60),'Abstract\nWe propose a new classifier.'); p.insert_text((60,130),'Methods\nWe trained a classifier on the XYZ dataset.'); p.insert_text((60,200),'Results\nAccuracy was 80%.'); p.insert_text((60,270),'Limitations\nThe sample was small.'); p.insert_text((60,340),'References\nXYZ dataset was mentioned here.'); data=pdf.tobytes()
    doc=sc.upload(a,'fixture.pdf',data)
    return s,lib,sc,a,b,doc

def test_analysis(corpus):
    s,_,sc,a,_,doc=corpus; ev=Intelligence(s).evidence(a); result=analyze(ev)
    assert result['Datasets'][0].text=='We trained a classifier on the XYZ dataset.'
    assert result['Results'][0].page==1 and result['Results'][0].document_id==doc
    assert result['Limitations'][0].text=='The sample was small.' and not result['Future work']
    for items in result.values():
        for e in items: assert e.text in next(p.text for p in sc.passages(doc) if p.id==e.passage_id)

def test_summary(corpus):
    s,_,_,a,_,_=corpus; ev=Intelligence(s).evidence(a)
    assert len(summarize(ev,'Abstract'))==1
    assert all(e.section=='Results' for e in summarize(ev,'Section','Results'))
    assert all(e.section!='References' for e in summarize(ev))
    assert not summarize([],limit=3)

def test_comparison(corpus):
    s,_,_,a,b,_=corpus; result=Intelligence(s).compare([a,b]); assert len(result)==2 and not result[1]['fields']['Results']
    with pytest.raises(ValueError): Intelligence(s).compare([a,a])

def test_graph(corpus):
    s,_,_,a,b,_=corpus; g=build_graph(s,lexicon={'Dataset':['XYZ']}); assert g.has_edge(f'paper:{a}',f'paper:{b}','cites')
    assert 'external:openalex:W3' in g
    assert g.has_edge(f'paper:{a}','entity:Dataset:xyz','mentions')
    assert len(g[f'paper:{a}']['entity:Dataset:xyz']['mentions']['evidence'])==1
    assert all(d['evidence'] for _,_,d in g.edges(data=True)); assert citation_rows(g)[0]['incoming in graph']==1
    assert len(graph_figure(g).data)>0

def test_graph_delete(corpus):
    s,lib,_,a,b,_=corpus; lib.delete_paper(a); g=build_graph(s); assert f'paper:{a}' not in g and g.number_of_edges()==0

def test_abstract_provenance(corpus):
    s,lib,sc,*_=corpus; p=lib.add_paper(PaperCreate(title='Manual fixture',abstract='We propose a model.')); ev=Intelligence(s).evidence(p); assert ev[0].page is None and 'unverified' in ev[0].reference()
    q=sc.save_record(LiteratureClient.crossref({'DOI':'10.1234/test','title':['Source fixture'],'abstract':'We propose a model.'},'2026-01-01')); ev=Intelligence(s).evidence(q); assert ev[0].source_id and ev[0].page is None

def test_version_validation(corpus):
    s,_,_,a,b,doc=corpus
    with pytest.raises(ValueError): Intelligence(s).evidence(b,doc)
