"""Metadata-only public API searches. No document text is sent externally."""
import os, time, json, re
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET
import httpx
from researchmind.schemas import PaperCreate

@dataclass(frozen=True)
class Record:
    provider: str
    external_id: str
    title: str
    year: int | None
    doi: str | None
    abstract: str
    authors: list[str]
    url: str
    pdf_url: str | None
    venue: str | None
    publication_type: str | None
    open_access: bool | None
    license: str | None
    citations: int | None
    references: list[str]
    topics: list[str]
    retrieved_at: str
    raw: dict
    @property
    def access(self): return 'abstract' if self.abstract else 'metadata_only'
    def paper(self): return PaperCreate(title=self.title,year=self.year,doi=self.doi,abstract=self.abstract)
    def normalized(self):
        data=asdict(self); data.pop('raw'); return data

def clean(value): return re.sub(r'<[^>]*>', '', str(value or '')).strip()
def doi(value):
    try: return PaperCreate(title='validation',doi=value).doi
    except ValueError: return None

def inverted(index):
    return ' '.join(word for _,word in sorted((pos,word) for word,positions in (index or {}).items() for pos in positions))

class LiteratureClient:
    def __init__(self, client=None, sleep=time.sleep):
        self.client=client or httpx.Client(timeout=20,follow_redirects=False,headers={'User-Agent':'ResearchMind/0.3 (academic metadata client)'})
        self.sleep=sleep; self.cache={}; self.last_request={}
    def close(self): self.client.close()
    def search(self, provider, query, page=1, size=10):
        query=query.strip()
        if not query or len(query)>500 or not 1<=page<=20 or not 1<=size<=25: raise ValueError('Enter a query of 1–500 characters, page 1–20, size 1–25.')
        key=(provider,query,page,size); now=time.monotonic()
        if key in self.cache and now-self.cache[key][0]<600: return self.cache[key][1]
        if provider=='OpenAlex':
            url='https://api.openalex.org/works'; params={'search':query,'page':page,'per-page':size}
            if os.getenv('OPENALEX_API_KEY'): params['api_key']=os.environ['OPENALEX_API_KEY']
        elif provider=='Crossref':
            url='https://api.crossref.org/works'; params={'query.bibliographic':query,'rows':size,'offset':(page-1)*size}
            if os.getenv('CROSSREF_MAILTO'): params['mailto']=os.environ['CROSSREF_MAILTO']
        elif provider=='arXiv':
            url='https://export.arxiv.org/api/query'; params={'search_query':'all:"'+query.replace('"',' ')+'"','start':(page-1)*size,'max_results':size}
        else: raise ValueError('Unknown literature provider.')
        for attempt in range(3):
            delay=(3 if provider=='arXiv' else 1)-(time.monotonic()-self.last_request.get(provider,-100))
            if delay>0: self.sleep(delay)
            self.last_request[provider]=time.monotonic()
            try: response=self.client.get(url,params=params)
            except httpx.RequestError:
                if attempt==2: raise ValueError(f'{provider} is unreachable. Try again later.') from None
                self.sleep(2**attempt); continue
            if response.status_code in (429,502,503,504) and attempt<2:
                wait=response.headers.get('Retry-After','')
                if wait.isdigit() and int(wait)>30: raise ValueError(f'{provider} requested a longer retry delay. Try later.')
                self.sleep(max(2**attempt,int(wait) if wait.isdigit() else 0)); continue
            if response.status_code!=200: raise ValueError(f'{provider} returned HTTP {response.status_code}. Check access or try later.')
            break
        stamp=datetime.now(timezone.utc).isoformat()
        try:
            if provider=='OpenAlex': records=[self.openalex(x,stamp) for x in response.json()['results']]
            elif provider=='Crossref': records=[self.crossref(x,stamp) for x in response.json()['message']['items']]
            else: records=self.arxiv(response.text,stamp)
        except (ValueError,KeyError,TypeError,ET.ParseError,AttributeError) as exc: raise ValueError(f'{provider} returned an unexpected response format.') from exc
        records=[r for r in records if r.title and r.external_id]
        if len(self.cache)>=128: self.cache.pop(next(iter(self.cache)))
        self.cache[key]=(now,records); return records
    @staticmethod
    def openalex(x,t):
        loc=x.get('best_oa_location') or {}; oa=x.get('open_access') or {}
        return Record('OpenAlex',x.get('id') or '',clean(x.get('title')),x.get('publication_year'),doi(x.get('doi')),inverted(x.get('abstract_inverted_index')),[(a.get('author') or {}).get('display_name','') for a in x.get('authorships',[])],(x.get('primary_location') or {}).get('landing_page_url') or x.get('id') or '',loc.get('pdf_url'),((x.get('primary_location') or {}).get('source') or {}).get('display_name'),x.get('type'),oa.get('is_oa'),loc.get('license'),x.get('cited_by_count'),x.get('referenced_works') or [],[v.get('display_name','') for v in x.get('topics',[])],t,x)
    @staticmethod
    def crossref(x,t):
        dates=(x.get('published') or x.get('issued') or {}).get('date-parts') or [[]]
        return Record('Crossref',x.get('DOI') or '',clean((x.get('title') or [''])[0]),dates[0][0] if dates[0] else None,doi(x.get('DOI')),clean(x.get('abstract')),[' '.join(filter(None,[a.get('given'),a.get('family')])) or a.get('name','') for a in x.get('author',[])],x.get('URL') or '',None,(x.get('container-title') or [None])[0],x.get('type'),None,None,x.get('is-referenced-by-count'),[r['DOI'] for r in x.get('reference',[]) if r.get('DOI')],x.get('subject') or [],t,x)
    @staticmethod
    def arxiv(xml,t):
        ns={'a':'http://www.w3.org/2005/Atom','r':'http://arxiv.org/schemas/atom'}; root=ET.fromstring(xml); records=[]
        for e in root.findall('a:entry',ns):
            get=lambda k:e.findtext(k,default='',namespaces=ns).strip()
            ident=get('a:id'); published=get('a:published'); pdf=next((l.get('href') for l in e.findall('a:link',ns) if l.get('type')=='application/pdf'),None)
            records.append(Record('arXiv',re.sub(r'v\d+$','',ident), ' '.join(get('a:title').split()),int(published[:4]) if published[:4].isdigit() else None,doi(get('r:doi')), ' '.join(get('a:summary').split()),[a.findtext('a:name',default='',namespaces=ns) for a in e.findall('a:author',ns)],ident,pdf,get('r:journal_ref') or None,'preprint',True,None,None,[],[c.get('term','') for c in e.findall('a:category',ns)],t,{'atom_xml':ET.tostring(e,encoding='unicode')}))
        return records
