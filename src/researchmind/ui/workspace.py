import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from researchmind.config import Settings
from researchmind.db.engine import initialize
from researchmind.services.library import Library
from researchmind.ui.science import discover, analyzer
from researchmind.ui.nlp import laboratory, search, evaluation
from researchmind.ui.intelligence import comparison, knowledge_graph
from researchmind.ui.reasoning import reasoning_page, analytics_page
from researchmind.ui.quality import quality_panel
from researchmind.schemas import PaperCreate, CollectionCreate

PAGES = {'Welcome':0,'Overview':0,'Library':0,'Discover papers':0,'Paper analyzer':0,'NLP laboratory':4,'Semantic search':4,'Compare papers':5,'Knowledge graph':5,'Research assistant':6,'Claim verification':6,'Research analytics':6,'Evaluation':7,'About & methodology':0}
CSS = '''<style>.block-container{max-width:1180px;padding-top:2.3rem}h1,h2,h3{letter-spacing:-.035em} [data-testid="stMetric"]{background:#fff;border:1px solid #dce4ee;border-radius:12px;padding:18px} [data-testid="stSidebar"]{border-right:1px solid #dce4ee} .rm-hero{background:#17283c;color:white;border-radius:16px;padding:32px;margin-bottom:24px}.rm-hero h1{color:white;font-size:2.4rem;margin:0}.rm-hero p{color:#dbe7f5;font-size:1.1rem}.rm-kicker{color:#345f8e;font-size:.78rem;letter-spacing:.12em;font-weight:700}
[data-testid="stSidebar"] {background:#17283c;color:#f2f5f9}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span {color:#f2f5f9}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:12px}
.stButton button,.stDownloadButton button {border-radius:8px;min-height:40px;font-weight:600}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea {border-radius:8px}
button:focus-visible,input:focus-visible,textarea:focus-visible {outline:3px solid #3a8a7a;outline-offset:2px}
[data-testid="stMetricValue"] {font-variant-numeric:tabular-nums}
@media(max-width:700px){.block-container{padding:1rem}.rm-hero{padding:20px}.rm-hero h1{font-size:1.8rem}}
</style>'''
@st.cache_resource
def get_library(path): return Library(initialize(path))
def main(cloud=False):
    st.set_page_config(page_title='ResearchMind',page_icon='📚',layout='wide')
    st.markdown(CSS,unsafe_allow_html=True)
    st.sidebar.title('ResearchMind')
    st.sidebar.caption('SCIENTIFIC INTELLIGENCE / v0.9')
    page=st.sidebar.radio('Workspace',list(PAGES),label_visibility='collapsed',key='page')
    st.sidebar.divider()
    st.sidebar.caption('Temporary cloud demo' if cloud else 'Local workspace · Release candidate')
    if cloud:
        from researchmind.cloud import workspace, reset_workspace
        st.sidebar.button('Reset demo workspace', on_click=lambda: reset_workspace(st.session_state))
        st.warning('Cloud demo: use public or non-sensitive authorized material only. Files and text are processed on the hosting server. Data is temporary and can disappear on refresh, disconnect or restart. Heavy AI models are disabled.')
        if not st.checkbox('I understand — use temporary demo workspace', key='cloud_consent'):
            st.stop()
    try: lib=workspace(st.session_state) if cloud else get_library(Settings.from_env().database)
    except (OSError, SQLAlchemyError): st.error('Cannot open local database. Check folder permissions.'); return
    if cloud:
        from researchmind.services.demo import load_demo, PAPERS
        if st.sidebar.button('Load demo papers',type='primary'):
            try:
                added=load_demo(lib)
                st.success(f'Demo collection ready: {added} new papers added.')
            except (ValueError, SQLAlchemyError):
                st.error('Could not load the demo collection. Check workspace limits or reset the workspace.')
        if page=='Welcome':
            with st.expander('Demo collection: six real NLP papers',expanded=True):
                st.caption('Click Load demo papers in the sidebar. These records include editorial summaries, not author abstracts or full PDFs.')
                for title,year,doi,url,authors,topics,note in PAPERS:
                    st.markdown(f'**[{title}]({url})** · {year}')
                    st.caption(note)
    st.markdown('<div class="rm-kicker">RESEARCHMIND / WORKSPACE</div>',unsafe_allow_html=True)
    try: render(page,lib)
    except SQLAlchemyError: st.error('Database operation failed. Check local storage and retry.')
    except (ValueError, ImportError, RuntimeError, OSError): st.error('This operation could not finish. Check input, local resources and model installation, then retry.')
def render(page,lib):
    if page=='Discover papers': return discover(lib)
    if page=='Paper analyzer': return analyzer(lib)
    if page=='NLP laboratory': return laboratory(lib)
    if page=='Semantic search': return search(lib)
    if page=='Compare papers': return comparison(lib)
    if page=='Knowledge graph': return knowledge_graph(lib)
    if page=='Research assistant': return reasoning_page(lib)
    if page=='Claim verification': return reasoning_page(lib,True)
    if page=='Research analytics': return analytics_page(lib)
    if page=='Evaluation':
        evaluation(lib); quality_panel(cloud=getattr(lib,"cloud",False)); return
    if PAGES[page]:
        st.title(page); st.info(f'Planned for approval gate {PAGES[page]}. This module is not implemented yet. No model outputs or scientific results are simulated.'); return
    if page=='Welcome':
        st.markdown('<div class="rm-hero"><p>RESEARCH WORKSPACE / SCIENTIFIC INTELLIGENCE</p><h1>Discover knowledge.<br>Understand evidence.</h1><p>A workspace for scientific literature intelligence.</p></div>',unsafe_allow_html=True)
        st.button('Open research workspace',on_click=lambda: setattr(st.session_state,'page','Overview'),type='primary')
        cols=st.columns(3)
        for col,title,body in zip(cols,['Discover','Understand','Reason'],['Available: academic discovery. Local lexical and optional hybrid retrieval.','Available: local PDF extraction. NLP laboratory available.','Available: evidence retrieval and experimental claim assessment.']):
            with col: st.subheader(title); st.write(body)
        st.divider(); st.subheader('How it works'); st.write('Save publications → Upload authorized PDFs → Retrieve evidence → Inspect sources and evaluate results.'); st.caption('No paid API required · ResearchMind 0.9')
    elif page=='Overview':
        st.title('Research overview'); st.caption('Live counts from your workspace database')
        stats=lib.overview()
        for col,label,key in zip(st.columns(3),['Saved papers','Collections','Collection memberships'],['papers','collections','memberships']): col.metric(label,stats[key])
        st.subheader('Recent activity')
        if not stats['activity']: st.info('Your workspace is empty. Add a metadata record or create a collection in Library.')
        for entry in stats['activity']: st.write(entry.event, '·', entry.created_at.isoformat(timespec='minutes'), 'UTC')
        st.subheader('Publication coverage')
        import pandas as pd
        years=pd.Series([p.year for p in lib.papers() if p.year is not None],dtype='int64').value_counts().sort_index()
        if not years.empty: st.bar_chart(years)
        else: st.caption('No publication years available yet.')
        st.subheader('Recently saved papers')
        for paper in lib.papers()[:5]: st.text(paper.title)
        st.button('Manage library',on_click=lambda: setattr(st.session_state,'page','Library'))
    elif page=='Library':
        st.title('Research library'); st.caption('Saved metadata and locally uploaded documents. Manual entries are unverified.')
        with st.expander('Add paper metadata'):
            with st.form('paper'):
                title=st.text_input('Paper title'); year=st.text_input('Publication year (optional)'); doi=st.text_input('DOI (optional)'); abstract=st.text_area('Abstract (optional)')
                if st.form_submit_button('Save paper'):
                    try: lib.add_paper(PaperCreate(title=title,year=year or None,doi=doi or None,abstract=abstract)); st.success('Metadata saved locally.')
                    except ValueError as exc: st.error(str(exc))
        with st.expander('Create collection'):
            with st.form('collection'):
                name=st.text_input('Collection name'); desc=st.text_area('Description')
                if st.form_submit_button('Create collection'):
                    try: lib.add_collection(CollectionCreate(name=name,description=desc)); st.success('Collection created.')
                    except ValueError as exc: st.error(str(exc))
        papers=lib.papers(st.text_input('Filter saved paper titles')); collections=lib.collections()
        if not papers: st.info('No matching saved papers.')
        for p in papers:
            with st.container(border=True):
                st.text(p.title); st.caption(f'{p.year or "Year unknown"} · {p.doi or "No DOI"} · {p.access_level}')
                if p.abstract: st.text(p.abstract)
                if collections:
                    names={c.id:c.name for c in collections}
                    chosen=st.selectbox('Collection',list(names),format_func=names.get,key=f'col{p.id}')
                    if st.button('Add to collection',key=f'assign{p.id}'):
                        st.success('Added.' if lib.assign(chosen,p.id) else 'Already in collection.')
                if st.checkbox('Confirm deletion',key=f'confirm{p.id}') and st.button('Delete paper',key=f'del{p.id}'):
                    lib.delete_paper(p.id); st.rerun()
        st.subheader('Collections')
        for c in collections:
            with st.expander(c.name):
                st.text(c.description); members=lib.members(c.id)
                if not members: st.caption('Empty collection')
                for p in members: st.text(p.title)
    else:
        st.title('About ResearchMind'); st.write('Modular Python monolith with Streamlit, SQLAlchemy, SQLite and Pydantic. Public metadata APIs and server-side PDF extraction. No external AI services configured.'); st.write('See docs/phase1 for approved architecture, source policies, model evaluation and roadmap.')
