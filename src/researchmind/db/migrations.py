"""Forward-only, additive SQLite migrations; preserves the Phase 2 schema."""
from sqlalchemy import text
from .models import Paper, Collection, Membership, Activity
from .science import SourceRecord, Document, Passage

REVISIONS = {1: [Paper, Collection, Membership, Activity], 2: [SourceRecord, Document, Passage]}

def upgrade(engine):
    with engine.connect() as connection:
        connection.exec_driver_sql('BEGIN IMMEDIATE')
        try:
            version = connection.exec_driver_sql('PRAGMA user_version').scalar_one()
            if version > max(REVISIONS):
                raise RuntimeError('Database was created by a newer ResearchMind version.')
            for revision, models in REVISIONS.items():
                if revision > version:
                    for model in models:
                        model.__table__.create(connection, checkfirst=True)
                    connection.exec_driver_sql(f'PRAGMA user_version={revision}')
            connection.commit()
        except BaseException:
            connection.rollback(); raise
