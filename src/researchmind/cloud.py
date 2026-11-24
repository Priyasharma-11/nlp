"""Ephemeral, per-browser-session demo storage. No global user data cache."""
from sqlalchemy import create_engine, event, select, func
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from researchmind.db.migrations import upgrade
from researchmind.db.models import Paper, Collection, Activity
from researchmind.db.science import Document, SourceRecord, Passage
from researchmind.services.library import Library

MAX_UPLOAD = 5 * 1024 * 1024
MAX_DOCUMENT_BYTES = 15 * 1024 * 1024
LIMITS = {Paper: 30, Collection: 10, Document: 4, SourceRecord: 60, Passage: 5000, Activity: 500}

class CloudWorkspace:
    def __init__(self):
        self.engine = create_engine('sqlite://', poolclass=StaticPool,
                                    connect_args={'check_same_thread': False})
        @event.listens_for(self.engine, 'connect')
        def configure(conn, _):
            conn.execute('PRAGMA foreign_keys=ON')
            conn.execute('PRAGMA max_page_count=12288')
        upgrade(self.engine)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False, info={'cloud': True})
        @event.listens_for(self.sessions, 'before_flush')
        def limits(session, *_):
            for model, limit in LIMITS.items():
                new = [o for o in session.new if isinstance(o, model)]
                if new and session.scalar(select(func.count()).select_from(model)) + len(new) > limit:
                    raise ValueError(f'Demo workspace limit reached: {limit} {model.__tablename__}. Reset workspace or remove records.')
            docs = [o for o in session.new if isinstance(o, Document)]
            if docs:
                if any(len(d.original)>MAX_UPLOAD for d in docs):
                    raise ValueError('Cloud PDF limit is 5 MiB per file.')
                used = session.scalar(select(func.coalesce(func.sum(func.length(Document.original)),0)))
                if used + sum(len(d.original) for d in docs)>MAX_DOCUMENT_BYTES:
                    raise ValueError('Cloud workspace PDF storage limit is 15 MiB.')
        self.library = Library(self.sessions)
        self.library.cloud = True
    def close(self):
        self.engine.dispose()


def workspace(state):
    if '_rm_cloud_workspace' not in state:
        state['_rm_cloud_workspace'] = CloudWorkspace()
    return state['_rm_cloud_workspace'].library


def reset_workspace(state):
    old = state.get('_rm_cloud_workspace')
    if old is not None:
        old.close()
    # Clear all widget values, search results, uploaded file references and consent.
    for key in list(state.keys()):
        del state[key]
