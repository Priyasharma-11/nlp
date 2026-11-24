"""Run with the cloud requirements installed."""
import pytest
from researchmind.nlp.pipeline import inspect

def test_english_model():
    pytest.importorskip("en_core_web_sm")
    out=inspect("Google is developing new tools in California. Researchers are testing them.")
    assert out["warnings"] == []
    assert len(out["sentences"]) == 2
    assert any(word == "developing" and lemma == "develop" for word, lemma in out["lemmas"])
    assert any(word == "developing" and pos == "VERB" for word, pos in out["pos"])
    assert any(entity == "Google" for entity, *_ in out["entities"])
