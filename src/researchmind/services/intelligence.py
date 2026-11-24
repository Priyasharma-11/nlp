"""Read-only evidence views over the existing persistent scientific corpus."""
import json
from sqlalchemy import select
from researchmind.db.models import Paper
from researchmind.db.science import Document, Passage, SourceRecord
from researchmind.documents.intelligence import Evidence, analyze, summarize

class Intelligence:
    def __init__(self,sessions): self.sessions=sessions
    def evidence(self,paper_id,document_id=None):
        with self.sessions() as s:
            p=s.get(Paper,paper_id)
            if p is None: raise ValueError('Paper not found.')
            docs=list(s.scalars(select(Document.id).where(Document.paper_id==paper_id).order_by(Document.id)))
            if document_id is not None and document_id not in docs: raise ValueError('Document does not belong to selected paper.')
            # A single version per analysis avoids mixing experimental results across versions.
            chosen=document_id if document_id is not None else (docs[-1] if docs else None)
            passages=list(s.scalars(select(Passage).where(Passage.document_id==chosen).order_by(Passage.page,Passage.ordinal))) if chosen is not None else []
            out=[Evidence(paper_id,b.text,b.section,'local PDF',chosen,b.id,b.page) for b in passages]
            if not any(e.section=='Abstract' for e in out):
                sources=list(s.scalars(select(SourceRecord).where(SourceRecord.paper_id==paper_id).order_by(SourceRecord.id)))
                for source in sources:
                    abstract=json.loads(source.normalized).get('abstract')
                    if abstract:
                        out.append(Evidence(paper_id,abstract,'Abstract',source.provider,source_id=source.id)); break
                else:
                    if p.abstract: out.append(Evidence(paper_id,p.abstract,'Abstract','manual metadata'))
            return out
    def compare(self,paper_ids,limit=2):
        if not 2<=len(set(paper_ids))<=10: raise ValueError('Select 2–10 distinct papers.')
        with self.sessions() as s:
            papers=[s.get(Paper,i) for i in dict.fromkeys(paper_ids)]
            if any(p is None for p in papers): raise ValueError('Paper not found.')
        return [{'id':p.id,'title':p.title,'year':p.year,'doi':p.doi,'fields':analyze(self.evidence(p.id),limit)} for p in papers]
