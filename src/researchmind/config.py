from pathlib import Path
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    data_dir: Path

    @classmethod
    def from_env(cls):
        return cls(Path(os.environ.get('RESEARCHMIND_DATA_DIR', 'data')).expanduser().resolve())

    @property
    def database(self):
        return self.data_dir / 'researchmind.sqlite3'
