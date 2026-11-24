import pytest
pytest.importorskip('streamlit')
from streamlit.testing.v1 import AppTest

def test_navigation(tmp_path,monkeypatch):
    monkeypatch.setenv('RESEARCHMIND_DATA_DIR',str(tmp_path))
    app=AppTest.from_file('app.py').run()
    assert not app.exception
    app.sidebar.radio[0].set_value('Overview').run()
    assert not app.exception
    assert app.metric[0].value=='0'
    app.sidebar.radio[0].set_value('Library').run()
    assert not app.exception
    app.sidebar.radio[0].set_value('Claim verification').run()
    assert not app.exception
    assert app.title[0].value=='Claim verification'

def test_science_navigation(tmp_path,monkeypatch):
    monkeypatch.setenv('RESEARCHMIND_DATA_DIR',str(tmp_path))
    app=AppTest.from_file('app.py').run()
    for page in ['Discover papers','Paper analyzer']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception
        assert app.title[0].value==page


def test_nlp_navigation(tmp_path,monkeypatch):
    monkeypatch.setenv('RESEARCHMIND_DATA_DIR',str(tmp_path))
    app=AppTest.from_file('app.py').run()
    for page in ['NLP laboratory','Semantic search','Evaluation']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception
        assert app.title[0].value==page

def test_intelligence_navigation(tmp_path,monkeypatch):
    monkeypatch.setenv('RESEARCHMIND_DATA_DIR',str(tmp_path))
    app=AppTest.from_file('app.py').run()
    for page in ['Compare papers','Knowledge graph']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception
        assert app.title[0].value==page


def test_reasoning_navigation(tmp_path,monkeypatch):
    monkeypatch.setenv("RESEARCHMIND_DATA_DIR",str(tmp_path))
    app=AppTest.from_file("app.py").run()
    for page in ["Research assistant","Claim verification","Research analytics"]:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception
        assert app.title[0].value==page

def test_all_navigation(tmp_path,monkeypatch):
    monkeypatch.setenv('RESEARCHMIND_DATA_DIR',str(tmp_path))
    from researchmind.ui.workspace import PAGES
    app=AppTest.from_file('app.py').run()
    for page in PAGES:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page
