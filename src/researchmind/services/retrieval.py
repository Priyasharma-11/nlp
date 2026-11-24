import json
from sqlalchemy import select
from researchmind.db.models import Paper
from researchmind.db.science import SourceRecord
from researchmind.retrieval.search import Record,Index

def corpus(lib):
    with lib.sessions() as s:
        sources={}
        for item in s.scalars(select(SourceRecord).order_by(SourceRecord.id)):
            data=json.loads(item.normalized); sources.setdefault(item.paper_id,[]).append(data)
        def strings(value):
            if isinstance(value,list): return ' '.join(str(x.get('name','')) if isinstance(x,dict) else str(x) for x in value)
            return str(value or '')
        return [Record(p.id,p.title,p.abstract,p.year,' '.join(strings(d.get('authors')) for d in sources.get(p.id,[])),' '.join(strings(d.get('topics')) for d in sources.get(p.id,[]))) for p in s.scalars(select(Paper).order_by(Paper.id))]
