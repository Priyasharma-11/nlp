from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from researchmind.db.models import Paper, Collection, Membership, Activity
from researchmind.schemas import PaperCreate, CollectionCreate

class Library:
    def __init__(self, sessions): self.sessions = sessions
    def _create(self, model, values, event):
        try:
            with self.sessions.begin() as s:
                obj = model(**values); s.add(obj); s.add(Activity(event=event)); s.flush()
                return obj.id
        except IntegrityError as exc:
            raise ValueError('Record already exists or violates a database constraint.') from exc
    def add_paper(self, data: PaperCreate):
        return self._create(Paper, data.model_dump(), 'Paper metadata saved')
    def add_collection(self, data: CollectionCreate):
        return self._create(Collection, data.model_dump(), 'Collection created')
    def papers(self, query=''):
        with self.sessions() as s:
            stmt=select(Paper).order_by(Paper.id.desc())
            if query.strip(): stmt=stmt.where(Paper.title.icontains(query.strip(), autoescape=True))
            return list(s.scalars(stmt))
    def collections(self):
        with self.sessions() as s: return list(s.scalars(select(Collection).order_by(Collection.name)))
    def assign(self, collection_id, paper_id):
        with self.sessions.begin() as s:
            if not s.get(Collection, collection_id) or not s.get(Paper, paper_id): raise ValueError('Paper or collection not found.')
            if s.get(Membership, (collection_id,paper_id)): return False
            s.add(Membership(collection_id=collection_id,paper_id=paper_id)); s.add(Activity(event='Paper added to collection')); return True
    def members(self, collection_id):
        with self.sessions() as s: return list(s.scalars(select(Paper).join(Membership).where(Membership.collection_id==collection_id)))
    def delete_paper(self, paper_id):
        with self.sessions.begin() as s:
            obj=s.get(Paper,paper_id)
            if not obj: return False
            s.delete(obj); s.add(Activity(event='Paper metadata deleted')); return True
    def overview(self):
        with self.sessions() as s:
            return {'papers':s.scalar(select(func.count()).select_from(Paper)), 'collections':s.scalar(select(func.count()).select_from(Collection)), 'memberships':s.scalar(select(func.count()).select_from(Membership)), 'activity':list(s.scalars(select(Activity).order_by(Activity.id.desc()).limit(10)))}
