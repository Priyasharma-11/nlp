import pytest
from researchmind.retrieval.beir import run_beir, load_beir

def test_beir_graded_fixture(tmp_path):
    (tmp_path/'qrels').mkdir()
    (tmp_path/'corpus.jsonl').write_text('{"_id":"a","title":"Synthetic","text":"apple apple fruit"}\n{"_id":"b","text":"orange fruit"}\n')
    (tmp_path/'queries.jsonl').write_text('{"_id":"q","text":"apple"}\n')
    (tmp_path/'qrels'/'test.tsv').write_text('query-id\tcorpus-id\tscore\nq\ta\t2\nq\tb\t0\n')
    result=run_beir(*load_beir(tmp_path),k=1)
    assert result['metrics']=={'precision':1.,'recall':1.,'mrr':1.,'ndcg':1.}

def test_beir_unknown_judgment():
    with pytest.raises(ValueError): run_beir([{'_id':'a','text':'apple'}],[{'_id':'q','text':'apple'}],{'q':{'missing':1}})

def test_beir_no_positive_judgment():
    with pytest.raises(ValueError): run_beir([{'_id':'a','text':'apple'}],[{'_id':'q','text':'apple'}],{'q':{'a':0}})
