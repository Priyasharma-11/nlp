import json
import streamlit as st
from researchmind.providers.literature import LiteratureClient
from researchmind.services.science import Science
from researchmind.ui.intelligence import paper_intelligence

@st.cache_resource
def client(): return LiteratureClient()

def search_metadata(provider,query,page,cloud):
    if not cloud: return client().search(provider,query,page)
    # No cross-session query cache; close HTTP connections immediately.
    instance=LiteratureClient()
    try: return instance.search(provider,query,page,size=5)
    finally: instance.close()

def discover(lib):
    cloud=getattr(lib,'cloud',False)
    st.title('Discover papers'); st.caption('Public metadata search. Search terms are sent to the selected provider; PDFs are not.')
    with st.form('discover'):
        provider=st.selectbox('Source',['OpenAlex','Crossref','arXiv']); query=st.text_input('Research topic or title',max_chars=500); page=st.number_input('Page',1,20,1)
        submit=st.form_submit_button('Search literature',type='primary')
    if submit:
        st.session_state.pop('discovery_results',None)
        try:
            with st.spinner('Retrieving scientific metadata...'): st.session_state.discovery_results=search_metadata(provider,query,int(page),cloud)
        except ValueError as exc: st.error(str(exc))
    results=st.session_state.get('discovery_results')
    if results is None: st.info('Search a public academic index to begin.'); return
    if not results: st.info('No results returned by this source.'); return
    service=Science(lib.sessions)
    for i,r in enumerate(results):
        with st.container(border=True):
            st.text(r.title); st.caption(f'{r.provider} · {r.year or "Unknown year"} · {r.access}')
            st.text(', '.join(r.authors)); st.text(r.abstract or 'No abstract supplied.')
            st.text('Publication URL: '+str(r.url)); st.text('DOI: '+str(r.doi or 'Unavailable'))
            if r.pdf_url: st.text('Provider-reported PDF URL (not downloaded): '+str(r.pdf_url))
            if st.button('Save to library',key=f'save_result_{i}'):
                try: service.save_record(r); st.success('Saved with original metadata and provenance.')
                except ValueError as exc: st.error(str(exc))

def analyzer(lib):
    st.title('Paper analyzer'); st.caption('PDF text extraction on the application server with original page references. Extractive scientific summaries use stored evidence.')
    papers=lib.papers(); service=Science(lib.sessions)
    if not papers: st.info('Save a paper in Discover papers or enter metadata in Library first.'); return
    names={p.id:p.title for p in papers}; paper=st.selectbox('Select paper',list(names),format_func=names.get)
    for source in service.sources(paper):
        with st.expander(f'{source.provider} metadata · {source.retrieved_at}'): st.json(json.loads(source.normalized))
    file=st.file_uploader('Upload an authorized public PDF (max 5 MiB)' if getattr(lib,'cloud',False) else 'Upload an authorized PDF (max 20 MiB)',type=['pdf'])
    if file is not None and st.button('Extract PDF',type='primary'):
        try:
            with st.spinner('Extracting PDF text...'): service.upload(paper,file.name,file.getvalue())
            st.success('PDF saved and text extracted.')
        except ValueError as exc: st.error(str(exc))
    for doc in service.documents(paper):
        with st.expander(doc.filename):
            meta=json.loads(doc.metadata_json); st.caption(f'{meta["page_count"]} pages · SHA-256 {doc.sha256[:12]}…')
            if meta['empty_pages']: st.warning(f'No text detected on pages {meta["empty_pages"]}. OCR is not implemented; these pages require manual review.')
            st.download_button('Original PDF',doc.original,file_name=doc.filename,mime='application/pdf',key=f'pdf_{doc.id}')
            blocks=service.passages(doc.id); sections=sorted({b.section for b in blocks}); selected=st.multiselect('Sections',sections,default=sections,key=f'sections_{doc.id}')
            for b in blocks:
                if b.section in selected: st.caption(f'Page {b.page} · {b.section}'); st.text(b.text)
            if not blocks: st.info('No extractable text found.')

    paper_intelligence(lib,paper)
