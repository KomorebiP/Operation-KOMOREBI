from pathlib import Path
import re,json,subprocess,hashlib
base=Path(__file__).resolve().parent
tex=(base/'Quadratic_Form_KCOS_Traditional.tex').read_text()
expanded=tex
for f in ['final_edition_validation.tex','lean_coverage.tex']:
 expanded=expanded.replace(r'\input{'+f+'}',(base/f).read_text())
# Preserve content that Pandoc ordinarily places only in metadata or drops.
expanded=expanded.replace(r'\begin{abstract}',r'\section*{Abstract}').replace(r'\end{abstract}','')
expanded=re.sub(r'\\path\{([^}]+)\}', lambda m:r'\texttt{'+m.group(1).replace('_',r'\_')+'}',expanded)
bibkeys=['Imhof1961','Davies1980','FangOosterlee2008']
expanded=re.sub(r'\\cite\{([^}]+)\}',lambda m:r'\href{#bib:'+m.group(1)+'}{['+str(bibkeys.index(m.group(1))+1)+']}',expanded)
expanded=expanded.replace(r'\begin{thebibliography}{9}',r'\section*{References}\begin{enumerate}')
expanded=expanded.replace(r'\end{thebibliography}',r'\end{enumerate}')
expanded=re.sub(r'\\bibitem\{([^}]+)\}',lambda m:r'\item \label{bib:'+m.group(1)+'}',expanded)
p=subprocess.run(['pandoc','--from=latex','--to=gfm','--wrap=none'],input=expanded,text=True,capture_output=True,cwd=base,check=True)
md=p.stdout

# Convert captions from canonical TeX, rather than keeping Pandoc's raw HTML
# figure-caption fallback. Balanced arguments retain nested mathematical braces.
def balanced_argument(source, start, opening='{', closing='}'):
 assert source[start]==opening,(start,source[start:start+30])
 depth=1; i=start+1
 while i<len(source):
  if source[i]=='\\':
   i+=2
   continue
  if source[i]==opening:depth+=1
  elif source[i]==closing:
   depth-=1
   if depth==0:return source[start+1:i],i+1
  i+=1
 raise AssertionError('Unclosed TeX argument')

def command_argument(source, name):
 match=re.search(r'\\'+re.escape(name)+r'\b',source)
 assert match is not None,('Missing command',name)
 i=match.end()
 while source[i].isspace():i+=1
 if source[i]=='[':
  _,i=balanced_argument(source,i,'[',']')
  while source[i].isspace():i+=1
 return balanced_argument(source,i)[0]

captions={}
caption_audit=[]
for match in re.finditer(r'\\begin\{figure\*?\}([\s\S]*?)\\end\{figure\*?\}',tex):
 body=match.group(1)
 filename=Path(command_argument(body,'includegraphics')).name
 assert filename not in captions,('Duplicate figure filename',filename)
 raw_caption=command_argument(body,'caption')
 converted=subprocess.run(['pandoc','--from=latex','--to=gfm','--wrap=none'],
  input=raw_caption,text=True,capture_output=True,cwd=base,check=True).stdout.strip()
 assert converted and '<span class="math' not in converted,(filename,converted)
 captions[filename]=converted
 caption_audit.append({'image_filename':filename,'canonical_caption_tex':raw_caption,
  'caption_markdown':converted})
used_captions=[]

# Align theorem numbers with the per-section counter in the canonical TeX.
claims=json.loads((base/'claim_inventory.json').read_text())
it=iter(claims)
def claim(m):
 item=next(it)
 assert m.group(2).lower()==item['type'],(m.group(0),item)
 return m.group(1)+m.group(2)+' '+item['number']+m.group(1)
md=re.sub(r'(\*{1,2})(Theorem|Lemma|Proposition|Corollary|Definition|Remark|Algorithm) \d+\1',claim,md)
assert next(it,None) is None,'Unexported statement'
# Use final TeX label numbers for all cross-references, including appendices.
aux=(base/'Quadratic_Form_KCOS_Traditional.aux').read_text()
labels=dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',aux))
def ref(m):
 key=m.group(1);kind=m.group(2)
 number=labels.get(key,m.group(3))
 if kind=='eqref':number='('+number+')'
 return '['+number+'](#'+key+')'
md=re.sub(r'<a href="#([^"]+)" data-reference-type="([^"]+)" data-reference="[^"]+">([^<]*)</a>',ref,md)
# Retain explicit equation target anchors but remove unsupported TeX labels.
def eq(m):
 block=m.group(0); keys=re.findall(r'\\label\{([^}]+)\}',block)
 anchors=''.join('<a id="'+k+'"></a>\n' for k in keys)
 block=re.sub(r'\\label\{[^}]+\}','',block)
 return anchors+block
md=re.sub(r'\$\$[\s\S]*?\$\$',eq,md)
# Figures use the original graphics path, which Pandoc does not resolve.
md=md.replace('src="figure_','src="figures_final/figure_')
# A plain figure keeps its caption adjacent and is readable in Markdown viewers.
def fig(m):
 attrs,body=m.group(1),m.group(2)
 iid=re.search(r'id="([^"]+)"',attrs)
 image=re.search(r'<img src="([^"]+)"[^>]*/?>',body)
 if not image:return m.group(0)
 filename=Path(image.group(1)).name
 assert filename in captions,('Caption not found for image',filename)
 cap=captions[filename]
 used_captions.append(filename)
 anchor='<a id="'+iid.group(1)+'"></a>\n\n' if iid else ''
 return anchor+'![Figure]('+image.group(1)+')\n\n*'+cap+'*\n'
md=re.sub(r'<figure([^>]*)>([\s\S]*?)</figure>',fig,md)
assert len(used_captions)==len(captions)==31,(len(used_captions),len(captions))
assert set(used_captions)==set(captions),'Caption/image mapping mismatch'
# Section anchors survive in the Markdown even when the writer drops heading ids.
for m in re.finditer(r'\\section\{([^{}]+)\}\s*\\label\{([^}]+)\}',tex):
 title,key=m.groups()
 marker='# '+title+'\n'
 if marker in md:md=md.replace(marker,'<a id="'+key+'"></a>\n\n'+marker,1)
# Remove layout-only wrappers; retain named theorem/proof anchors.
md=re.sub(r'<div class="center">\s*([\s\S]*?)\s*</div>',lambda m:m.group(1),md)
def div_anchor(m):
 iid=re.search(r'\bid="([^"]+)"',m.group(1))
 return '<a id="'+iid.group(1)+'"></a>' if iid else ''
md=re.sub(r'<div\b([^>]*)>',div_anchor,md)
md=md.replace('</div>','')
md=md.replace(r'\mathop{\mathrm{\mathbb E}}',r'\mathbb E')
md=re.sub(r'(?m)^(#{1,5}) ',lambda m:'#'+m.group(1)+' ',md)
head='# Komorebi Quadratic-Form Engine and K-COS\n\n**Komorebi P. · Final traditional edition · October 7, 2026**\n\n*Memory-Bounded Structured Solvers, Query-Adaptive Spectral Packets, and Directed-Rounding Extreme-Tail Enclosures*\n\nThis editable text contains the complete traditional edition, including proofs, experiments, companion contracts, and bibliography. Statement and reference numbers match the typeset PDF.\n\n'
md=head+md
assert '<span class="math' not in md,'Raw HTML caption mathematics remain'
assert not re.search(r'</?div\b',md),'Raw div wrappers remain'
image_paths=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',md)
assert len(image_paths)==31 and all((base/path).is_file() for path in image_paths)
(base/'Quadratic_Form_KCOS_Traditional.md').write_text(md)
(base/'MARKDOWN_CAPTION_EXPORT.json').write_text(json.dumps({
 'source':'Quadratic_Form_KCOS_Traditional.tex',
 'source_sha256':hashlib.sha256((base/'Quadratic_Form_KCOS_Traditional.tex').read_bytes()).hexdigest(),
 'caption_conversion':'Canonical balanced TeX caption arguments converted individually by Pandoc latex to gfm; matched by image filename.',
 'caption_count':len(captions),'image_count':len(image_paths),
 'all_image_paths_exist':True,'raw_html_math_spans':0,'raw_div_wrappers':0,
 'captions':caption_audit},indent=2)+'\n')
print('Markdown lines',len(md.splitlines()),'bytes',len(md.encode()))
# Keep all label targets and manuscript-statement counts reviewable.
for item in claims:
 item['pdf_page']=re.search(r'\\newlabel\{'+re.escape(item['label'])+r'\}\{\{[^}]*\}\{([^}]*)\}',aux).group(1)
(base/'claim_inventory.json').write_text(json.dumps(claims,indent=2)+'\n')
anchors={'source':'Quadratic_Form_KCOS_Traditional.tex','pdf':'Quadratic_Form_KCOS_Traditional.pdf','labels':labels,'statement_counts':{k:sum(c['type']==k for c in claims) for k in sorted({c['type'] for c in claims})}}
(base/'source_anchors.json').write_text(json.dumps(anchors,indent=2)+'\n')
