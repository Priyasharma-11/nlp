import argparse,json
from pathlib import Path
from researchmind.reasoning.benchmark import read_jsonl,run_scifact
from researchmind.reasoning.assistant import local_stance

def main():
    p=argparse.ArgumentParser(); p.add_argument('corpus'); p.add_argument('claims'); p.add_argument('--method',choices=['BM25','TF-IDF','Semantic','Hybrid'],default='BM25'); p.add_argument('--k',type=int,default=5); p.add_argument('--nli'); p.add_argument('--output',default='scifact-results.json'); a=p.parse_args()
    classifier=(lambda text,claim:local_stance(text,claim,a.nli)) if a.nli else None
    result=run_scifact(read_jsonl(a.corpus),read_jsonl(a.claims),a.method,a.k,classifier); Path(a.output).write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps({k:v for k,v in result.items() if k!='details'},indent=2))
if __name__=='__main__': main()
