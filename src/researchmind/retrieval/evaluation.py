import math
import numpy as np

def metrics(ranked,relevant,k=10):
    if k<1 or not relevant: raise ValueError('Positive k and nonempty relevance labels required.')
    hits=[int(p in relevant) for p in list(dict.fromkeys(ranked))[:k]]
    dcg=sum(h/math.log2(i+2) for i,h in enumerate(hits)); ideal=sum(1/math.log2(i+2) for i in range(min(k,len(relevant))))
    return {'precision':sum(hits)/k,'recall':sum(hits)/len(relevant),'mrr':next((1/(i+1) for i,h in enumerate(hits) if h),0.),'ndcg':dcg/ideal}

def evaluate(index,judgments,methods,k,model):
    if not judgments: raise ValueError('Supply judged queries.')
    ids={r.id for r in index.records}; output=[]
    for method in methods:
        rows=[]
        for item in judgments:
            q=item['query']; rel=set(item['relevant_ids'])
            if not q.strip() or not rel or not rel<=ids: raise ValueError('Query and existing relevant paper IDs required.')
            rows.append(metrics([r.id for r,s in index.search(q,method,model,k)],rel,k))
        output.append({'method':method,'queries':len(rows),'k':k,**{key:float(np.mean([r[key] for r in rows])) for key in rows[0]}})
    return output
