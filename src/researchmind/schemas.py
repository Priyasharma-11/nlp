from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timezone

class CollectionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default='', max_length=2000)

class PaperCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=1000)
    year: int | None = Field(default=None, ge=1500, le=datetime.now(timezone.utc).year+1)
    doi: str | None = Field(default=None, max_length=500)
    abstract: str = Field(default='', max_length=100000)
    @field_validator('doi', mode='before')
    @classmethod
    def normalize_doi(cls, value):
        import re
        if not value: return None
        value = str(value).strip().lower().removeprefix('https://doi.org/').removeprefix('doi:').strip()
        if not re.fullmatch(r'10\.\d{4,9}/\S+', value):
            raise ValueError('Enter a valid DOI or leave it blank')
        return value
