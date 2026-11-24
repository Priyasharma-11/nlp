"""Explicit local inference. Downloads only via separately requested setup."""
from functools import lru_cache
import numpy as np
MODELS={'General MiniLM':'sentence-transformers/all-MiniLM-L6-v2','SciBERT (mean pooling, experimental)':'allenai/scibert_scivocab_uncased','SPECTER2 retrieval':'allenai/specter2_base'}
@lru_cache(maxsize=2)
def load(name):
    if name not in MODELS: raise ValueError('Unknown embedding model.')
    if name=='General MiniLM':
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(MODELS[name],device='cpu',local_files_only=True,trust_remote_code=False,model_kwargs={'use_safetensors':True})
    from transformers import AutoTokenizer, AutoModel
    tokenizer=AutoTokenizer.from_pretrained(MODELS[name],local_files_only=True)
    if name.startswith('SPECTER2'):
        from adapters import AutoAdapterModel
        model=AutoAdapterModel.from_pretrained(MODELS[name],local_files_only=True,trust_remote_code=False,use_safetensors=True)
        # AdapterHub expects downloaded adapter directories, not a base-only embedding.
        import os
        for role,var in [('query','RESEARCHMIND_SPECTER_QUERY'),('paper','RESEARCHMIND_SPECTER_PAPER')]:
            path=os.environ.get(var)
            if not path or not os.path.isdir(path): raise ValueError(f'SPECTER2 requires local adapter directory: {var}')
            model.load_adapter(path,load_as=role)
    else: model=AutoModel.from_pretrained(MODELS[name],local_files_only=True,trust_remote_code=False,use_safetensors=True)
    return tokenizer,model.eval()

def encode(texts,name,role='paper'):
    if not texts: raise ValueError('No text to embed.')
    try:
        obj=load(name)
        if name=='General MiniLM': return np.asarray(obj.encode(texts,batch_size=8,normalize_embeddings=True,show_progress_bar=False))
        import torch
        tokenizer,model=obj
        if name.startswith('SPECTER2'): model.set_active_adapters(role)
        result=[]
        with torch.inference_mode():
            for i in range(0,len(texts),8):
                inp=tokenizer(texts[i:i+8],padding=True,truncation=True,max_length=512,return_tensors='pt')
                h=model(**inp).last_hidden_state
                v=h[:,0] if name.startswith('SPECTER2') else (h*inp['attention_mask'].unsqueeze(-1)).sum(1)/inp['attention_mask'].sum(1,keepdim=True).clamp(min=1)
                result.append(torch.nn.functional.normalize(v,dim=1).cpu().numpy())
        return np.concatenate(result)
    except (ImportError,OSError,RuntimeError) as exc: raise ValueError(f'Local model unavailable or incompatible: {name}. See model setup in README. ({type(exc).__name__})') from exc
