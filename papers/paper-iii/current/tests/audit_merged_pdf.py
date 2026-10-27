from pathlib import Path
import fitz,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'checkpoint_v0.3.0' if (ROOT/'checkpoint_v0.3.0').exists() else ROOT.parent/'Paper_III_Continuation_v0.3.0'
book=fitz.open(ROOT/'publication/Paper_III_Integrated_Reading_Edition_v1.0.0_rc1.pdf')
segments=[(ROOT/'publication/Paper_III_Release_Scope_v1.0.0_rc1.pdf',2),(BASE/'baseline/publication/pdfs/Paper_III_Traditional_Final.pdf',98),(ROOT/'docs/Paper_III_Section17_Analytic_Closeout.pdf',5),(BASE/'baseline/publication/pdfs/Paper_III_Visual_Guide_Final.pdf',26),(BASE/'baseline/publication/pdfs/Paper_III_Lean_Guide_Final.pdf',49)]
assert len(book)==sum(n for _,n in segments)==180
start=0;checks=0;pages_emptied=[];outside=[]
for path,n in segments:
 original=fitz.open(path)
 assert len(original)==n
 for i in range(n):
  got=book[start+i].get_text(sort=True)
  orig=original[i].get_text(sort=True)
  assert got==orig,(start+i+1,path.name)
  checks+=1
  if len(got.strip())<35: pages_emptied.append(start+i+1)
  page=book[start+i]
  for line in page.get_text('dict')['blocks']:
   if line['type'] != 0:continue
   for row in line.get('lines',[]):
    for span in row.get('spans',[]):
     if not span['text'].strip():continue
     a=fitz.Rect(span['bbox']);r=page.rect
     if a.x0<-3 or a.y0<-3 or a.x1>r.x1+3 or a.y1>r.y1+3:outside.append({'page':start+i+1,'span':span['text'][:40],'bbox':list(a)})
 start+=n
pdf=ROOT/'docs/Paper_III_Section17_Analytic_Closeout.pdf'
assert all(p.get_text().strip() for p in fitz.open(pdf))
status={'schema':'paper_iii_reader_comparison/1','status':'PASS' if not outside and not pages_emptied else 'WARN',
 'pages':len(book),'source_page_text_identical':checks,'table_of_contents':book.get_toc(),
 'empty_or_unreadable_pages':pages_emptied,'outside_crop_spans':outside[:25],
 'source_bookmark_count':len(book.get_toc()),'source_segment_page_counts':[n for _,n in segments],
 'note':'Exact Unicode text checks across all pages. Not a line-by-line human proof audit.'}
(ROOT/'evidence/READER_TEXT_AND_CROP_AUDIT.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status,indent=2)[:4000]);assert status['status']=='PASS',status
