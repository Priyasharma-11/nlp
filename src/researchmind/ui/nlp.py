import json
import streamlit as st
import pandas as pd
from researchmind.nlp.pipeline import inspect,representations,topics,classify,scientific_entities,scientific_ner,word_vectors
from researchmind.services.retrieval import corpus
from researchmind.retrieval.search import Index
from researchmind.retrieval.embeddings import MODELS
from researchmind.retrieval.evaluation import evaluate
METHODS=['Keyword','TF-IDF','BM25','Semantic','Hybrid']

def laboratory(lib):
    st.title('NLP laboratory'); st.caption('Inspect actual transformations; original scientific text is preserved.')
    records=corpus(lib); tabs=st.tabs(['Preprocessing','Representations','Topics','Classification','Scientific entities','Embeddings'])
    with tabs[0]:
        text=st.text_area('Scientific text',max_chars=30000)
        if st.button('Analyze text') and text.strip():
            out=inspect(text)
            for warning in out.pop('warnings'): st.warning(warning)
            for key,value in out.items():
                with st.expander(key,expanded=key=='tokens'): st.write(value)
    with tabs[1]:
        st.caption('Bag of Words and TF-IDF, fitted on the saved paper metadata corpus.')
        if st.button('Build representations'):
            try:
                _,bow,names,tf,tf_names=representations([r.text for r in records])
                st.write('Corpus shape',bow.shape); st.dataframe(pd.DataFrame({'term':names,'count':bow.sum(axis=0).A1}).sort_values('count',ascending=False).head(40)); st.dataframe(pd.DataFrame({'term':tf_names,'mean TF-IDF':tf.mean(axis=0).A1}).sort_values('mean TF-IDF',ascending=False).head(40))
            except ValueError as exc: st.warning(str(exc))
    with tabs[2]:
        method=st.selectbox('Topic model',['NMF','LDA']); n=st.slider('Topics',2,10,3)
        if st.button('Discover topics'):
            try:
                terms,weights=topics([r.text for r in records],n,method); st.write(terms); st.dataframe(pd.DataFrame(weights,index=[r.title for r in records])); st.caption('Exploratory model weights, not validated scientific domains.')
            except ValueError as exc: st.warning(str(exc))
    with tabs[3]:
        st.caption('Supply JSON mapping saved paper IDs to human-assigned labels. At least four papers per class. Held-out evaluation is exploratory.')
        st.dataframe([{'id':r.id,'title':r.title} for r in records]); raw=st.text_area('Label mapping (JSON)',value='{}')
        if st.button('Train and evaluate classifier'):
            try:
                labels=json.loads(raw); selected=[r for r in records if str(r.id) in labels]; _,result=classify([r.text for r in selected],[str(labels[str(r.id)]) for r in selected]); st.json(result)
            except (ValueError,TypeError,AttributeError) as exc: st.error(str(exc))

    with tabs[4]:
        st.caption('Use a local zero-shot scientific NER model for flexible entity labels, or your own terminology list for exact matching.')
        mode=st.radio('Recognition method',['Local scientific NER (GLiNER)','User terminology dictionary'],horizontal=True)
        entity_text=st.text_area('Scientific text',max_chars=30000,key='ner_text')
        if mode.startswith('Local'):
            st.info('GLiNER can recognize labels across scientific fields. Results are model predictions, not verified annotations. Model weights must already exist on your computer; ResearchMind will not download them automatically.')
            model_path=st.text_input('Local GLiNER model folder',placeholder=r'C:\\models\\gliner')
            labels_text=st.text_input('Entity labels (comma-separated)',value='method, dataset, disease, gene, protein, chemical, task, material, metric, organism')
            threshold=st.slider('Confidence threshold',0.05,0.95,0.35,0.05)
            if st.button('Run scientific NER'):
                try:
                    labels=[x.strip() for x in labels_text.split(',') if x.strip()]
                    found=scientific_ner(entity_text,labels,model_path,threshold)
                    if found:
                        st.dataframe(pd.DataFrame(found),use_container_width=True)
                        st.caption('Offsets refer to the original text. Review predictions before using them as research evidence.')
                    else: st.info('No entities found above the selected threshold.')
                except ValueError as exc: st.error(str(exc))
        else:
            st.caption('Exact, boundary-aware matches only. This is not machine-learned NER.')
            lex=st.text_area('Entity lexicon (JSON)',max_chars=10000,value='{"METHOD": [], "DATASET": [], "DISEASE": []}')
            if st.button('Find scientific terminology'):
                try: st.dataframe(scientific_entities(entity_text,json.loads(lex)),use_container_width=True)
                except (ValueError,TypeError) as exc: st.error(str(exc))
    with tabs[5]:
        if getattr(lib,"cloud",False):
            st.info("Word2Vec and transformer inference are available in the local edition, not the free cloud demo."); return
        st.caption('Compare actual local representations; model weights must be installed explicitly.')
        word=st.text_input('Word for Word2Vec exploration')
        if st.button('Train exploratory Word2Vec'):
            try: st.write(word_vectors([r.text for r in records],word))
            except ValueError as exc: st.error(str(exc))
        a=st.text_area('Text A'); b=st.text_area('Text B'); models=st.multiselect('Compare embedding models',list(MODELS))
        if st.button('Compare embeddings') and a.strip() and b.strip():
            from researchmind.retrieval.embeddings import encode
            import numpy as np
            for model in models:
                try:
                    x,y=encode([a,b],model,'paper'); st.write(model,{'dimension':len(x),'cosine':float(x@y/max(1e-12,np.linalg.norm(x)*np.linalg.norm(y)))})
                except ValueError as exc: st.warning(str(exc))

def search(lib):
    st.title('Semantic search'); st.caption('Search saved title and abstract metadata. Scores are ranking signals, not probabilities.')
    records=corpus(lib)
    if not records: st.info('Save papers in Discover papers or Library first.'); return
    query=st.text_input('Research question or keywords'); method=st.selectbox('Ranking',METHODS[:3] if getattr(lib,'cloud',False) else METHODS,index=2); model=st.selectbox('Local embedding model',list(MODELS),disabled=getattr(lib,'cloud',False)); weight=st.slider('Semantic weight (hybrid only)',0.,1.,.5,disabled=getattr(lib,'cloud',False)); k=st.slider('Results',1,30,10)
    author=st.text_input('Author filter'); topic=st.text_input('Topic filter'); year=st.text_input('Publication year (optional)')
    selected=st.selectbox('Related-paper seed (optional)',[None]+[r.id for r in records],format_func=lambda x: 'None' if x is None else next(r.title for r in records if r.id==x))
    if st.button('Search saved papers'):
        try:
            filtered=[r for r in records if author.casefold() in r.authors.casefold() and topic.casefold() in r.topics.casefold() and (not year.strip() or r.year==int(year))]
            index=Index(filtered); kwargs=dict(method=method,model=model,k=k,weight=weight)
            if selected is None: result=index.search(query,**kwargs)
            else:
                seed=next(r for r in records if r.id==selected); result=index.search(seed.scientific_text,exclude=selected,role='paper',**kwargs)
            if not result: st.info('No positive-scoring matches in this collection.')
            for r,score in result:
                with st.container(border=True):
                    st.text(r.title); st.caption(f'Paper {r.id} · {r.year or "Unknown year"} · {method} score {score:.4f}'); st.text(r.abstract or 'Abstract unavailable'); st.caption('Matched by '+method+'; inspect original paper before drawing conclusions.')
        except ValueError as exc: st.error(str(exc))

def evaluation(lib):
    st.title('Evaluation'); st.caption('Measure retrieval on your own relevance judgments. No default performance scores.')
    records=corpus(lib); st.dataframe([{'id':r.id,'title':r.title} for r in records]); raw=st.text_area('Judged queries (JSON)',max_chars=20000,value='[]',help='List of objects with query and relevant_ids (saved paper IDs).')
    methods=st.multiselect('Methods',METHODS[:3] if getattr(lib,'cloud',False) else METHODS,default=METHODS[:3]); k=st.slider('Cutoff K',1,30,10); model=st.selectbox('Embedding model',list(MODELS))
    if st.button('Run benchmark'):
        try:
            if not methods: raise ValueError('Select at least one method.')
            judgments=json.loads(raw)
            if getattr(lib,'cloud',False) and (not isinstance(judgments,list) or len(judgments)>20): raise ValueError('Cloud demo supports up to 20 judged queries.')
            result=evaluate(Index(records),judgments,methods,k,model); st.dataframe(result); st.download_button('Export results',json.dumps(result,indent=2),'retrieval-evaluation.json','application/json'); st.caption('Binary relevance; MRR truncated at K. Small or incomplete judgments limit generalization.')
        except (ValueError,TypeError,KeyError,AttributeError) as exc: st.error(str(exc))
