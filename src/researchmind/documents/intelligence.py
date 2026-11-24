"""Conservative extractive analysis. All text is copied from stored evidence."""
import re
from dataclasses import dataclass, asdict
from collections import Counter
from researchmind.nlp.pipeline import lexical_tokens
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

@dataclass(frozen=True)
class Evidence:
    paper_id: int
    text: str
    section: str
    origin: str
    document_id: int | None = None
    passage_id: int | None = None
    page: int | None = None
    source_id: int | None = None
    def reference(self):
        if self.document_id is not None:
            return f'Document {self.document_id}, page {self.page}, {self.section}, passage {self.passage_id}'
        return f'Provider record {self.source_id}, abstract' if self.source_id else 'User-entered abstract (unverified)'

FIELDS = {
 'Research problem': ({'Introduction','Background','Abstract'}, r'\b(problem|challenge|gap|lack|difficulty)\b'),
 'Objectives': ({'Abstract','Introduction'}, r'\b(aim|aims|objective|objectives|we propose|we investigate|we study)\b'),
 'Research questions': ({'Introduction','Abstract'}, r'\b(research question|we ask|whether)\b|\?'),
 'Background': ({'Background','Related work','Introduction'}, None),
 'Methodology': ({'Methodology','Experiments'}, None),
 'Algorithms and techniques': ({'Methodology','Experiments','Abstract'}, r'\b(algorithm|model|architecture|classifier|network|method|framework)s?\b'),
 'Datasets': ({'Methodology','Experiments','Results','Abstract'}, r'\b(data ?sets?|corpus|benchmark|cohort|training data)\b'),
 'Experimental setup': ({'Experiments','Methodology'}, r'\b(train|training|test|evaluation|experiment|baseline|parameter|split)\w*\b'),
 'Evaluation metrics': ({'Experiments','Results','Methodology'}, r'\b(accuracy|precision|recall|f1|auc|rouge|bleu|ndcg|mrr|error rate|rmse|mae)\b'),
 'Results': ({'Results','Results and discussion'}, None),
 'Contributions': ({'Abstract','Introduction','Conclusion'}, r'\b(contribut\w*|we introduce|we propose|we present)\b'),
 'Limitations': ({'Limitations'}, None),
 'Future work': ({'Future work'}, None),
}
EXTRA = {'Limitations': ({'Discussion','Conclusion','Results and discussion','Abstract'},r'\b(limitation\w*|limited by|cannot generalize|should be interpreted with caution)\b'), 'Future work': ({'Discussion','Conclusion','Abstract'},r'\b(future work|future research|further studies|future studies)\b')}

def sentences(evidence):
    for e in evidence:
        if e.section == 'References': continue
        # Exact slices, with simple boundary detection; do not paraphrase.
        for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', e.text):
            sentence=sentence.strip()
            if sentence: yield Evidence(**{**asdict(e),'text':sentence})

def rank(items, limit=3):
    if not items: return []
    vocab=Counter(t for e in items for t in set(lexical_tokens(e.text)) if t not in ENGLISH_STOP_WORDS)
    scored=[]; seen=set()
    for i,e in enumerate(items):
        key=' '.join(e.text.split()).casefold()
        if key in seen: continue
        seen.add(key); terms=[t for t in lexical_tokens(e.text) if t not in ENGLISH_STOP_WORDS]
        score=sum(vocab[t] for t in set(terms))/max(1,len(set(terms)))
        scored.append((score,i,e))
    return [e for _,_,e in sorted(sorted(scored,key=lambda x:(-x[0],x[1]))[:limit],key=lambda x:x[1])]

def analyze(evidence, limit=3):
    items=list(sentences(evidence)); result={}
    for field,(sections,pattern) in FIELDS.items():
        matches=[e for e in items if e.section in sections and (pattern is None or re.search(pattern,e.text,re.I))]
        if field in EXTRA:
            sections2,pattern2=EXTRA[field]; matches.extend(e for e in items if e.section in sections2 and re.search(pattern2,e.text,re.I))
        result[field]=rank(matches,limit)
    return result

def summarize(evidence, mode='Full text', section=None, limit=5):
    if mode=='Abstract': evidence=[e for e in evidence if e.section=='Abstract']
    elif mode=='Section': evidence=[e for e in evidence if e.section==section]
    elif mode=='Technical': evidence=[e for e in evidence if e.section in {'Methodology','Experiments','Results','Results and discussion'}]
    elif mode!='Full text': raise ValueError('Unknown summary mode.')
    return rank(list(sentences(evidence)),limit)
