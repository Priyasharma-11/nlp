"""Offline SciFact-format evaluation. No downloads or synthetic scientific scores."""
import json
from pathlib import Path
from researchmind.documents.intelligence import Evidence
from researchmind.reasoning.evidence import chunk_evidence, EvidenceIndex
from researchmind.reasoning.assistant import answer, verify
from researchmind.reasoning.evaluation import citation_metrics, claim_metrics
from researchmind.retrieval.evaluation import metrics

def read_jsonl(path):
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def run_scifact(corpus, claims, method='BM25', k=5, classifier=None):
    if not corpus or not claims or not 1<=k<=50: raise ValueError('Nonempty corpus and claims; K must be 1–50.')
    docs={int(d['doc_id']):d for d in corpus}
    if len(docs)!=len(corpus): raise ValueError('Duplicate document IDs.')
    originals=[Evidence(pid,s,'Abstract','SciFact benchmark',source_id=i+1) for pid,d in docs.items() for i,s in enumerate(d['abstract']) if s.strip()]
    chunks=chunk_evidence(originals); idx=EvidenceIndex(chunks)
    scores=[]; expected=[]; predicted=[]; citations=[]; detail=[]
    for row in claims:
        if 'evidence' not in row: raise ValueError('Use labeled development claims, not unlabeled test claims.')
        gold=row['evidence']; rel=set(map(int,gold)); labels={e['label'] for entries in gold.values() for e in entries}
        if not rel<=docs.keys() or not labels<={'SUPPORT','CONTRADICT'}: raise ValueError('Invalid or missing benchmark evidence.')
        hits=idx.search(row['claim'],method,k); ranked=list(dict.fromkeys(c.evidence.paper_id for c,_ in hits))
        if rel: scores.append(metrics(ranked,rel,k))
        target='Mixed evidence' if len(labels)==2 else 'Supported' if 'SUPPORT' in labels else 'Contradicted' if 'CONTRADICT' in labels else 'Insufficient evidence'
        result=verify(row['claim'],hits,originals,classifier); expected.append(target); predicted.append(result['status'])
        response=answer(row['claim'],hits,originals); cm=citation_metrics(response['items'],{c.id for c,_ in hits}); citations.append(cm)
        detail.append({'claim_id':row.get('id'),'expected':target,'predicted':result['status'],'retrieved_doc_ids':ranked})
    avg=lambda rows,key: sum(v[key] for v in rows if v[key] is not None)/sum(v[key] is not None for v in rows) if any(v[key] is not None for v in rows) else None
    return {'documents':len(docs),'claims':len(claims),'retrieval_labeled_claims':len(scores),'method':method,'k_passages':k,'retrieval_document_metrics':{key:avg(scores,key) for key in ['precision','recall','mrr','ndcg']},'claim_metrics':claim_metrics(expected,predicted),'citation_id_validity':avg(citations,'citation_id_validity'),'citation_coverage':avg(citations,'citation_coverage'),'human_faithfulness':None,'details':detail,'limitations':'Document retrieval measured at passage cutoff; exact-match baseline unless a classifier is supplied. Citation validity is not factual entailment.'}
