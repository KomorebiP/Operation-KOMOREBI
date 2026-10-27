"""Compare lossless PDF candidates against a fixed intermediate book."""
from pathlib import Path
import hashlib,json,re,sys,time
import fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from audit_monograph import annotation_xrefs,inspect_action

def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def canonical(value):
 if isinstance(value,dict):return {k:canonical(v) for k,v in value.items() if k not in ('xref','id','seqno')}
 if isinstance(value,(list,tuple,fitz.Rect,fitz.Point,fitz.Matrix,fitz.Quad)):return [canonical(v) for v in value]
 return value

def embedded_actions(doc,page):
 result=[]
 for xref in annotation_xrefs(doc,page):
  action=inspect_action(doc,xref)
  if action is not None and action('S')[1]=='/GoToE':
   result.append({'attachment':action('T/N')[1],'relation':action('T/R')[1],
    'destination':re.sub(r'\s+','',action('D')[1])})
 return result

def verify(source,candidate,out):
 start=time.monotonic();a,b=fitz.open(source),fitz.open(candidate)
 counts={'pages':0,'link_records':0,'embedded_actions':0,'attachments':0}
 report={'status':'RUNNING','source':{'bytes':source.stat().st_size,'sha256':sha(source)},
  'candidate':{'bytes':candidate.stat().st_size,'sha256':sha(candidate)}}
 def equal(x,y,what,pn=None):
  if x!=y:raise ValueError(what+(' on page '+str(pn) if pn is not None else ''))
 try:
  equal(len(a),len(b),'Page count changed')
  equal(a.metadata,b.metadata,'Metadata changed')
  equal(a.get_page_labels(),b.get_page_labels(),'Page labels changed')
  equal(canonical(a.get_toc(simple=False)),canonical(b.get_toc(simple=False)),'Bookmarks changed')
  equal(canonical(a.resolve_names()),canonical(b.resolve_names()),'Named destinations changed')
  equal(a.embfile_names(),b.embfile_names(),'Attachment names/order changed')
  for name in a.embfile_names():
   equal(a.embfile_get(name),b.embfile_get(name),'Attachment bytes changed: '+name);counts['attachments']+=1
  for i,(p,q) in enumerate(zip(a,b),1):
   equal(p.rect,q.rect,'Page geometry changed',i)
   equal(p.get_text('rawdict'),q.get_text('rawdict'),'Extracted glyph, font, image or geometry record changed',i)
   equal(canonical(p.get_links()),canonical(q.get_links()),'Link semantics or rectangle changed',i)
   equal(p.get_bboxlog(),q.get_bboxlog(),'Graphic operation bbox changed',i)
   equal(canonical(p.get_drawings()),canonical(q.get_drawings()),'Vector path/style changed',i)
   equal(canonical(p.get_image_info(hashes=True)),canonical(q.get_image_info(hashes=True)),'Scientific image digest/placement changed',i)
   ae,be=embedded_actions(a,p),embedded_actions(b,q);equal(ae,be,'Embedded reference actions changed',i)
   counts['pages']+=1;counts['link_records']+=len(p.get_links());counts['embedded_actions']+=len(ae)
  report.update({'status':'PASS','seconds':round(time.monotonic()-start,2),'checks':counts,
    'scope':'All-page exact extracted glyph/font/image records, exact vector operations, link semantics/rectangles and embedded actions, metadata, labels, outlines, named destinations and exact attachment bytes. PDF object identities excluded from semantic link/vector comparisons.'})
 except Exception as exc:
  report.update({'status':'FAIL','seconds':round(time.monotonic()-start,2),'checks_completed':counts,'error':str(exc)});raise
 finally:
  out.write_text(json.dumps(report,indent=2)+'\n');a.close();b.close()
 return report
if __name__=='__main__':
 result=verify(*map(Path,sys.argv[1:4]));print(json.dumps(result,indent=2))
