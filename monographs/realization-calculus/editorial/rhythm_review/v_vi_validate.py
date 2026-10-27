from pathlib import Path
import json,re,hashlib,difflib
D=Path('editorial/rhythm_review');B=D/'v_vi_before'
fs=[Path(p) for p in json.loads((D/'v_vi_scope.json').read_text())['continuous_review_files']]
mathre=re.compile(r'(?<!\\)\\\[.*?(?<!\\)\\\]|(?<!\\)\\\(.*?(?<!\\)\\\)|(?<!\\)\$\$.*?(?<!\\)\$\$|(?<![\\$])\$(?!\$).*?(?<!\\)\$|\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?|displaymath|math)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|multline\*?|displaymath|math)\}',re.S)
litre=re.compile(r'\\begin\{(lstlisting|Verbatim|verbatim|minted)\}.*?\\end\{\1\}|\\(?:code|texttt|nolinkurl|url|path|lstinline)\{(?:[^{}]|\{[^{}]*\})*\}',re.S)
structre=re.compile(r'\\(?:label|ref|eqref|cref|Cref|pageref|cite|citep|citet|input|includegraphics|include|hypertarget|hyperlink|setcounter|addtocounter|bibliography|bibliographystyle)(?:\[[^\]]*\])?\{[^{}]*\}')
extract=lambda pat,s:[m.group(0) for m in pat.finditer(s)]
checks=[];patch=[];edited=[]
for p in fs:
 a=(B/p).read_text();b=p.read_text();rec={'file':str(p),'raw_tex_words_before':len(a.split()),'raw_tex_words_after':len(b.split())}
 for name,pat in [('math',mathre),('literal',litre),('structural',structre)]:
  aa=extract(pat,a);bb=extract(pat,b)
  rec[name+'_region_count']=len(aa);rec[name+'_identical']=aa==bb
  if aa!=bb:print('MISMATCH',name,p)
 rec['before_sha256']=hashlib.sha256(a.encode()).hexdigest();rec['after_sha256']=hashlib.sha256(b.encode()).hexdigest();checks.append(rec)
 if a!=b:
  edited.append(str(p));patch.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=str(B/p),tofile=str(p)))
v=Path('source_v_viii/V/editable');vi=Path('source_v_viii/VI/editable')
a=(v/'traditional/atlas-pages.tex').read_text().replace('\\platecaption','\\captiontext').replace('visual_graphics/','graphics/').strip();b=(v/'visual_guide/source/pages_final.tex').read_text().strip()
a_vi=(vi/'traditional/atlas-pages.tex').read_text().replace('\\platecaption','\\captiontext');start=a_vi.index('\\vpage{1}');end=a_vi.rindex('\\endgroup');a_vi=a_vi[start:end].strip()
b_vi=((vi/'visual_guide/source/pages.tex').read_text()+'\n'+(vi/'visual_guide/source/extensions.tex').read_text()).strip()
norm=lambda s:re.sub(r'\s+',' ',s).strip()
plate={'V_body_matches_standalone':norm(a)==norm(b),'VI_body_matches_standalone':norm(a_vi)==norm(b_vi),'normalizations':'caption wrapper macro (platecaption/captiontext); V graphic directory prefix; VI group wrapper; whitespace'}
checks_pass=all(r['math_identical'] and r['literal_identical'] and r['structural_identical'] for r in checks)
result={'checks':checks,'plate_consistency':plate,'all_protected_regions_identical':checks_pass,'counts':{'files':len(fs),'edited_files':len(edited),'raw_tex_words_before':sum(r['raw_tex_words_before'] for r in checks),'raw_tex_words_after':sum(r['raw_tex_words_after'] for r in checks),'math_regions':sum(r['math_region_count'] for r in checks),'literal_regions':sum(r['literal_region_count'] for r in checks),'structural_regions':sum(r['structural_region_count'] for r in checks)}}
(D/'v_vi_preservation.json').write_text(json.dumps(result,indent=2)+'\n')
(D/'v_vi_changes.patch').write_text(''.join(patch));(D/'v_vi_edited_files.json').write_text(json.dumps(edited,indent=2)+'\n')
print(result['counts']);print('Protected:',checks_pass,'Plate bodies:',plate)
assert checks_pass and plate['V_body_matches_standalone'] and plate['VI_body_matches_standalone']
