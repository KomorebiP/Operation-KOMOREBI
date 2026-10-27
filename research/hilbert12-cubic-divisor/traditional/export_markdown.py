#!/usr/bin/env python3
"""Full GFM mathematical export, with canonical balanced figure captions."""
from pathlib import Path
import hashlib,json,re,subprocess
B=Path(__file__).resolve().parent;N='H12_Cubic_Divisor_Traditional'
def expand(p):
 s=p.read_text()
 return re.sub(r'\\input\{([^}]+)\}',lambda m:expand(B/m.group(1)),s)
tex=expand(B/(N+'.tex'))
def argument(s,i,op='{',cl='}'):
 assert s[i]==op
 depth=1;j=i+1
 while j<len(s):
  if s[j]=='\\':j+=2;continue
  if s[j]==op:depth+=1
  elif s[j]==cl:
   depth-=1
   if depth==0:return s[i+1:j],j+1
  j+=1
 raise ValueError('Unbalanced TeX argument')
def command(s,name):
 m=re.search(r'\\'+name+r'\b',s);assert m,(name,s[:50]);i=m.end()
 while s[i].isspace():i+=1
 if s[i]=='[':_,i=argument(s,i,'[',']')
 while s[i].isspace():i+=1
 return argument(s,i)[0]
# Resolve only the explicitly used file-existence figure condition.
while r'\IfFileExists' in tex:
 m=re.search(r'\\IfFileExists',tex);i=m.end();filename,i=argument(tex,i);yes,i=argument(tex,i);no,i=argument(tex,i)
 tex=tex[:m.start()]+(yes if (B/filename).is_file() else no)+tex[i:]
expanded=tex.replace(r'\begin{abstract}',r'\section*{Abstract}').replace(r'\end{abstract}','')
bibkeys=re.findall(r'\\bibitem\{([^}]+)\}',expanded)
expanded=re.sub(r'\\cite\{([^}]+)\}',lambda m:r'\href{#bib:'+m.group(1)+'}{['+str(bibkeys.index(m.group(1))+1)+']}',expanded)
expanded=re.sub(r'\\begin\{thebibliography\}\{[^}]+\}',r'\\section*{References}\\begin{enumerate}',expanded).replace(r'\end{thebibliography}',r'\end{enumerate}')
expanded=re.sub(r'\\bibitem\{([^}]+)\}',lambda m:r'\item\label{bib:'+m.group(1)+'}',expanded)
md=subprocess.run(['pandoc','-f','latex','-t','gfm','--wrap=none'],cwd=B,input=expanded,text=True,capture_output=True,check=True).stdout
aux=(B/(N+'.aux')).read_text();labels=dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',aux))
claims=[]
for m in re.finditer(r'\\begin\{(theorem|proposition|lemma|corollary|definition|remark)\}([\s\S]*?)\\end\{\1\}',tex):
 kind,body=m.groups();keys=re.findall(r'\\label\{([^}]+)\}',body);assert keys,(kind,body[:80]);key=keys[0]
 src='sections/norms.tex' if key=='prop:allnorms' else 'sections/principal.tex' if key in ['thm:base-divisor','thm:complete-divisor','thm:transitions','thm:anchor'] else 'sections/rigidity.tex' if key=='thm:principal-rigidity' else 'sections/reconstruction.tex'
 page=re.search(r'\\newlabel\{'+re.escape(key)+r'\}\{\{[^}]*\}\{([^}]*)\}',aux).group(1)
 claims.append({'type':kind,'label':key,'number':labels[key],'pdf_page':page,'editable_source':src,'source_sha256':hashlib.sha256((B/src).read_bytes()).hexdigest(),'status':'ordinary mathematical source proof; formal consequence coverage separately scoped'})
claim_it=iter(claims)
def claim_number(m):
 c=next(claim_it);assert m.group(2).lower()==c['type']
 return m.group(1)+m.group(2)+' '+c['number']+m.group(1)
md=re.sub(r'(\*{1,2})(Theorem|Proposition|Lemma|Corollary|Definition|Remark) \d+\1',claim_number,md)
assert next(claim_it,None) is None
def ref(m):
 k,t,old=m.groups();num=labels.get(k,old);num='('+num+')' if t=='eqref' else num
 return '['+num+'](#'+k+')'
md=re.sub(r'<a href="#([^"]+)" data-reference-type="([^"]+)" data-reference="[^"]+">([^<]*)</a>',ref,md)
def eq(m):
 s=m.group();ids=re.findall(r'\\label\{([^}]+)\}',s)
 return ''.join('<a id="'+k+'"></a>\n' for k in ids)+re.sub(r'\\label\{[^}]+\}','',s)
md=re.sub(r'\$\$[\s\S]*?\$\$',eq,md)
captions={};records=[]
for m in re.finditer(r'\\begin\{figure\}([\s\S]*?)\\end\{figure\}',tex):
 body=m.group(1);filename=Path(command(body,'includegraphics')).name;cap=command(body,'caption')
 converted=subprocess.run(['pandoc','-f','latex','-t','gfm','--wrap=none'],input=cap,text=True,capture_output=True,check=True).stdout.strip()
 converted=re.sub(r'<a href="#([^"]+)" data-reference-type="([^"]+)" data-reference="[^"]+">([^<]*)</a>',ref,converted)
 assert '<span class="math' not in converted
 captions[filename]=converted;records.append({'filename':filename,'canonical_tex':cap,'markdown':converted})
used=[]
def fig(m):
 attrs,body=m.groups();im=re.search(r'<img src="([^"]+)"',body);assert im
 path=im.group(1);filename=Path(path).name;assert filename in captions;used.append(filename)
 iid=re.search(r'id="([^"]+)"',attrs)
 return ('<a id="'+iid.group(1)+'"></a>\n\n' if iid else '')+'![Figure]('+path+')\n\n*'+captions[filename]+'*\n'
md=re.sub(r'<figure([^>]*)>([\s\S]*?)</figure>',fig,md)
def div(m):
 iid=re.search(r'id="([^"]+)"',m.group(1));return '<a id="'+iid.group(1)+'"></a>' if iid else ''
md=re.sub(r'<div\b([^>]*)>',div,md).replace('</div>','')
md=re.sub(r'(?m)^(#{1,5}) ',lambda m:'#'+m.group(1)+' ',md)
for title,key in re.findall(r'\\section\{([^{}]+)\}\s*\\label\{([^}]+)\}',tex):
 marker='## '+title+'\n'
 if marker in md:md=md.replace(marker,'<a id="'+key+'"></a>\n\n'+marker,1)
md='# Cubic Divisor Transport and Reconstruction\n\n**Komorebi P. · Final traditional companion edition · October 7, 2026**\n\n'+md
assert '<span class="math' not in md,'HTML mathematics remain'
assert not re.search(r'</?div\b',md),'HTML layout wrappers remain'
paths=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',md)
assert set(used)==set(captions) and len(paths)==len(captions)
assert all((B/p).is_file() for p in paths)
(B/(N+'.md')).write_text(md)
(B/'MANUSCRIPT_CLAIM_INVENTORY.json').write_text(json.dumps(claims,indent=2)+'\n')
(B/'MARKDOWN_EXPORT_AUDIT.json').write_text(json.dumps({'expanded_tex_sha256':hashlib.sha256(tex.encode()).hexdigest(),'source_sha256':hashlib.sha256((B/(N+'.tex')).read_bytes()).hexdigest(),'markdown_sha256':hashlib.sha256(md.encode()).hexdigest(),'lines':len(md.splitlines()),'bytes':len(md.encode()),'captions':records,'image_paths_exist':True,'HTML_math_spans':0,'HTML_divs':0,'label_numbers':labels},indent=2)+'\n')
print('Full mathematical Markdown:',len(md.encode()),'bytes')
