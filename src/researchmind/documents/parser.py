"""Local PDF extraction with optional OCR for image-only pages."""
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
    extraction:str='native text'

def heading(line):
    line=re.sub(r'^\\s*\\d+(?:\\.\\d+)*[.)]?\\s+', '',line).strip().rstrip(':').casefold()
    return HEADINGS.get(line)

def _ocr_blocks(page, language='eng', dpi=200):
    """OCR one page and return grouped text lines with page-coordinate boxes."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise ValueError('OCR needs the optional dependencies. Install ResearchMind with the [ocr] extra.') from exc
    pix=page.get_pixmap(matrix=pymupdf.Matrix(dpi/72,dpi/72),alpha=False)
    image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    try:
        data=pytesseract.image_to_data(image,lang=language,output_type=pytesseract.Output.DICT)
    except pytesseract.TesseractNotFoundError as exc:
        raise ValueError('Tesseract OCR executable was not found. Install Tesseract and add it to PATH, then restart the terminal.') from exc
    except Exception as exc:
        raise ValueError(f'OCR failed for page {page.number+1}: {type(exc).__name__}: {exc}') from exc
    grouped={}
    count=len(data.get('text',[]))
    scale=72/dpi
    for i in range(count):
        word=str(data['text'][i]).strip()
        try: confidence=float(data['conf'][i])
        except (ValueError,TypeError,KeyError): confidence=-1
        if not word or confidence<0: continue
        key=(data['block_num'][i],data['par_num'][i],data['line_num'][i])
        x=int(data['left'][i]); y=int(data['top'][i]); w=int(data['width'][i]); h=int(data['height'][i])
        item=grouped.setdefault(key,{'words':[],'box':[x,y,x+w,y+h]})
        item['words'].append(word)
        item['box']=[min(item['box'][0],x),min(item['box'][1],y),max(item['box'][2],x+w),max(item['box'][3],y+h)]
    result=[]
    for item in grouped.values():
        text=' '.join(item['words']).strip()
        if text:
            x0,y0,x1,y1=item['box']; result.append((y0,x0,text,(x0*scale,y0*scale,x1*scale,y1*scale)))
    return sorted(result,key=lambda x:(x[0],x[1]))

def parse_pdf(data, ocr=False, ocr_language='eng', ocr_dpi=200):
    if not data or len(data)>20*1024*1024 or not data.startswith(b'%PDF-'): raise ValueError('Upload a valid PDF, maximum 20 MiB.')
    if not isinstance(ocr_dpi,int) or not 120<=ocr_dpi<=300: raise ValueError('OCR resolution must be between 120 and 300 DPI.')
    if not re.fullmatch(r'[A-Za-z0-9_+.-]{2,32}',ocr_language or ''): raise ValueError('Enter a valid Tesseract language code.')
    try: doc=pymupdf.open(stream=data,filetype='pdf')
    except (RuntimeError,ValueError) as exc: raise ValueError('PDF could not be opened.') from exc
    with doc:
        if doc.needs_pass: raise ValueError('Encrypted PDFs are not supported.')
        if not 1<=len(doc)<=300: raise ValueError('PDF must contain 1–300 pages.')
        meta=dict(doc.metadata or {}); blocks=[]; empty=[]; ocr_pages=[]; section='Unclassified'; total=0
        for page in doc:
            raw=[b for b in page.get_text('blocks',sort=True) if b[6]==0 and b[4].strip()]
            if not raw and ocr:
                ocr_raw=_ocr_blocks(page,ocr_language,ocr_dpi)
                raw=[(x0,y0,x1,y1,text,0,0) for y,x,text,(x0,y0,x1,y1) in ocr_raw]
                if raw: ocr_pages.append(page.number+1)
            mid=page.rect.width/2
            left=[b for b in raw if b[2]<=mid+10]; right=[b for b in raw if b[0]>=mid-10]
            if len(left)>=3 and len(right)>=3:
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
                        if current: blocks.append(Block(page.number+1,ordinal,section,'\\n'.join(current),tuple(b[:4]),'OCR' if page.number+1 in ocr_pages else 'native text')); ordinal+=1; current=[]
                        section=h
                    elif line.strip(): current.append(line.strip())
                if current: blocks.append(Block(page.number+1,ordinal,section,'\\n'.join(current),tuple(b[:4]),'OCR' if page.number+1 in ocr_pages else 'native text')); ordinal+=1
        return meta,blocks,empty,len(doc),ocr_pages
