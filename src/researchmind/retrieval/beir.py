"""Offline BEIR-format graded retrieval evaluation (not official pytrec_eval)."""
import csv
import math
from pathlib import Path
from researchmind.reasoning.benchmark import read_jsonl
from researchmind.retrieval.search import Index, Record


def run_beir(corpus, queries, qrels, method='BM25', k=10, model='General MiniLM'):
    if not corpus or not queries or not qrels or not 1 <= k <= 100:
        raise ValueError('Provide nonempty corpus, queries and judgments; K must be 1–100.')
    ids = {str(d['_id']): i for i, d in enumerate(corpus)}
    query_map = {str(q['_id']): q['text'] for q in queries}
    if len(ids) != len(corpus) or len(query_map) != len(queries):
        raise ValueError('Duplicate corpus or query IDs.')
    index = Index([Record(i, str(d.get('title') or ''), str(d.get('text') or '')) for i,d in enumerate(corpus)])
    details = []
    for qid, labels in qrels.items():
        if qid not in query_map or not set(labels) <= ids.keys() or any(v < 0 for v in labels.values()):
            raise ValueError('Invalid judgment identifiers or grades.')
        relevant = {ids[d]: grade for d,grade in labels.items() if grade > 0}
        if not relevant:
            continue
        hits = [r.id for r,_ in index.search(query_map[qid], method, model, k)]
        grades = [relevant.get(i,0) for i in hits]
        dcg = lambda values: sum(v/math.log2(i+2) for i,v in enumerate(values))
        ideal = dcg(sorted(relevant.values(),reverse=True)[:k])
        details.append({'query_id':qid,'precision':sum(v>0 for v in grades)/k,'recall':sum(v>0 for v in grades)/len(relevant),'mrr':next((1/(i+1) for i,v in enumerate(grades) if v>0),0.),'ndcg':dcg(grades)/ideal,'ranked_ids':[str(corpus[i]['_id']) for i in hits]})
    if not details:
        raise ValueError('No positively judged queries.')
    return {'method':method,'model':model if method in ('Semantic','Hybrid') else None,'k':k,'documents':len(corpus),'queries_evaluated':len(details),'metrics':{m:sum(d[m] for d in details)/len(details) for m in ('precision','recall','mrr','ndcg')},'details':details,'protocol':'Graded linear-gain nDCG; positive relevance for other metrics; no-positive queries excluded. Not official BEIR scoring.'}


def load_beir(folder, split='test'):
    if split not in ('train','dev','test'):
        raise ValueError('Invalid split.')
    folder = Path(folder)
    qrels = {}
    with (folder/'qrels'/f'{split}.tsv').open(encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            qid, docid, grade = row['query-id'],row['corpus-id'],int(row['score'])
            if docid in qrels.setdefault(qid,{}):
                raise ValueError('Duplicate judgment.')
            qrels[qid][docid] = grade
    return read_jsonl(folder/'corpus.jsonl'),read_jsonl(folder/'queries.jsonl'),qrels
