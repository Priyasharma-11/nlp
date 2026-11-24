"""Local passage retrieval. Evidence is immutable and references the original passage."""
from dataclasses import dataclass, replace
import re
from functools import lru_cache
from researchmind.retrieval.search import Index, Record
from researchmind.retrieval.embeddings import encode
from researchmind.documents.intelligence import Evidence
from researchmind.nlp.pipeline import lexical_tokens
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

@dataclass(frozen=True)
class Chunk:
    id: int
    evidence: Evidence
    start: int
    end: int

def chunk_evidence(items, size=120, overlap=20):
    if not 0 <= overlap < size: raise ValueError('Invalid chunk size or overlap.')
    out=[]
    for e in items:
        if e.section.casefold()=='references': continue
        words=list(re.finditer(r'\S+',e.text))
        for i in range(0,len(words),size-overlap):
            a=words[i].start(); b=words[min(i+size,len(words))-1].end()
            out.append(Chunk(len(out)+1,replace(e,text=e.text[a:b]),a,b))
            if i+size>=len(words): break
    return out

@lru_cache(maxsize=4)
def cached_vectors(texts, model, role):
    return encode(list(texts),model,role)

def cached_encoder(texts,model,role):
    return cached_vectors(tuple(texts),model,role)

class EvidenceIndex:
    def __init__(self, chunks, encoder=cached_encoder):
        self.chunks={c.id:c for c in chunks}
        self.index=Index([Record(c.id,'',c.evidence.text) for c in chunks],encoder)
    def search(self,query,method='BM25',k=5,weight=.5):
        if method not in {'BM25','TF-IDF','Semantic','Hybrid'}: raise ValueError('Invalid evidence retrieval method.')
        filtered=' '.join(t for t in lexical_tokens(query) if t not in ENGLISH_STOP_WORDS or t in {'no','not','never','nor'})
        if not filtered: return []
        if method in {'BM25','TF-IDF'}: query=filtered
        return [(self.chunks[r.id],score) for r,score in self.index.search(query,method,'General MiniLM',k,weight)]

def validate_chunk(chunk, originals):
    e=chunk.evidence
    return any((o.paper_id,o.document_id,o.passage_id,o.source_id,o.page,o.section,o.origin)==(e.paper_id,e.document_id,e.passage_id,e.source_id,e.page,e.section,e.origin) and 0<=chunk.start<chunk.end<=len(o.text) and o.text[chunk.start:chunk.end]==e.text for o in originals)
