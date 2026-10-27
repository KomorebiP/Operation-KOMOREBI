#!/usr/bin/env python3
"""Regenerate source inventories; this is a textual audit, not Lean elaboration."""
from __future__ import annotations
import argparse, collections, csv, hashlib, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parent / 'formal'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def mask_lean(text):
    out = list(text); i = 0; depth = 0; string = False
    while i < len(text):
        if depth:
            if text[i:i+2] == '/-':
                out[i:i+2] = '  '; depth += 1; i += 2; continue
            if text[i:i+2] == '-/':
                out[i:i+2] = '  '; depth -= 1; i += 2; continue
            if text[i] != '\n': out[i] = ' '
            i += 1; continue
        if string:
            if text[i] == '\\':
                out[i] = ' '; i += 1
                if i < len(text) and text[i] != '\n': out[i] = ' '
                i += 1; continue
            if text[i] == '"': string = False
            if text[i] != '\n': out[i] = ' '
            i += 1; continue
        if text[i:i+2] == '/-':
            out[i:i+2] = '  '; depth = 1; i += 2; continue
        if text[i:i+2] == '--':
            j = text.find('\n', i)
            if j < 0: j = len(text)
            out[i:j] = ' ' * (j-i); i = j; continue
        if text[i] == '"': out[i] = ' '; string = True
        i += 1
    if depth or string: raise ValueError('Unclosed Lean comment or string')
    return ''.join(out)

def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def build(source):
    source = source.resolve()
    root_imports = re.findall(r'^import Komorebi\.SufficientResolution\.(\w+)',
                             (source/'Komorebi.lean').read_text(), re.M)
    block_ends = [6,11,16,22,30,35,41,47,53,60,65,70,75,81,87,93]
    blocks = {name:next(i+1 for i,end in enumerate(block_ends) if j<end)
              for j,name in enumerate(root_imports)}
    files = sorted((source/'Komorebi'/'SufficientResolution').glob('*.lean'))
    assert len(files)==93 and len(root_imports)==93 and len(set(root_imports))==93
    declarations = []; modules = []
    for f in files:
        text=f.read_text(); masked=mask_lean(text); lines=masked.splitlines()
        rawlines=text.splitlines(); scopes=[]; local=[]
        for n,line in enumerate(lines,1):
            s=line.strip()
            m=re.match(r'namespace\s+(\S+)',s)
            if m: scopes.append(('namespace',m.group(1))); continue
            m=re.match(r'(?:noncomputable\s+)?section(?:\s+(\S+))?\s*$',s)
            if m: scopes.append(('section',m.group(1))); continue
            if re.match(r'end(?:\s|$)',s):
                if scopes: scopes.pop()
                continue
            m=re.match(r'(?:@\[[^\]]*\]\s*)?(theorem|lemma|def|abbrev|structure)\s+(\w+)',s)
            if not m: continue
            name='.'.join([value for kind,value in scopes if kind=='namespace']+[m.group(2)])
            row={'name':name,'kind':m.group(1),'module':f.stem,'block':blocks[f.stem],
                 'file':f.relative_to(source).as_posix(),'line':n,
                 'declaration_start':rawlines[n-1].strip(),'source_sha256':sha(f)}
            declarations.append(row); local.append(row)
        counts=collections.Counter(r['kind'] for r in local)
        imports=re.findall(r'^import\s+(\S+)',masked,re.M)
        modules.append({'module':f.stem,'block':blocks[f.stem],
            'file':f.relative_to(source).as_posix(),'lines':len(rawlines),'bytes':f.stat().st_size,
            'theorem_lemma_count':counts['theorem']+counts['lemma'],
            'definition_count':counts['def'],'abbreviation_count':counts['abbrev'],
            'structure_count':counts['structure'],'named_declaration_count':len(local),
            'local_imports':';'.join(x for x in imports if x.startswith('Komorebi.')),
            'external_imports':';'.join(x for x in imports if not x.startswith('Komorebi.')),
            'sha256':sha(f)})
    counts=collections.Counter(r['kind'] for r in declarations)
    assert len(declarations)==1159 and counts=={'theorem':998,'def':144,'abbrev':9,'structure':8}
    assert len(set(x['name'] for x in declarations))==1159
    inherited=list(csv.DictReader((source/'DECLARATION_INDEX_v0.16.0.csv').open()))
    expected={(x['name'],x['kind'],x['file']) for x in inherited}
    actual={(x['name'],x['kind'],x['file']) for x in declarations}
    assert expected==actual, (expected-actual,actual-expected)
    guide_hashes={('THEOREM_GUIDE.md' if b==1 else f'BLOCK_{b:02d}_THEOREMS.md'):
                  sha(source/('THEOREM_GUIDE.md' if b==1 else f'BLOCK_{b:02d}_THEOREMS.md'))
                  for b in range(1,17)}
    summary={'edition':'2026-10-06','inventory_method':'Comment/string-masked textual namespace and declaration scan; no Lean elaboration',
      'modules':93,'named_declarations':1159,'kinds':dict(counts),'matches_inherited_index':True,
      'inventoried_root':'formal/Komorebi/SufficientResolution','guide_input_hashes':guide_hashes,
      'block_counts':[{'block':b,'modules':sum(x['block']==b for x in modules),
         'theorem_lemma':sum(x['kind'] in ('theorem','lemma') and x['block']==b for x in declarations),
         'named_declarations':sum(x['block']==b for x in declarations)} for b in range(1,17)]}
    for name,rows in [('Declaration_Inventory',declarations),('Module_Inventory',modules)]:
        write_csv(HERE/(name+'.csv'),rows,list(rows[0]));
        (HERE/(name+'.json')).write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
    (HERE/'INVENTORY_AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('modules','named_declarations','kinds','matches_inherited_index')}))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=pathlib.Path,default=DEFAULT_SOURCE)
    build(ap.parse_args().source)
