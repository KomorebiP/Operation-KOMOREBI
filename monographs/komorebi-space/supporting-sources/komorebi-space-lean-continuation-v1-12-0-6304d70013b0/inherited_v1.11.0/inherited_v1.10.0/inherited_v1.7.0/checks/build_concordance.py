#!/usr/bin/env python3
"""Resolve editorial claim IDs against frozen source inventories.

This checks declaration identity and source hashes against the retained accepted version 1.2.0 replay. It is not a Lean compiler and
cannot certify the semantic equivalence of edited prose and a theorem type.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
TREES = {'F': ROOT/'evidence/foundations_v020', 'M': ROOT/'evidence/moving_v032',
         'S': ROOT/'evidence/selected', 'I': ROOT/'formal'}
ARCHIVES = {'F':'Komorebi_Space_Lean_v0.20.0.zip',
            'M':'Komorebi_Moving_Exact_Spaces_v0.32.0.zip'}

def strip_comments(s: str) -> str:
    out=[];i=0;depth=0;in_str=False
    while i<len(s):
        if depth:
            if s[i:i+2]=='/-': depth+=1;out.extend('  ');i+=2
            elif s[i:i+2]=='-/': depth-=1;out.extend('  ');i+=2
            else: out.append('\n' if s[i]=='\n' else ' ');i+=1
        elif not in_str and s[i:i+2]=='/-': depth=1;out.extend('  ');i+=2
        elif not in_str and s[i:i+2]=='--':
            j=s.find('\n',i)
            if j<0:j=len(s)
            out.extend(' '*(j-i));i=j
        else:
            if s[i]=='"' and (i==0 or s[i-1]!='\\'):in_str=not in_str
            out.append(s[i]);i+=1
    return ''.join(out)

def tex(s: str) -> str:
    for a,b in [('\\',r'\textbackslash{}'),('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#')]:s=s.replace(a,b)
    return s

def main() -> None:
    release=json.loads((ROOT/'audit/formal/release.json').read_text())
    if release.get('status')!='PASS':raise RuntimeError('Retained formal baseline is not PASS')
    envrows=json.loads((ROOT/release['axiom_report']).read_text())['declarations']
    current_hashes=release['source_sha256']
    historical={}
    for k,a in ARCHIVES.items():
        with ZipFile(ROOT/'evidence/archives'/a) as z:
            name=next(n for n in z.namelist() if n.endswith('/audit/declaration_index.json'))
            historical[k]=json.loads(z.read(name))
    rows=[];missing=[]
    for row in csv.reader((ROOT/'data/claim_specs.tsv').read_text().splitlines(),delimiter='\t'):
        if not row:continue
        cid,title,specs,note=row
        refs=[]
        if specs!='W':
            for spec in specs.split(';'):
                k,rest=spec.split(':',1);module,names=rest.split('#',1)
                p=TREES[k]/(module+'.lean' if k=='S' else 'KomorebiSpace/'+module+'.lean')
                text=p.read_text();clean=strip_comments(text)
                for name in names.split(','):
                    pat=r'\b(theorem|def|lemma|structure|abbrev)\s+('+re.escape(name)+r')(?![\w.])'
                    matches=list(re.finditer(pat,clean))
                    if len(matches)!=1:
                        missing.append({'id':cid,'module':module,'name':name,'matches':len(matches)})
                        continue
                    m=matches[0];line=clean.count('\n',0,m.start())+1
                    next_decl=re.search(r'\b(theorem|def|lemma|structure|abbrev)\s+',clean[m.end():])
                    end=clean.count('\n',0,m.end()+next_decl.start()) if next_decl else len(clean.splitlines())
                    hist=[h for h in historical.get(k,[]) if h['file'].endswith('/'+module+'.lean') and h['name'].endswith('.'+name)]
                    matches_env=[d for d in envrows if d['module']=='KomorebiSpace.'+module
                                 and (d['name']==name or d['name'].endswith('.'+name))]
                    public=[d for d in matches_env if d['name'].startswith('KomorebiSpace.')]
                    if len(public)==1:matches_env=public
                    if len(matches_env)!=1:
                        missing.append({'id':cid,'module':module,'name':name,'environment_matches':len(matches_env)})
                        continue
                    fullname=matches_env[0]['name']
                    canonical='KomorebiSpace/'+module+'.lean'
                    digest=hashlib.sha256(p.read_bytes()).hexdigest()
                    if current_hashes.get(canonical)!=digest or hashlib.sha256((ROOT/'formal'/canonical).read_bytes()).hexdigest()!=digest:
                        raise RuntimeError('Source correspondence not bound to retained accepted replay: '+canonical)
                    refs.append({'tree':k,'module':module,'declaration':fullname,'lexical_name':name,'kind':m.group(1),
                                 'line_start':line,'line_end_exclusive_upper':end,
                                 'source_path':str(p.relative_to(ROOT)), 'canonical_source_path':'formal/'+canonical,
                                 'baseline_axioms':matches_env[0]['axioms'], 'type':matches_env[0].get('type',''),
                                 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        rows.append({'id':cid,'title':title,'source_refs':refs,'correspondence_note':note,
                     'prose_status':'written_addition' if specs=='W' else 'editorially_aligned_source_statements',
                     'formal_baseline_version':'1.2.0','new_lean_compilation_this_edition':False})
    (ROOT/'audit/concordance_unresolved.json').write_text(json.dumps(missing,indent=2)+'\n')
    if missing:
        print(json.dumps(missing,indent=2));raise SystemExit('Unresolved declaration references. Correct before publishing.')
    (ROOT/'data/claim_ledger.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (ROOT/'data/claim_ledger.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['id','title','source_refs','note','formal_baseline_version','new_lean_compilation_this_edition'])
        for r in rows:w.writerow([r['id'],r['title'],'; '.join(x['tree']+':'+x['module']+'#'+x['declaration'] for x in r['source_refs']),r['correspondence_note'],'1.2.0',False])
    lines=[r'\small',r'\begin{longtable}{@{}p{.09\linewidth}p{.35\linewidth}p{.49\linewidth}@{}}',r'\toprule ID & Topic & Source modules\\\midrule\endhead']
    for r in rows:
        mods=list(dict.fromkeys(x['tree']+': '+x['module'] for x in r['source_refs']))
        moduletex=r'\newline '.join(r'\path{'+s+'}' for s in mods) if mods else 'W: printed proof only'
        lines.append(r'\hypertarget{claim:'+r['id']+'}{'+tex(r['id'])+'}'+' & '+tex(r['title'])+' & '+moduletex+r'\\[3pt]')
    lines.extend([r'\bottomrule\end{longtable}',r'\normalsize'])
    (ROOT/'source/claim_table.tex').write_text('\n'.join(lines)+'\n')
    result={'status':'PASS','claims':len(rows),'references_resolved':sum(len(r['source_refs']) for r in rows),
            'written_only':sum(not r['source_refs'] for r in rows),'formal_baseline_version':'1.2.0','new_lean_compilation_this_edition':False,
            'scope':'Declared names and hashes matched to the retained version 1.2.0 compiler and axiom record. The formal source tree is unchanged; no new compiler run is claimed. Editorial correspondence is not a machine-certified prose translation.'}
    (ROOT/'audit/concordance_result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__': main()
