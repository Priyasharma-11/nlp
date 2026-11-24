import streamlit as st
import pandas as pd
from functools import partial
from researchmind.services.reasoning import Reasoning
from researchmind.reasoning.assistant import answer,verify,generate_local,local_stance
from researchmind.analytics.trends import research_analytics

def choose(lib):
    papers={p.id:p.title for p in lib.papers()}
    return st.multiselect('Research collection',list(papers),default=list(papers)[:10],format_func=papers.get),papers

def reasoning_page(lib,claim_mode=False):
    st.title('Claim verification' if claim_mode else 'Research assistant')
    st.caption('Evidence workspace · latest uploaded version per paper · no external AI APIs')
    ids,papers=choose(lib)
    question=st.text_area('Scientific claim' if claim_mode else 'Scientific question',max_chars=2000)
    method=st.selectbox('Evidence retrieval',['BM25','TF-IDF'] if getattr(lib,'cloud',False) else ['BM25','TF-IDF','Semantic','Hybrid'])
    k=st.slider('Maximum evidence passages',1,20,5)
    path='' if getattr(lib,'cloud',False) else st.text_input('Optional local NLI model directory' if claim_mode else 'Optional local causal language model directory')
    if not st.button('Assess evidence' if claim_mode else 'Retrieve and answer',type='primary'): return
    if not ids or not question.strip(): st.warning('Select papers and enter a question or claim.'); return
    try:
        with st.spinner('Retrieving scientific evidence locally…'):
            originals,index=Reasoning(lib.sessions).corpus(ids); hits=index.search(question,method,k)
            if claim_mode:
                classifier=(lambda p,c:local_stance(p,c,path)) if path else None
                result=verify(question,hits,originals,classifier)
                st.subheader(result['status']); st.caption(result['method']); st.dataframe(pd.DataFrame(result['rows']))
            else:
                generator=partial(generate_local,path=path) if path else None
                result=answer(question,hits,originals,generator)
                st.subheader(result['mode'].capitalize());
                for row in result['items']: st.text(row['text']); st.caption('Evidence IDs: '+', '.join(map(str,row['citations'])))
            st.warning(result['warning'])
            for c,score in hits:
                with st.expander(f'Evidence {c.id} · {papers[c.evidence.paper_id]} · {c.evidence.section}'):
                    st.text(c.evidence.text); st.caption(c.evidence.reference()); st.caption(f'Retrieval score: {score:.4f} (not confidence)')
    except (ValueError,ImportError,OSError,RuntimeError) as exc: st.error(str(exc))

def analytics_page(lib):
    st.title('Research analytics'); st.caption('Coverage of your selected collection, not the entire scientific literature.')
    ids,_=choose(lib)
    methods=st.text_input('Method terms (comma separated)'); datasets=st.text_input('Dataset terms (comma separated)')
    if not ids: st.info('Select saved publications.'); return
    if not st.button('Analyze collection'): return
    data=research_analytics(lib.sessions,ids,{'Method':[x.strip() for x in methods.split(',') if x.strip()],'Dataset':[x.strip() for x in datasets.split(',') if x.strip()]})
    a,b=st.columns(2); a.metric('Selected papers',data['papers']); b.metric('Unknown publication year',data['unknown_year'])
    for name in ['years','topics','authors','institutions']:
        st.subheader(name.capitalize()); values=data[name]
        if values: st.bar_chart(pd.DataFrame({'label':list(map(str,values)),'papers':list(values.values())}).set_index('label'))
        else: st.caption('No available metadata.')
    st.subheader('Topic coverage by year'); st.dataframe(pd.DataFrame(data['topic_year']))
    st.subheader('Method and dataset mentions (not confirmed usage)'); st.dataframe(pd.DataFrame(data['mentions']))
    st.subheader('Candidate research leads'); st.caption('Reported limitations and future work require independent literature validation.')
    for lead in data['leads']:
        with st.expander(lead['paper']+' · '+lead['type']): st.write(lead['suggestion']); st.text(lead['evidence']); st.caption(lead['reference'])
    if not data['leads']: st.info('No reported limitations or future work extracted.')
