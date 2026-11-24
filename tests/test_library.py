import pytest
from researchmind.db.engine import initialize
from researchmind.services.library import Library
from researchmind.schemas import CollectionCreate, PaperCreate

@pytest.fixture
def lib(tmp_path): return Library(initialize(tmp_path/'test.sqlite'))
def test_empty(lib): assert lib.overview()['papers']==0 and lib.overview()['collections']==0
def test_persistence(tmp_path):
    path=tmp_path/'db.sqlite'; Library(initialize(path)).add_paper(PaperCreate(title='Test fixture'))
    assert Library(initialize(path)).papers()[0].title=='Test fixture'
def test_doi_duplicate(lib):
    lib.add_paper(PaperCreate(title='Test A',doi='https://doi.org/10.1234/test'))
    with pytest.raises(ValueError): lib.add_paper(PaperCreate(title='Test B',doi='10.1234/TEST'))
    assert lib.overview()['papers']==1
@pytest.mark.parametrize('kwargs',[{'title':' '},{'title':'A','doi':'invalid'},{'title':'A','year':100}])
def test_validation(kwargs):
    with pytest.raises(ValueError): PaperCreate(**kwargs)
def test_membership_and_cascade(lib):
    p=lib.add_paper(PaperCreate(title='Fixture')); c=lib.add_collection(CollectionCreate(name='Test'))
    assert lib.assign(c,p); assert not lib.assign(c,p); assert len(lib.members(c))==1
    assert lib.delete_paper(p); assert lib.members(c)==[]; assert lib.overview()['memberships']==0
    assert not lib.delete_paper(p)
def test_missing_membership(lib):
    with pytest.raises(ValueError): lib.assign(99,99)
def test_literal_search(lib):
    lib.add_paper(PaperCreate(title='100% test')); lib.add_paper(PaperCreate(title='Another test'))
    assert len(lib.papers('%'))==1
    assert lib.papers("' OR 1=1 --")==[]
def test_collection_duplicate(lib):
    lib.add_collection(CollectionCreate(name='Fixture'))
    with pytest.raises(ValueError): lib.add_collection(CollectionCreate(name='Fixture'))
