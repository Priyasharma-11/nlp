"""Curated public bibliography. Summaries are editorial notes, not verbatim abstracts."""
import json
from datetime import datetime, timezone
from sqlalchemy import select
from researchmind.db.models import Paper, Collection, Membership, Activity
from researchmind.db.science import SourceRecord

PAPERS = [
 ("Attention Is All You Need", 2017, "10.48550/arxiv.1706.03762", "https://arxiv.org/abs/1706.03762", ["Ashish Vaswani","Noam Shazeer","Niki Parmar","Jakob Uszkoreit","Llion Jones","Aidan N. Gomez","Łukasz Kaiser","Illia Polosukhin"], ["Transformers","Attention"], "The Transformer architecture uses attention rather than recurrent or convolutional sequence processing. The study applies the architecture to machine translation."),
 ("BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",2019,"10.18653/v1/N19-1423","https://aclanthology.org/N19-1423/",["Jacob Devlin","Ming-Wei Chang","Kenton Lee","Kristina Toutanova"],["Transformers","Language models"],"BERT learns contextual representations from unlabeled text using bidirectional Transformer pretraining. The model is adapted to language understanding tasks through fine-tuning."),
 ("Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",2019,"10.18653/v1/D19-1410","https://aclanthology.org/D19-1410/",["Nils Reimers","Iryna Gurevych"],["Embeddings","Semantic retrieval"],"Sentence-BERT uses siamese and triplet architectures to produce sentence embeddings suitable for similarity search using cosine similarity."),
 ("SciBERT: A Pretrained Language Model for Scientific Text",2019,"10.18653/v1/D19-1371","https://aclanthology.org/D19-1371/",["Iz Beltagy","Kyle Lo","Arman Cohan"],["Scientific NLP","Language models"],"SciBERT adapts BERT pretraining to scientific literature to address the limited availability of labeled scientific language data."),
 ("SPECTER: Document-level Representation Learning using Citation-informed Transformers",2020,"10.18653/v1/2020.acl-main.207","https://aclanthology.org/2020.acl-main.207/",["Arman Cohan","Sergey Feldman","Iz Beltagy","Doug Downey","Daniel S. Weld"],["Embeddings","Scientific NLP","Semantic retrieval"],"SPECTER uses citation relationships during Transformer training to learn scientific document representations for tasks such as recommendation and classification."),
 ("Fact or Fiction: Verifying Scientific Claims",2020,"10.18653/v1/2020.emnlp-main.609","https://aclanthology.org/2020.emnlp-main.609/",["David Wadden","Shanchuan Lin","Kyle Lo","Lucy Lu Wang","Madeleine van Zuylen","Arman Cohan","Hannaneh Hajishirzi"],["Scientific NLP","Claim verification"],"SciFact is a benchmark for identifying scientific abstracts that support or refute claims and locating rationales for those decisions."),
]
COLLECTION = "Demo — NLP & scientific intelligence"
def load_demo(lib):
    """Atomic, repeatable load into the current session only."""
    with lib.sessions.begin() as s:
        col=s.scalar(select(Collection).where(Collection.name==COLLECTION))
        if col is None:
            col=Collection(name=COLLECTION,description="Six real publications with source links and editorial summaries; not original abstracts or uploaded PDFs.")
            s.add(col); s.flush()
        added=0
        for title,year,doi,url,authors,topics,note in PAPERS:
            p=s.scalar(select(Paper).where(Paper.doi==doi.lower()))
            if p is None:
                p=Paper(title=title,year=year,doi=doi.lower(),abstract="",access_level="manual_metadata")
                s.add(p); s.flush(); added+=1
            # Keep summaries in separate metadata, never pass them off as author evidence.
            src=s.scalar(select(SourceRecord).where(SourceRecord.provider=="Curated demo",SourceRecord.external_id==url))
            if src is None:
                meta=dict(title=title,year=year,doi=doi,url=url,authors=authors,topics=topics,editorial_summary=note,abstract="",references=[],citations=None,summary_type="Editorial paraphrase; not original abstract")
                s.add(SourceRecord(paper_id=p.id,provider="Curated demo",external_id=url,retrieved_at=datetime.now(timezone.utc).isoformat(),normalized=json.dumps(meta,ensure_ascii=False),raw=json.dumps({"source_url":url,"kind":"curated bibliography"})))
            if s.get(Membership,(col.id,p.id)) is None:
                s.add(Membership(collection_id=col.id,paper_id=p.id))
        if added: s.add(Activity(event="Loaded curated NLP demonstration papers"))
        return added
