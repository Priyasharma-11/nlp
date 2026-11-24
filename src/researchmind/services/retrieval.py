import json
from sqlalchemy import select
from researchmind.db.models import Paper
from researchmind.db.science import SourceRecord, Document, Passage
from researchmind.retrieval.search import Record

def corpus(lib, full_text=False):
    """Return metadata records or searchable PDF passage records with paper provenance."""
    with lib.sessions() as s:
        sources={}
        for item in s.scalars(select(SourceRecord).order_by(SourceRecord.id)):
            data=json.loads(item.normalized)
            sources.setdefault(item.paper_id,[]).append(data)
        def strings(value):
            if isinstance(value,list): return ' '.join(str(x.get('name','')) if isinstance(x,dict) else str(x) for x in value)
            return str(value or '')
        papers=list(s.scalars(select(Paper).order_by(Paper.id)))
        metadata={}
        for p in papers:
            metadata[p.id]=Record(p.id,p.title,p.abstract,p.year,
                ' '.join(strings(d.get('authors')) for d in sources.get(p.id,[])),
                ' '.join(strings(d.get('topics')) for d in sources.get(p.id,[])))
        if not full_text: return list(metadata.values())
        rows=s.execute(select(Paper,Document,Passage).join(Document,Document.paper_id==Paper.id)
                       .join(Passage,Passage.document_id==Document.id)
                       .order_by(Paper.id,Passage.page,Passage.ordinal)).all()
        indexed=[]; with_text=set()
        for paper,document,passage in rows:
            base=metadata[paper.id]; with_text.add(paper.id)
            indexed.append(Record(base.id,base.title,passage.text,base.year,base.authors,base.topics,
                                  page=passage.page,section=passage.section,document_id=document.id,full_text=True))
        indexed.extend(record for pid,record in metadata.items() if pid not in with_text)
        return indexed
