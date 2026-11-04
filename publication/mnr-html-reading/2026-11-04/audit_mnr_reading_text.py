"""Find long visible-text discrepancies between the PDF and HTML conversion."""
from pathlib import Path
import collections,json,re,unicodedata
from html.parser import HTMLParser
import pypdfium2 as pdf
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'output/mnr-html-work'
class Text(HTMLParser):
    def __init__(self,text):super().__init__();self.parts=[];self.feed(text)
    def handle_data(self,text):self.parts.append(text)
def normalized(text):
    text=unicodedata.normalize('NFKC',text).replace('\u00ad','')
    text=re.sub(r'(?<=\w)[-‐]\s*[\r\n]+\s*(?=\w)','',text)
    text=re.sub(r'\\[a-zA-Z]+\*?',' ',text)
    return re.findall(r"[a-z]+(?:['’][a-z]+)?",text.lower())
def grams(words,n=7):return {' '.join(words[i:i+n]) for i in range(len(words)-n+1)}
def main():
    metadata=json.loads((WORK/'reading-metadata.json').read_bytes());parts=[]
    for page in metadata['pages']:
        parts.extend([page['title'],' '.join(Text((WORK/'pages'/page['file']).read_text(encoding='utf-8')).parts)])
    # Figure text is retained as graphics, and must not be misreported as lost prose.
    for name in ['figure-export.pdf','diagram-1.pdf','diagram-2.pdf']:
        d=pdf.PdfDocument(ROOT/'output/mnr-figure-work'/name)
        for i in range(len(d)):parts.append(d[i].get_textpage().get_text_range())
    for p in (ROOT/'output/MNR/sources/monographs/large-signal-model/Visual_Companion/figures').glob('*.pdf'):
        d=pdf.PdfDocument(p)
        for i in range(len(d)):parts.append(d[i].get_textpage().get_text_range())
    known=grams(normalized('\n'.join(parts)));document=pdf.PdfDocument(ROOT/'output/MNR/main.pdf');candidates=[];total=missing=0
    for i in range(len(document)):
        words=normalized(document[i].get_textpage().get_text_range());flags=[]
        for j in range(len(words)-6):
            total+=1;absent=' '.join(words[j:j+7]) not in known;missing+=absent;flags.append(absent)
        start=None
        for j,absent in enumerate(flags+[False]):
            if absent and start is None:start=j
            if not absent and start is not None:
                if j-start>=8:candidates.append(dict(page=i+1,words=j-start+6,text=' '.join(words[max(0,start-3):j+9])))
                start=None
    duplicate=[]
    for page in metadata['pages']:
        text=' '.join(Text((WORK/'pages'/page['file']).read_text(encoding='utf-8')).parts)
        for m in re.finditer(r'\b(the|and|of|to|is|that|in)\s+\1\b',text,re.I):duplicate.append(dict(file=page['file'],context=text[max(0,m.start()-70):m.end()+70]))
    result=dict(pdf_pages=len(document),english_7grams=total,unmatched_7grams=missing,candidates=sorted(candidates,key=lambda r:r['words'],reverse=True),duplicate_words=duplicate)
    (WORK/'TEXT_COMPARISON.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('candidates','duplicate_words')}))
    print(json.dumps({'largest_candidates':result['candidates'][:15],'duplicate_words':duplicate[:20]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
