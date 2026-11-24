import argparse, json
from pathlib import Path
from researchmind.retrieval.beir import load_beir, run_beir

def main():
    p=argparse.ArgumentParser(description='Offline BEIR-format retrieval evaluation')
    p.add_argument('folder'); p.add_argument('--split',choices=['train','dev','test'],default='test'); p.add_argument('--method',choices=['Keyword','BM25','TF-IDF','Semantic','Hybrid'],default='BM25'); p.add_argument('--k',type=int,default=10); p.add_argument('--output',default='beir-results.json'); a=p.parse_args()
    result=run_beir(*load_beir(a.folder,a.split),method=a.method,k=a.k)
    result['split']=a.split
    Path(a.output).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='details'},indent=2))
if __name__=='__main__': main()
