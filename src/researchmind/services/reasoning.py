from researchmind.services.intelligence import Intelligence
from researchmind.reasoning.evidence import chunk_evidence,EvidenceIndex
from researchmind.services.library import Library

class Reasoning:
    def __init__(self,sessions): self.sessions=sessions
    def corpus(self,paper_ids):
        ids=list(dict.fromkeys(paper_ids))
        if len(ids)>100: raise ValueError('Select at most 100 papers.')
        service=Intelligence(self.sessions)
        originals=[e for pid in ids for e in service.evidence(pid)]
        chunks=chunk_evidence(originals)
        if len(chunks)>10000: raise ValueError('Evidence index exceeds 10,000 chunks; select fewer papers.')
        return originals,EvidenceIndex(chunks)
