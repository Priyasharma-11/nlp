import hashlib,json
from datetime import datetime,timezone
from pathlib import PurePath
from sqlalchemy import select
from researchmind.db.models import Paper, Activity
from researchmind.db.science import SourceRecord, Document, Passage
from researchmind.documents.parser import parse_pdf

class Science:
    def __init__(self,sessions): self.sessions=sessions
    def save_record(self,record):
        data=record.paper()
        with self.sessions.begin() as s:
            existing=s.scalar(select(SourceRecord).where(SourceRecord.provider==record.provider,SourceRecord.external_id==record.external_id))
            if existing:
                existing.raw=json.dumps(record.raw,ensure_ascii=False); existing.normalized=json.dumps(record.normalized(),ensure_ascii=False); existing.retrieved_at=record.retrieved_at
                return existing.paper_id
            paper=s.scalar(select(Paper).where(Paper.doi==data.doi)) if data.doi else None
            if paper is None:
                paper=Paper(**data.model_dump(),access_level=record.access); s.add(paper); s.flush()
            elif not paper.abstract and data.abstract:
                paper.abstract=data.abstract
                if paper.access_level!='uploaded_pdf': paper.access_level='abstract'
            s.add(SourceRecord(paper_id=paper.id,provider=record.provider,external_id=record.external_id,retrieved_at=record.retrieved_at,raw=json.dumps(record.raw,ensure_ascii=False),normalized=json.dumps(record.normalized(),ensure_ascii=False)))
            s.add(Activity(event='Scientific metadata saved')); return paper.id
    def upload(self,paper_id,filename,data):
        if not data or len(data)>20*1024*1024 or not data.startswith(b'%PDF-'): raise ValueError('Upload a valid PDF, maximum 20 MiB.')
        if self.sessions.kw.get('info',{}).get('cloud'):
            from researchmind.cloud import MAX_UPLOAD
            if len(data)>MAX_UPLOAD: raise ValueError('Cloud PDF limit is 5 MiB per file.')
        digest=hashlib.sha256(data).hexdigest()
        with self.sessions() as s:
            existing=s.scalar(select(Document).where(Document.sha256==digest))
            if existing:
                if existing.paper_id!=paper_id: raise ValueError('This PDF is already attached to another paper.')
                return existing.id
        meta,blocks,empty,count=parse_pdf(data)
        with self.sessions.begin() as s:
            paper=s.get(Paper,paper_id)
            if not paper: raise ValueError('Paper not found.')
            document=Document(paper_id=paper_id,sha256=digest,filename=PurePath(filename.replace('\\','/')).name[:255],uploaded_at=datetime.now(timezone.utc).isoformat(),original=data,metadata_json=json.dumps({'pdf_metadata':meta,'empty_pages':empty,'page_count':count,'extraction':'local text blocks; section labels heuristic'})); s.add(document); s.flush()
            s.add_all([Passage(document_id=document.id,page=b.page,ordinal=b.ordinal,section=b.section,text=b.text,bbox_json=json.dumps(b.bbox)) for b in blocks]); paper.access_level='uploaded_pdf'; s.add(Activity(event='PDF uploaded locally')); return document.id
    def documents(self,paper_id):
        with self.sessions() as s: return list(s.scalars(select(Document).where(Document.paper_id==paper_id)))
    def passages(self,document_id):
        with self.sessions() as s: return list(s.scalars(select(Passage).where(Passage.document_id==document_id).order_by(Passage.page,Passage.ordinal)))
    def sources(self,paper_id):
        with self.sessions() as s: return list(s.scalars(select(SourceRecord).where(SourceRecord.paper_id==paper_id)))
