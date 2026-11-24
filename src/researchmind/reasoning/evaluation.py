"""Metrics computed against human-provided judgments, not fabricated scores."""
from researchmind.retrieval.evaluation import metrics
from sklearn.metrics import classification_report

def citation_metrics(items,allowed_ids,judged_supported=None):
    ids=[i for row in items for i in row.get('citations',[])]
    valid=sum(type(i) is int and i in allowed_ids for i in ids)
    result={'citation_id_validity':valid/len(ids) if ids else None,'citation_coverage':sum(bool(row.get('citations')) for row in items)/len(items) if items else None,'human_faithfulness':None,'unsupported_claim_rate':None}
    if judged_supported is not None:
        if len(judged_supported)!=len(items) or any(type(x) is not bool for x in judged_supported): raise ValueError('Provide one human support judgment per answer item.')
        if items: result.update(human_faithfulness=sum(judged_supported)/len(items),unsupported_claim_rate=1-sum(judged_supported)/len(items))
    return result

def claim_metrics(expected,predicted):
    labels=['Supported','Contradicted','Insufficient evidence','Mixed evidence']
    if not expected or len(expected)!=len(predicted) or not set(expected+predicted)<=set(labels): raise ValueError('Supply paired valid claim labels.')
    return classification_report(expected,predicted,labels=labels,output_dict=True,zero_division=0)

def passage_metrics(hits,relevant,k=5): return metrics([c.id for c,_ in hits],set(relevant),k)
