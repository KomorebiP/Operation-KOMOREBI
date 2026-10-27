#!/usr/bin/env python3
"""Read-only publication integrity checks; all output stays in this review folder.

This is a preservation/source-closure check, not a new whole-mathematics audit.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[1]
ROOT = WORK.parent
ACCEPTED = ROOT / 'output/Komorebi_Space_Lean_Continuation_v1.12.0'
BASE = ACCEPTED / 'inherited_v1.11.0/inherited_v1.10.0/source'
FORMAL = ACCEPTED / 'formal'
AXIOMS = ACCEPTED / 'wr15_v1.12.0/integration/runs/clean_wr15_01/axioms.json'
SOURCE = WORK / 'source'
ENV_NAMES = ('theorem', 'lemma', 'proposition', 'corollary', 'definition', 'example', 'proof')
ENV = re.compile(r'\\begin\{(' + '|'.join(ENV_NAMES) + r')\}(.*?)\\end\{\1\}', re.S)
MATH = re.compile(r'\\\((.*?)\\\)|\\\[(.*?)\\\]|(?<!\\)\$(?!\$)(.*?)(?<!\\)\$|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\4\}', re.S)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def strip_comments(s):
    return re.sub(r'(?<!\\)%[^\n]*', '', s)

def envs(s):
    result=[]
    for m in ENV.finditer(strip_comments(s)):
        body=m.group(2)
        labs=re.findall(r'\\label\{([^}]+)\}', body)
        result.append({'environment':m.group(1),'labels':labs,'body':body})
    return result

def math_items(s):
    return [re.sub(r'\s+', '', ''.join(x or '' for x in m.groups() if x not in ('equation','align','gather','multline'))) for m in MATH.finditer(strip_comments(s))]

def source_closure(main):
    visited=set(); missing=[]; graphics=[]
    def visit(p):
        if p in visited: return
        if not p.exists(): missing.append(str(p.relative_to(SOURCE))); return
        visited.add(p)
        s=strip_comments(p.read_text())
        for cmd,arg in re.findall(r'\\(input|include)\{([^}]+)\}',s):
            if '#' in arg: continue
            q=SOURCE/arg
            if not q.suffix: q=q.with_suffix('.tex')
            visit(q)
        for arg in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',s):
            if '#' in arg: continue
            q=SOURCE/arg
            candidates=[q] if q.suffix else [q.with_suffix(e) for e in ('.pdf','.png','.jpg','.eps')]
            graphics.append({'reference':arg,'exists':any(x.exists() for x in candidates)})
        for arg in re.findall(r'\\(?:fixedplate|plate)\{([^}]+)\}',s):
            if '#' not in arg: visit(SOURCE/'figures'/(arg+'.tex'))
    visit(main)
    joined='\n'.join(strip_comments(p.read_text()) for p in sorted(visited))
    labels=re.findall(r'\\label\{([^}]+)\}',joined)
    # The source macro constructs an anchor label without rendering its identifier.
    labels += ['src:'+s for s in re.findall(r'\\source\{([^}]+)\}',joined)]
    refs=[]
    for group in re.findall(r'\\(?:ref|eqref|cref|Cref|pageref|autoref)\*?\{([^}]+)\}',joined):
        refs.extend(group.split(','))
    return {'main':main.name,'files':[str(p.relative_to(SOURCE)) for p in sorted(visited)],
            'missing_inputs':missing,'missing_graphics':[g for g in graphics if not g['exists']],
            'unresolved_literal_refs':sorted(set(r for r in refs if '#' not in r and r not in labels)),
            'duplicate_literal_labels':sorted(set(l for l in labels if '#' not in l and labels.count(l)>1))}

def run(tag):
    all_formal=sorted(FORMAL.rglob('*.lean'))
    production=sorted((FORMAL/'KomorebiSpace').rglob('*.lean'))
    roots=[FORMAL/n for n in ('KomorebiSpace.lean','KomorebiSpaceRegularization.lean','KomorebiSpaceCombined.lean')]
    formal_cmp=[]
    for p in production+roots:
        q=WORK/'lean'/p.relative_to(FORMAL)
        formal_cmp.append({'file':str(p.relative_to(FORMAL)),'accepted_sha256':sha(p),
                           'public_sha256':sha(q) if q.exists() else None,'identical':q.exists() and p.read_bytes()==q.read_bytes()})
    decls=json.loads(AXIOMS.read_text())
    report={'scope':'Publication preservation/source closure only; not a fresh mathematical or Lean compilation audit.',
            'accepted_axioms_sha256':sha(AXIOMS),
            'accepted_export_count':len(decls['declarations']),
            'accepted_unexpected_axioms':decls['unexpected'],
            'production_module_count':len(production),'root_count':len(roots),
            'production_explicit_theorem_lemma_count':0,
            'formal_comparison':formal_cmp,'formal_unchanged':all(x['identical'] for x in formal_cmp),
            'all_lean_file_count_in_accepted':len(all_formal),
            'source_changes':[], 'environment_changes':[], 'closure':[]}
    # Match explicit declarations linewise, excluding Lean comments. This count is corroborative.
    thm=0
    for p in production:
        s=re.sub(r'/\-.*?\-/','',p.read_text(),flags=re.S)
        s=re.sub(r'--[^\n]*','',s)
        thm+=len(re.findall(r'^\s*(?:@\[[^\n]*?\]\s*)*(?:protected\s+|private\s+)?(?:theorem|lemma)\s+',s,re.M))
    report['production_explicit_theorem_lemma_count']=thm
    diff_lines=[]
    for p in sorted(BASE.rglob('*.tex')):
        q=SOURCE/p.relative_to(BASE)
        if not q.exists():
            report['source_changes'].append({'file':str(p.relative_to(BASE)),'status':'missing'})
            continue
        a=p.read_text(); b=q.read_text()
        if a==b: continue
        rel=str(p.relative_to(BASE))
        report['source_changes'].append({'file':rel,'status':'changed','old_sha256':sha(p),'new_sha256':sha(q)})
        diff_lines.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='accepted/'+rel,tofile='public/'+rel))
        ea,eb=envs(a),envs(b)
        for i in range(max(len(ea),len(eb))):
            x=ea[i] if i<len(ea) else None; y=eb[i] if i<len(eb) else None
            if x==y: continue
            item={'file':rel,'index':i,'old':x,'new':y,'math_fragments_unchanged':bool(x and y and math_items(x['body'])==math_items(y['body']))}
            report['environment_changes'].append(item)
    for p in sorted(SOURCE.glob('Komorebi*.tex')):
        report['closure'].append(source_closure(p))
    paths=re.compile(r'\\(?:path|code|texttt|api|leanname)\{([^{}]+)\}')
    refs=[]; names={x['name'] for x in decls['declarations']}
    module_names={x['module'] for x in decls['declarations']}
    for p in sorted(SOURCE.rglob('*.tex')):
        for m in paths.finditer(strip_comments(p.read_text())):
            x=m.group(1).replace(r'\_','_')
            if x.startswith('KomorebiSpace.') and '#' not in x:
                refs.append({'file':str(p.relative_to(SOURCE)),'reference':x,'exact_declaration':x in names,'module':x in module_names,
                             'namespace':any(n.startswith(x.rstrip('.')+'.') for n in names)})
    report['qualified_lean_references']=refs
    report['unresolved_qualified_lean_references']=[x for x in refs if not(x['exact_declaration'] or x['module'] or x['namespace'])]
    out=HERE/(tag+'.json'); out.write_text(json.dumps(report,indent=2)+'\n')
    (HERE/(tag+'.diff')).write_text(''.join(diff_lines))
    print(json.dumps({'output':str(out),'formal_unchanged':report['formal_unchanged'],
        'production_modules':len(production),'roots':len(roots),'explicit_theorems_lemmas':thm,
        'source_change_count':len(report['source_changes']),'changed_environments':len(report['environment_changes']),
        'unresolved_qualified_lean_references':report['unresolved_qualified_lean_references'],
        'closure':[{k:v for k,v in x.items() if k!='files'} for x in report['closure']]},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--tag',default='baseline')
    run(parser.parse_args().tag)
