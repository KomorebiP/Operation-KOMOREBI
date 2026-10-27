#!/usr/bin/env python3
"""Inventory only current reader prose; never mutate canonical sources."""
from pathlib import Path
import hashlib, json, re

ROOT = Path('/dev/shm/komorebi_core_monograph_fbc994080222')
OUT = ROOT / 'editorial/rhythm_review'
scope=[]
for chap in ['XI','XII']:
    root=ROOT/'source_ix_xii'/chap/'publication/source'
    for role, kind in [('traditional','Traditional'),('visual_guide','Visual_Guide'),('lean_guide','Lean_Guide')]:
        scope.append(root/role/f'Paper_{chap}_{kind}_Final.tex')
        route=root/role/('reader_route.tex' if chap=='XI' else 'reading_route.tex')
        if route.exists(): scope.append(route)
    if chap=='XI':
        scope += sorted((root/'traditional/appendices').glob('*.tex'))
        scope.append(root/'lean_guide/current_verification.tex')
    else: scope.append(root/'visual_guide/source/pages.tex')

LITERAL=re.compile(r'\\begin\{(lstlisting|Verbatim|verbatim|minted|quote)\}.*?\\end\{\1\}',re.S)
MATH=re.compile(r'(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$|\\\[.*?\\\]|\\\(.*?\\\)|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}',re.S)
XII_STATEMENTS=re.compile(r'\\begin\{(theorem|proposition|lemma|corollary|definition|standardfact)\}.*?\\end\{\1\}',re.S)
MACROS=re.compile(r'\\(nolinkurl|path|code|texttt|input|include|includegraphics|VerbatimInput|label|ref|eqref|pageref|cite|href|hyperref|url|hypertarget)\*?')

def balanced(s,pos,left='{',right='}'):
    depth=0
    for i in range(pos,len(s)):
        if s[i]==left and (i==0 or s[i-1]!='\\'): depth+=1
        elif s[i]==right and (i==0 or s[i-1]!='\\'):
            depth-=1
            if depth==0:return i+1
    raise ValueError(s[pos:pos+80])

def macro_spans(s):
    spans=[]
    for m in MACROS.finditer(s):
        p=m.end()
        while p<len(s) and s[p].isspace(): p+=1
        if p<len(s) and s[p]=='[':p=balanced(s,p,'[',']')
        for _ in range(2 if m.group(1)=='href' else 1):
            while p<len(s) and s[p].isspace():p+=1
            if p<len(s) and s[p]=='{':p=balanced(s,p)
        spans.append((m.start(),p))
    return spans

def extra_spans(s,name):
    spans=[]
    if '\\begin{document}' in s:spans.append((0,s.index('\\begin{document}')+len('\\begin{document}')))
    if name.endswith('XI_Lean_Guide_Final.tex'):
        a=s.index('\\appendix\\chapter{Complete selected named-source catalog}')
        spans.append((a,len(s)))
        a=s.index('Fix the declared class',s.index('\\section{The publication statement}'))
        spans.append((a,s.index('\n\n',a)))
    if '/XI/' in name and name.endswith('XI_Visual_Guide_Final.tex'):
        a=s.index('\\textbf{Conjecture 66 (arithmetic packet realization).}')
        spans.append((a,s.index('\n\n',a)))
    if '/XI/' in name and '/traditional/' in name:
        spans += [(m.start(),m.end()) for m in re.finditer(r'\\begin\{conjecture\}.*?\\end\{conjecture\}',s,re.S)]
    if '/XII/' in name and '/traditional/' in name:
        spans += [(m.start(),m.end()) for m in XII_STATEMENTS.finditer(s)]
    return spans

def masked(s,name):
    literals=[(m.start(),m.end()) for m in LITERAL.finditer(s)]
    chars=list(s)
    for a,b in literals:chars[a:b]=['\n' if c=='\n' else ' ' for c in s[a:b]]
    math=[(m.start(),m.end()) for m in MATH.finditer(''.join(chars))]
    spans=literals+math+macro_spans(s)+extra_spans(s,name)
    spans +=[(m.start(),m.end()) for m in re.finditer(r'(?<!\\)%[^\n]*',s)]
    chars=list(s)
    for a,b in spans:chars[a:b]=['\n' if c=='\n' else ' ' for c in s[a:b]]
    return ''.join(chars)

if __name__=='__main__':
    records=[]; scopeinfo=[]
    for path in dict.fromkeys(scope):
        s=path.read_text();name=str(path.relative_to(ROOT));mask=masked(s,name)
        paras=[]
        for m in re.finditer(r'\S(?:.|\n)*?(?=\n\s*\n|\Z)',s):
            a,b=m.span(); prose=mask[a:b]
            semis=len(re.findall(';',prose));dashes=len(re.findall(r'--+|[—–]',prose))
            hyphens=re.findall(r'\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+\b',prose)
            if semis or dashes or hyphens:
                paras.append({'line':s[:a].count('\n')+1,'end_line':s[:b].count('\n')+1,
                              'semicolons':semis,'dash_or_ranges':dashes,'hyphen_compounds':hyphens,
                              'text':m.group()})
        rec={'file':name,'raw_lines':len(s.splitlines()),'raw_words':len(s.split()),'sha256':hashlib.sha256(s.encode()).hexdigest(),
             'eligible_semicolons':sum(p['semicolons'] for p in paras),'dash_or_range_candidates':sum(p['dash_or_ranges'] for p in paras),
             'hyphen_compounds':sum(len(p['hyphen_compounds']) for p in paras),'candidate_paragraphs':len(paras),'paragraphs':paras}
        records.append(rec)
        txt='\n\n'.join(f"[{p['line']}–{p['end_line']}; semi={p['semicolons']}; dash={p['dash_or_ranges']}; hyphens={','.join(p['hyphen_compounds'])}]\n{p['text']}" for p in paras)
        tag=name.split('/')[1]+'_'+name.split('/')[4]+'_'+path.stem
        dest=OUT/f'xi_xii_reader_{tag}.txt';dest.write_text(txt+'\n')
        scopeinfo.append({k:v for k,v in rec.items() if k!='paragraphs'}|{'reader':str(dest.relative_to(ROOT))})
    (OUT/'xi_xii_candidates.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
    (OUT/'xi_xii_scope.json').write_text(json.dumps(scopeinfo,indent=2)+'\n')
    print(json.dumps(scopeinfo,indent=2))
