from collections import Counter,defaultdict
import json
from sqlalchemy import select
from researchmind.db.models import Paper
from researchmind.db.science import SourceRecord
from researchmind.services.intelligence import Intelligence
from researchmind.documents.intelligence import analyze
from researchmind.nlp.pipeline import scientific_entities

def research_analytics(sessions,paper_ids,lexicon=None):
    ids=list(dict.fromkeys(paper_ids)); service=Intelligence(sessions)
    with sessions() as s:
        papers=list(s.scalars(select(Paper).where(Paper.id.in_(ids))))
        sources=list(s.scalars(select(SourceRecord).where(SourceRecord.paper_id.in_(ids))))
    topics=defaultdict(set); authors=defaultdict(set); institutions=defaultdict(set); mentions=defaultdict(set); leads=[]; topic_year=defaultdict(set)
    years={p.id:p.year for p in papers}
    for r in sources:
        data=json.loads(r.normalized); raw=json.loads(r.raw)
        for t in data.get('topics') or []:
            topics[t].add(r.paper_id)
            if years[r.paper_id]: topic_year[(years[r.paper_id],t)].add(r.paper_id)
        for a in data.get('authors') or []: authors[a].add(r.paper_id)
        for a in raw.get('authorships',[]) or []:
            for inst in a.get('institutions',[]) or []:
                if inst.get('display_name'): institutions[inst['display_name']].add(r.paper_id)
    for p in papers:
        ev=service.evidence(p.id); fields=analyze(ev)
        for e in ev:
            if e.section=='References': continue
            for m in scientific_entities(e.text,lexicon or {}): mentions[(m['type'],m['text'].casefold())].add(p.id)
        for field in ('Limitations','Future work'):
            for e in fields[field]: leads.append({'paper':p.title,'paper_id':p.id,'type':field,'evidence':e.text,'reference':e.reference(),'suggestion':'Investigate whether subsequent studies address this reported issue.'})
    return {'papers':len(papers),'unknown_year':sum(p.year is None for p in papers),'years':dict(sorted(Counter(p.year for p in papers if p.year is not None).items())), 'topics':{k:len(v) for k,v in topics.items()},'authors':{k:len(v) for k,v in authors.items()},'institutions':{k:len(v) for k,v in institutions.items()},'mentions':[{'type':k[0],'term':k[1],'papers':len(v)} for k,v in mentions.items()], 'topic_year':[{'year':k[0],'topic':k[1],'papers':len(v)} for k,v in sorted(topic_year.items())], 'leads':leads}
