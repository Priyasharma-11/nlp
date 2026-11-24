"""Evidence-backed graph reconstructed from persistent records on demand."""
import json,re
from collections import Counter
import networkx as nx
from sqlalchemy import select
from researchmind.db.models import Paper
from researchmind.db.science import SourceRecord
from researchmind.services.intelligence import Intelligence
from researchmind.nlp.pipeline import scientific_entities
from researchmind.schemas import PaperCreate

def identifier(value):
    value=str(value or '').strip()
    if re.fullmatch(r'(?:https?://openalex.org/)?W\d+',value,re.I): return 'openalex:'+value.rsplit('/',1)[-1].upper()
    try:
        doi=PaperCreate(title='validation',doi=value).doi
        if doi: return 'doi:'+doi.casefold()
    except ValueError: pass
    return None

def build_graph(sessions, paper_ids=None, lexicon=None):
    g=nx.MultiDiGraph(); service=Intelligence(sessions)
    with sessions() as s:
        all_papers=list(s.scalars(select(Paper).order_by(Paper.id))); sources=list(s.scalars(select(SourceRecord).order_by(SourceRecord.id)))
    selected={p.id for p in all_papers} if paper_ids is None else set(paper_ids)
    papers={p.id:p for p in all_papers}; aliases={}; counts={}
    def paper_node(pid):
        p=papers[pid]; key=f'paper:{pid}'; g.add_node(key,label=p.title,kind='Paper',year=p.year,doi=p.doi); return key
    def edge(a,b,relation,provenance):
        key=relation
        if g.has_edge(a,b,key):
            if provenance not in g[a][b][key]['evidence']: g[a][b][key]['evidence'].append(provenance)
        else: g.add_edge(a,b,key=key,relation=relation,evidence=[provenance])
    for p in all_papers:
        if p.doi: aliases.setdefault(identifier(p.doi),set()).add(p.id)
        if p.id in selected: paper_node(p.id)
    for source in sources:
        ident=identifier(source.external_id)
        if ident: aliases.setdefault(ident,set()).add(source.paper_id)
    for source in sources:
        if source.paper_id not in selected: continue
        p=paper_node(source.paper_id); data=json.loads(source.normalized); raw=json.loads(source.raw)
        provenance={'source_id':source.id,'provider':source.provider,'retrieved_at':source.retrieved_at}
        count=data.get('citations')
        if isinstance(count,int): counts.setdefault(source.paper_id,[]).append({**provenance,'count':count})
        for ref in data.get('references',[]) or []:
            ident=identifier(ref)
            if not ident: continue
            matches=aliases.get(ident,set())
            if len(matches)==1: target=paper_node(next(iter(matches)))
            else:
                target='external:'+ident; g.add_node(target,label=ident,kind='External reference')
            if target!=p: edge(p,target,'cites',{**provenance,'reference':ref})
        # Provider-specific stable IDs where available; otherwise keep names scoped to a paper.
        authorships=raw.get('authorships',[]) if source.provider=='OpenAlex' else []
        if authorships:
            for i,a in enumerate(authorships):
                author=a.get('author') or {}; name=author.get('display_name')
                if not name: continue
                aid='author:'+str(author.get('id') or f'{source.id}:{i}'); g.add_node(aid,label=name,kind='Author'); edge(aid,p,'wrote',{**provenance,'author':name})
                for inst in a.get('institutions',[]) or []:
                    if not inst.get('display_name'): continue
                    iid='institution:'+str(inst.get('id') or f'{source.id}:{i}:{inst["display_name"]}'); g.add_node(iid,label=inst['display_name'],kind='Institution'); edge(aid,iid,'reported affiliation',{**provenance,'author':name,'institution':inst['display_name']})
        else:
            for i,name in enumerate(data.get('authors',[]) or []):
                if not name: continue
                aid=f'author:{source.id}:{i}'; g.add_node(aid,label=name,kind='Author'); edge(aid,p,'wrote',{**provenance,'author':name})
        for topic in data.get('topics',[]) or []:
            if topic:
                tid='topic:'+topic.casefold(); g.add_node(tid,label=topic,kind='Topic'); edge(p,tid,'indexed topic',{**provenance,'topic':topic})
    for pid in sorted(selected & papers.keys()):
        for e in service.evidence(pid):
            if e.section=='References': continue
            for match in scientific_entities(e.text,lexicon or {}):
                kind=match['type']; term=match['text']; node=f'entity:{kind}:{term.casefold()}'; g.add_node(node,label=term,kind=kind)
                edge(paper_node(pid),node,'mentions',{'reference':e.reference(),'text':e.text,'start':match['start'],'end':match['end']})
    for pid,values in counts.items(): g.nodes[f'paper:{pid}']['citation_counts']=values
    return g

def citation_rows(g):
    rows=[]
    for node,d in g.nodes(data=True):
        if d['kind']!='Paper': continue
        rows.append({'paper':d['label'],'year':d.get('year'),'incoming in graph':sum(1 for _,_,a in g.in_edges(node,data=True) if a['relation']=='cites'),'outgoing in graph':sum(1 for _,_,a in g.out_edges(node,data=True) if a['relation']=='cites'),'provider counts':d.get('citation_counts',[])})
    return sorted(rows,key=lambda r:(-r['incoming in graph'],r['paper']))

def graph_figure(g):
    import plotly.graph_objects as go
    if len(g)>500: raise ValueError('Graph exceeds 500 nodes. Select fewer papers or terms.')
    pos=nx.spring_layout(g,seed=42); fig=go.Figure()
    for a,b,d in g.edges(data=True):
        x,y=pos[a]; xx,yy=pos[b]; fig.add_trace(go.Scatter(x=[x,xx],y=[y,yy],mode='lines',line={'width':1,'color':'#9aaabb'},hoverinfo='skip',showlegend=False))
    palette=['#345F8E','#3A8A7A','#71669C','#B28C52','#536473']
    for i,kind in enumerate(sorted({d['kind'] for _,d in g.nodes(data=True)})):
        nodes=[n for n,d in g.nodes(data=True) if d['kind']==kind]; fig.add_trace(go.Scatter(x=[pos[n][0] for n in nodes],y=[pos[n][1] for n in nodes],mode='markers',name=kind,text=[g.nodes[n]['label'] for n in nodes],hovertemplate='%{text}<extra></extra>',marker={'size':13,'color':palette[i%len(palette)]}))
    fig.update_layout(height=580,xaxis={'visible':False},yaxis={'visible':False},margin={'l':10,'r':10,'t':10,'b':10},hovermode='closest',dragmode='pan')
    return fig
