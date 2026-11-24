from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from .migrations import upgrade

def initialize(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(URL.create('sqlite', database=str(path)), connect_args={'timeout': 10})
    @event.listens_for(engine, 'connect')
    def configure(connection, _):
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.close()
    upgrade(engine)
    return sessionmaker(engine, expire_on_commit=False)
