import pytest
from researchmind.cloud import workspace, reset_workspace, MAX_UPLOAD, LIMITS
from researchmind.db.models import Paper
from researchmind.schemas import PaperCreate, CollectionCreate
from researchmind.services.science import Science


def test_session_isolation_and_reset(monkeypatch,tmp_path):
    monkeypatch.setenv('RESEARCHMIND_DATA_DIR',str(tmp_path))
    a,b={},{}
    try:
        first=workspace(a); second=workspace(b)
        p=first.add_paper(PaperCreate(title='Synthetic private session A'))
        first.add_collection(CollectionCreate(name='A collection'))
        assert workspace(a) is first
        assert second.papers()==[] and second.collections()==[]
        second.add_paper(PaperCreate(title='Synthetic session B'))
        assert first.papers()[0].title=='Synthetic private session A'
        a['discovery_results']=['synthetic']; a['cloud_consent']=True
        reset_workspace(a)
        assert not a and workspace(a).papers()==[]
        assert len(second.papers())==1
        assert not list(tmp_path.iterdir())
    finally:
        reset_workspace(a); reset_workspace(b)


def test_paper_quota_rollback():
    state={}; lib=workspace(state)
    try:
        for i in range(LIMITS[Paper]): lib.add_paper(PaperCreate(title=f'Synthetic {i}'))
        with pytest.raises(ValueError,match='limit reached'): lib.add_paper(PaperCreate(title='Overflow'))
        assert len(lib.papers())==LIMITS[Paper]
        lib.delete_paper(lib.papers()[0].id)
        lib.add_paper(PaperCreate(title='Replacement'))
        assert len(lib.papers())==LIMITS[Paper]
    finally: reset_workspace(state)


def test_upload_quota_before_parsing(monkeypatch):
    state={}; lib=workspace(state)
    try:
        p=lib.add_paper(PaperCreate(title='Synthetic paper'))
        def fail(*args): pytest.fail('Parser must not run for oversized upload')
        monkeypatch.setattr('researchmind.services.science.parse_pdf',fail)
        with pytest.raises(ValueError,match='5 MiB'):
            Science(lib.sessions).upload(p,'oversized.pdf',b'%PDF-'+b'x'*MAX_UPLOAD)
    finally: reset_workspace(state)


def test_cloud_pdf_and_cross_session_access():
    import fitz
    a,b={},{}
    try:
        x,y=workspace(a),workspace(b)
        p=x.add_paper(PaperCreate(title='Synthetic PDF'))
        with fitz.open() as doc:
            page=doc.new_page(); page.insert_text((72,72),'Synthetic test passage.'); data=doc.tobytes()
        service=Science(x.sessions); d=service.upload(p,'fixture.pdf',data)
        assert service.passages(d)
        assert Science(y.sessions).documents(p)==[]
        assert Science(y.sessions).passages(d)==[]
        reset_workspace(a)
        assert Science(workspace(a).sessions).documents(p)==[]
    finally: reset_workspace(a); reset_workspace(b)
