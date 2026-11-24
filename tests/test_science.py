import json, sqlite3
import httpx, pytest, pymupdf
from researchmind.db.engine import initialize
from researchmind.services.library import Library
from researchmind.services.science import Science
from researchmind.schemas import PaperCreate
from researchmind.providers.literature import LiteratureClient
from researchmind.documents.parser import parse_pdf

@pytest.fixture
def services(tmp_path):
    sessions=initialize(tmp_path/'db.sqlite'); return Library(sessions),Science(sessions)

# Synthetic transport fixtures, never displayed as real papers in the app.
def fixture(): return {'DOI':'10.1234/fixture','title':['Synthetic test fixture'],'published':{'date-parts':[[2020]]},'abstract':'<p>Test abstract</p>','author':[{'given':'Test','family':'Author'}]}
def test_crossref_cache():
    calls=[]
    def handler(req):
        calls.append(req); return httpx.Response(200,json={'message':{'items':[fixture()]}})
    client=LiteratureClient(httpx.Client(transport=httpx.MockTransport(handler)),sleep=lambda _:None)
    r=client.search('Crossref','example',2)[0]; assert r.abstract=='Test abstract' and r.year==2020 and r.authors==['Test Author']
    assert calls[0].url.params['offset']=='10'; client.search('Crossref','example',2); assert len(calls)==1

def test_openalex():
    c=LiteratureClient(httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'results':[{'id':'https://openalex.org/W1','title':'Fixture','abstract_inverted_index':{'world':[1],'hello':[0]},'open_access':{'is_oa':True}}]}))),sleep=lambda _:None)
    r=c.search('OpenAlex','example')[0]; assert r.abstract=='hello world' and r.open_access is True

def test_arxiv():
    xml='<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>https://arxiv.org/abs/1234.5678v2</id><title>Fixture</title><published>2020-01-01</published><summary>Test</summary><author><name>Test Author</name></author></entry></feed>'
    c=LiteratureClient(httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(200,text=xml))),sleep=lambda _:None)
    r=c.search('arXiv','example')[0]; assert r.external_id.endswith('5678') and r.year==2020

def test_retry():
    calls=[]
    def handler(r):
        calls.append(r); return httpx.Response(429 if len(calls)==1 else 200,json={'message':{'items':[]}})
    c=LiteratureClient(httpx.Client(transport=httpx.MockTransport(handler)),sleep=lambda _:None); assert c.search('Crossref','x')==[] and len(calls)==2

def test_error():
    c=LiteratureClient(httpx.Client(transport=httpx.MockTransport(lambda r:httpx.Response(403))),sleep=lambda _:None)
    with pytest.raises(ValueError,match='403'): c.search('Crossref','x')

def test_sources(services):
    lib,sc=services; r=LiteratureClient.crossref(fixture(),'2026-01-01'); p=sc.save_record(r); assert sc.save_record(r)==p
    assert len(lib.papers())==1 and json.loads(sc.sources(p)[0].raw)['DOI']==r.doi
    other=LiteratureClient.openalex({'id':'W1','title':'Fixture','doi':r.doi},'2026-01-01'); assert sc.save_record(other)==p and len(sc.sources(p))==2

def pdf():
    with pymupdf.open() as d:
        p=d.new_page(); p.insert_text((72,72),'Abstract\nSynthetic extraction test.'); p.insert_text((72,150),'1 Methods\nTest method.'); d.new_page(); return d.tobytes()

def test_pdf(services):
    lib,sc=services; p=lib.add_paper(PaperCreate(title='Synthetic fixture')); data=pdf(); doc=sc.upload(p,'../test.pdf',data)
    assert sc.upload(p,'same.pdf',data)==doc; blocks=sc.passages(doc); assert {b.section for b in blocks}=={'Abstract','Methodology'} and all(b.page==1 for b in blocks)
    stored=sc.documents(p)[0]; assert stored.original==data and stored.filename=='test.pdf' and json.loads(stored.metadata_json)['empty_pages']==[2]
    lib.delete_paper(p); assert sc.passages(doc)==[] and sc.documents(p)==[]

def test_bad_pdf():
    with pytest.raises(ValueError): parse_pdf(b'not a pdf')

def test_migration(tmp_path):
    from sqlalchemy import create_engine
    from researchmind.db.models import Paper, Collection, Membership, Activity
    path=tmp_path/'legacy.sqlite'; engine=create_engine(f'sqlite:///{path}')
    with engine.begin() as c:
        for model in [Paper,Collection,Membership,Activity]: model.__table__.create(c)
        c.exec_driver_sql("INSERT INTO papers (title,abstract,access_level,created_at) VALUES ('Legacy','','manual_metadata','2020-01-01')")
    engine.dispose(); lib=Library(initialize(path)); assert lib.papers()[0].title=='Legacy'
    with sqlite3.connect(path) as c: assert c.execute('PRAGMA user_version').fetchone()[0]==2
    assert Library(initialize(path)).papers()[0].title=='Legacy'
