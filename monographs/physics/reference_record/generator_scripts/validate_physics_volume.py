import fitz,json,pathlib,sys,collections,hashlib
root=pathlib.Path(__file__).resolve().parent.parent
m=json.loads((root/'book/volume_manifest.json').read_text())
fn=root/'book/Komorebi_Physics_Collected_Volume_0.6.0_2026-10-20.pdf'
d=fitz.open(fn)
assert len(d)==m['page_count']
assert len(m['components'])==19
assert sum(e['page_count'] for e in m['components'])==610
assert d[2].get_links() and len(d[2].get_links())==8
assert len(d[3].get_links())==11
assert len(d.get_toc())>=450
for e in m['components']:
 n=e['page_start']-1
 assert n>=0 and n+e['page_count']<=len(d)
 assert len(d[n].get_text())>20, (e['title'],n)
 source=pathlib.Path(e['source_path']); assert hashlib.sha256(source.read_bytes()).hexdigest()==e['source_sha256']
# No erroneous text outside each physical page.
for n in [0,1,2,3,4,5,6,41,42,78,79,91,92,93,239,240,287,288,528,529,len(d)-1]:
 page=d[n]
 for w in page.get_text('words'):
  assert w[0]>-0.5 and w[1]>-0.5 and w[2]<page.rect.width+1 and w[3]<page.rect.height+1,(n,w)
# Check chapter start matches outline and navigable contents.
for e in m['components']:
 assert any(x[1]==e['title'] and x[2]==e['page_start'] for x in d.get_toc()),e['title']
res={'ok':True,'page_count':len(d),'source_pdf_count':len(m['components']),
     'source_content_pages':610,'part_dividers':7,'frontmatter_pages':5,
     'bookmark_count':len(d.get_toc()),'frontmatter_links':len(d[2].get_links())+len(d[3].get_links()),
     'pdf_bytes':fn.stat().st_size,'book_sha256':hashlib.sha256(fn.read_bytes()).hexdigest()}
(root/'book'/'book_validation.json').write_text(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
