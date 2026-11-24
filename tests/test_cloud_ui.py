import pytest
pytest.importorskip('streamlit')
from streamlit.testing.v1 import AppTest


def test_cloud_consent_and_navigation():
    app=AppTest.from_file('cloud_app.py').run()
    assert not app.exception
    assert '_rm_cloud_workspace' not in app.session_state
    app.checkbox(key='cloud_consent').check().run()
    assert not app.exception
    from researchmind.ui.workspace import PAGES
    for page in PAGES:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert '_rm_cloud_workspace' not in app.session_state
