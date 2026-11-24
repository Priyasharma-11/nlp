"""Local layout-aware extraction. No OCR or table interpretation is implied."""
import re, unicodedata
from dataclasses import dataclass
import pymupdf

HEADINGS={'abstract':'Abstract','introduction':'Introduction','background':'Background','related work':'Related work','methods':'Methodology','materials and methods':'Methodology','methodology':'Methodology','experimental setup':'Methodology','experiments':'Experiments','results':'Results','discussion':'Discussion','results and discussion':'Results and discussion','conclusion':'Conclusion','conclusions':'Conclusion','limitations':'Limitations','future work':'Future work','references':'References','bibliography':'References'}
@dataclass
class Block:
    page:int
    ordinal:int
    section:str
    text:str
    bbox:tuple

def heading(line):
    line=re.sub(r'^\s*\d+(?:\.\d+)*[.)]?\s+', '',line).strip().rstrip(':').casefold()
    return HEADINGS.get(line)

def parse_pdf(data):
    if not data or len(data)>20*1024*1024 or not data.startswith(b'%PDF-'): raise ValueError('Upload a valid PDF, maximum 20 MiB.')
    try: doc=pymupdf.open(stream=data,filetype='pdf')
    except (RuntimeError,ValueError) as exc: raise ValueError('PDF could not be opened.') from exc
    with doc:
        if doc.needs_pass: raise ValueError('Encrypted PDFs are not supported.')
        if not 1<=len(doc)<=300: raise ValueError('PDF must contain 1–300 pages.')
        meta=dict(doc.metadata or {}); blocks=[]; empty=[]; section='Unclassified'; total=0
        for page in doc:
            raw=[b for b in page.get_text('blocks',sort=True) if b[6]==0 and b[4].strip()]
            mid=page.rect.width/2
            left=[b for b in raw if b[2]<=mid+10]; right=[b for b in raw if b[0]>=mid-10]
            if len(left)>=3 and len(right)>=3:
                # Full-width blocks delimit column regions; retain original bounding boxes.
                spanning=[b for b in raw if b not in left and b not in right]; ordered=[]; remaining=[b for b in raw if b not in spanning]
                for wide in sorted(spanning,key=lambda b:b[1]):
                    band=[b for b in remaining if b[1]<wide[1]]
                    ordered.extend(sorted(band,key=lambda b:(b[0]>=mid-10,b[1]))); ordered.append(wide)
                    remaining=[b for b in remaining if b not in band]
                raw=ordered+sorted(remaining,key=lambda b:(b[0]>=mid-10,b[1]))
            if not raw: empty.append(page.number+1)
            ordinal=0
            for b in raw:
                text=unicodedata.normalize('NFC',b[4]).strip(); total+=len(text)
                if total>2_000_000: raise ValueError('Extracted text exceeds the safety limit.')
                current=[]
                for line in text.splitlines():
                    h=heading(line)
                    if h:
                        if current: blocks.append(Block(page.number+1,ordinal,section,'\n'.join(current),tuple(b[:4]))); ordinal+=1; current=[]
                        section=h
                    elif line.strip(): current.append(line.strip())
                if current: blocks.append(Block(page.number+1,ordinal,section,'\n'.join(current),tuple(b[:4]))); ordinal+=1
        return meta,blocks,empty,len(doc)
