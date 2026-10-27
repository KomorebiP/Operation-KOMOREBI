from pathlib import Path
import json,re,hashlib,difflib
import fitz
ROOT=Path(__file__).resolve().parent.parent
S=ROOT/'source_v_viii'
OUT=ROOT/'editorial/book_revision'
configs={
 'V':(['traditional/atlas-pages.tex'],['visual_guide/source/pages_final.tex'],'vpage'),
 'VI':(['traditional/atlas-pages.tex'],['visual_guide/source/pages.tex','visual_guide/source/extensions.tex'],'vvpage'),
 'VII':(['traditional/monograph_atlas.tex'],['visual_guide/source/pages.tex','visual_guide/source/extended_pages.tex'],'atlasvpage'),
 'VIII':(['traditional/atlas_sources/pages.tex','traditional/atlas_sources/extended_pages.tex'],['visual_guide/source/pages.tex','visual_guide/source/extended_pages.tex'],'atlasvpage'),
}
def parse(paths):
 result={}
 for p in paths:
  t=p.read_text();starts=list(re.finditer(r'\\vpage\{([0-9]+)\}',t))
  for i,m in enumerate(starts):
   pos=m.start()+len('\\vpage');args=[]
   for j in range(4):
    assert t[pos]=='{';begin=pos+1;depth=1;pos+=1
    while depth:
     c=t[pos]
     if c=='{' and t[pos-1]!='\\':depth+=1
     if c=='}' and t[pos-1]!='\\':depth-=1
     pos+=1
    args.append(t[begin:pos-1])
   body=t[pos:starts[i+1].start() if i+1<len(starts) else len(t)]
   # Atlas file wrappers are outside the final mathematical plate.
   body=re.sub(r'\\endgroup\s*$','',body)
   result[int(args[0])]={'title':args[1],'kicker':args[2],'locator':args[3],'body':body.strip(),'source':str(p.relative_to(ROOT))}
 return result
def norm(s):
 s=s.replace(r'\platecaption',r'\captiontext').replace('visual_graphics/','graphics/')
 return re.sub(r'\s+',' ',s).strip()
def names(p,prefix):
 d=fitz.open(p);ns=d.resolve_names();return {int(k[len(prefix):]):v['page']+1 for k,v in ns.items() if re.fullmatch(prefix+r'\d+',k)}
def figurepaths(roman,role,body):
 base=S/roman/'editable'/role
 out=[]
 for kind,stem in re.findall(r'\\(vfig|xfig)(?:\[[^\]]*\])?\{([^}]+)\}',body):
  if role=='visual_guide':folder='graphics' if kind=='vfig' else 'graphics_extended'
  elif roman=='VIII':folder='atlas_sources/graphics'
  else:folder='visual_graphics' if kind=='vfig' else 'visual_graphics_extended'
  p=base/folder/(stem+'.tex');out.append((kind,stem,hashlib.sha256(p.read_bytes()).hexdigest()))
 for asset in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',body):
  p=base/asset;out.append(('includegraphics',p.name,hashlib.sha256(p.read_bytes()).hexdigest()))
 return out
allrows=[];differences=[]
for roman,(ts,vs,prefix) in configs.items():
 base=S/roman/'editable';tp=parse([base/f for f in ts]);vp=parse([base/f for f in vs]);assert tp.keys()==vp.keys()
 tpdf=S/'compiled'/roman/'traditional'/f'Paper_{roman}_Traditional_Final.pdf';vpdf=S/'compiled'/roman/'visual_guide'/f'Paper_{roman}_Visual_Guide_Final.pdf'
 tn=names(tpdf,prefix);vn=names(vpdf,'vpage')
 for n,t in tp.items():
  v=vp[n]
  row={'chapter':roman,'plate':n,'title':t['title'],'traditional_pdf_page':tn[n],'visual_pdf_page':vn[n],'traditional_destination':prefix+str(n),'visual_destination':'vpage'+str(n),'title_equal':t['title']==v['title'],'kicker_equal':t['kicker']==v['kicker'],'body_equal_whitespace_normalized':norm(t['body'])==norm(v['body']),'figure_source_hashes_equal':figurepaths(roman,'traditional',t['body'])==figurepaths(roman,'visual_guide',v['body']),'traditional_locator':t['locator'],'visual_locator':v['locator'],'locator_equal':t['locator']==v['locator'],'sources':[t['source'],v['source']]}
  allrows.append(row)
  if not row['body_equal_whitespace_normalized']:
   differences.append({'chapter':roman,'plate':n,'diff':'\n'.join(difflib.unified_diff(t['body'].splitlines(),v['body'].splitlines(),fromfile='embedded',tofile='standalone',lineterm=''))})
(OUT/'v_viii_plate_overlap.json').write_text(json.dumps({'rows':allrows,'body_differences':differences},indent=2))
lines=['# V–VIII visual plate overlap','', '| Plate | Traditional PDF page | Standalone PDF page | Body identical¹ | Figures identical² | Locator identical |','|---|---:|---:|---|---|---|']
for r in allrows:lines.append(f"| {r['chapter']}.{r['plate']} | {r['traditional_pdf_page']} | {r['visual_pdf_page']} | {r['body_equal_whitespace_normalized']} | {r['figure_source_hashes_equal']} | {r['locator_equal']} |")
lines+=['','¹ Whitespace, equivalent caption macro names and corresponding asset-directory prefixes normalized; final atlas group wrapper excluded. ² SHA-256 of corresponding TikZ source files.','']
for x in differences:lines += [f"## Plate {x['chapter']}.{x['plate']} body differences",'```diff',x['diff'],'```','']
(OUT/'v_viii_plate_overlap.txt').write_text('\n'.join(lines))
print({x:{'plates':sum(r['chapter']==x for r in allrows),'body_mismatches':[r['plate'] for r in allrows if r['chapter']==x and not r['body_equal_whitespace_normalized']],'figure_mismatches':[r['plate'] for r in allrows if r['chapter']==x and not r['figure_source_hashes_equal']],'locator_mismatches':[r['plate'] for r in allrows if r['chapter']==x and not r['locator_equal']]} for x in configs})
