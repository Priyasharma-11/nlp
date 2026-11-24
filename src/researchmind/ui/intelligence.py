import json
import pandas as pd
import streamlit as st
from researchmind.documents.intelligence import analyze,summarize,FIELDS
from researchmind.services.intelligence import Intelligence
from researchmind.services.science import Science
from researchmind.graph.network import build_graph,citation_rows,graph_figure

def csv_safe(value):
    if isinstance(value,str) and value.lstrip().startswith(('=', '+', '-', '@')):
        return "'"+value
    return value

def show_evidence(items):
    if not items: st.caption('Not reliably extracted from available evidence.'); return
    for e in items:
        st.text(e.text); st.caption(e.reference())

def paper_intelligence(lib,paper):
    service=Intelligence(lib.sessions); docs=Science(lib.sessions).documents(paper)
    chosen=st.selectbox('Document version for analysis',[d.id for d in docs] or [None],index=max(0,len(docs)-1),format_func=lambda i:next((d.filename for d in docs if d.id==i),'Abstract only'),key='analysis_version')
    evidence=service.evidence(paper,chosen)
    st.subheader('Structured paper intelligence'); st.caption('Extractive, heuristic analysis; passages are not independently verified findings. Missing fields are not proof of absence.')
    if not evidence: st.info('No readable evidence. Upload a PDF or save an abstract.'); return
    mode=st.selectbox('Summary mode',['Full text','Abstract','Section','Technical']); section=st.selectbox('Summary section',sorted({e.section for e in evidence})) if mode=='Section' else None
    if not any(e.document_id for e in evidence): st.warning('Abstract-only evidence; full-paper analysis unavailable.')
    show_evidence(summarize(evidence,mode,section))
    for name,items in analyze(evidence).items():
        with st.expander(name): show_evidence(items)

def comparison(lib):
    st.title('Compare papers'); st.caption('Compare extracted passages, not normalized experimental effect sizes. Missing fields remain unknown.')
    names={p.id:p.title for p in lib.papers()}; ids=st.multiselect('Select 2–10 papers',list(names),format_func=names.get,max_selections=10)
    if len(ids)<2: st.info('Select at least two saved papers.'); return
    records=Intelligence(lib.sessions).compare(ids)
    rows=[]
    for field in ['Publication year','DOI',*FIELDS]:
        row={'Field':field}
        for p in records:
            label=f'{p["title"]} [{p["id"]}]'
            row[label]=str(p['year'] or 'Unknown') if field=='Publication year' else (p['doi'] or 'Unknown') if field=='DOI' else '\n\n'.join(f'{e.text} ({e.reference()})' for e in p['fields'][field]) or 'Not reliably extracted'
        rows.append(row)
    frame=pd.DataFrame(rows); st.dataframe(frame,hide_index=True,use_container_width=True); st.download_button('Export comparison CSV',frame.map(csv_safe).rename(columns=csv_safe).to_csv(index=False).encode('utf-8'),file_name='comparison.csv',mime='text/csv')
    for p in records:
        with st.expander(f'Inspect evidence: {p["title"]}'):
            for field,items in p['fields'].items(): st.markdown(f'**{field}**'); show_evidence(items)

def knowledge_graph(lib):
    st.title('Knowledge graph'); st.caption('Provider-reported citations and authorship; terminology matches are mentions, not proof of method usage.')
    names={p.id:p.title for p in lib.papers()}
    if not names: st.info('Save scientific papers first.'); return
    ids=st.multiselect('Papers to explore',list(names),default=list(names)[:5],format_func=names.get,max_selections=20)
    methods=st.text_input('Method terms (comma-separated)'); datasets=st.text_input('Dataset terms (comma-separated)')
    lexicon={k:[t.strip() for t in v.split(',') if t.strip()][:30] for k,v in [('Method',methods),('Dataset',datasets)]}
    g=build_graph(lib.sessions,ids,lexicon)
    if not len(g): st.info('Select papers to explore.'); return
    kinds=sorted({d['kind'] for _,d in g.nodes(data=True)}); selected=st.multiselect('Node types',kinds,default=kinds)
    view=g.subgraph([n for n,d in g.nodes(data=True) if d['kind'] in selected]).copy()
    st.metric('Visible entities',len(view)); st.metric('Visible relationships',view.number_of_edges())
    try: st.plotly_chart(graph_figure(view),use_container_width=True)
    except ValueError as exc: st.warning(str(exc))
    st.subheader('Relationship evidence'); edges=[{'from':g.nodes[a]['label'],'to':g.nodes[b]['label'],'relationship':d['relation'],'evidence':d['evidence']} for a,b,d in view.edges(data=True)]
    if edges:
        st.dataframe([{**e,'evidence':json.dumps(e['evidence'],ensure_ascii=False)} for e in edges],hide_index=True)
        st.download_button('Export visible graph JSON',json.dumps({'nodes':[{'id':n,**d} for n,d in view.nodes(data=True)],'edges':[{'from_id':a,'to_id':b,**d} for a,b,d in view.edges(data=True)]},ensure_ascii=False,indent=2),file_name='knowledge-graph.json',mime='application/json')
    else: st.info('No evidence-backed relationships for this selection.')
    st.subheader('Citation analysis'); st.caption('Counts are provider-specific snapshots. In-graph counts cover only loaded relationships, not global quality.')
    rows=citation_rows(g); st.dataframe([{**r,'provider counts':json.dumps(r['provider counts'])} for r in rows],hide_index=True)
    years=pd.Series([r['year'] for r in rows if r['year'] is not None],dtype='int64').value_counts().sort_index()
    if not years.empty: st.bar_chart(years)
