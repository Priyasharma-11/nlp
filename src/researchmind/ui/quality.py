import json
import streamlit as st
from researchmind.reasoning.evaluation import citation_metrics,claim_metrics
from researchmind.reasoning.benchmark import run_scifact

def quality_panel(cloud=False):
    st.subheader('Evidence & reasoning evaluation')
    st.caption('Provide independent human judgments or labeled benchmark data. No default scores.')
    with st.expander('Citation and human faithfulness evaluation'):
        raw=st.text_area('Answer items with citations (JSON)',value='[]'); ids=st.text_input('Retrieved evidence IDs (comma separated)'); support=st.text_area('Human support judgments (JSON boolean list, optional)')
        if st.button('Evaluate citations'):
            try:
                items=json.loads(raw); allowed={int(i.strip()) for i in ids.split(',') if i.strip()}; judgments=json.loads(support) if support.strip() else None
                st.json(citation_metrics(items,allowed,judgments))
            except (ValueError,TypeError,AttributeError,KeyError): st.error('Check JSON items, evidence IDs and human judgments.')
    with st.expander('Claim classification evaluation'):
        expected=st.text_area('Expected labels (JSON list)',value='[]'); predicted=st.text_area('Predicted labels (JSON list)',value='[]')
        if st.button('Evaluate claim labels'):
            try: st.json(claim_metrics(json.loads(expected),json.loads(predicted)))
            except (ValueError,TypeError): st.error('Provide paired valid claim labels.')
    if cloud:
        st.info('Full dataset benchmarks are available in the local edition and CLI to avoid exhausting shared cloud resources.'); return
    with st.expander('Offline SciFact benchmark'):
        st.caption('Upload labeled development data from SciFact. Processing is local; baseline claim assessment uses exact statement matching.')
        corpus=st.file_uploader('SciFact corpus.jsonl',type=['jsonl']); claims=st.file_uploader('SciFact claims_dev.jsonl',type=['jsonl']); method=st.selectbox('Benchmark retrieval',['BM25','TF-IDF','Semantic','Hybrid']); k=st.number_input('Passage cutoff',1,50,5)
        if st.button('Run SciFact evaluation'):
            if not corpus or not claims: st.warning('Upload both labeled benchmark files.'); return
            try:
                with st.spinner('Evaluating supplied dataset locally…'):
                    result=run_scifact(*[[json.loads(line) for line in f.getvalue().decode('utf-8').splitlines() if line.strip()] for f in (corpus,claims)],method,int(k))
                st.json({key:value for key,value in result.items() if key!='details'}); st.download_button('Export benchmark report',json.dumps(result,indent=2),'scifact-results.json','application/json')
            except (ValueError,TypeError,KeyError,RuntimeError) as exc: st.error(f'Benchmark could not run: {type(exc).__name__}. Check data format and installed models.')
