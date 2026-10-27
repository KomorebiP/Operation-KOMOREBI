#!/usr/bin/env python3
"""Compare retained theorem/proof text and executable predecessors by exact bytes."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'lineage/v0.6.0'
PAT=r'\\begin\{(theorem|proposition)\}\[([^]]+)\]\\label\{([^}]+)\}(.*?)\\end\{\1\}\s*\\begin\{proof\}(.*?)\\end\{proof\}'

def parsed(p):
    return {label:(kind,title,body,proof) for kind,title,label,body,proof in re.findall(PAT,p.read_text(),re.S)}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    before=parsed(OLD/'Self_Improving_Intelligence_v0.6.0.tex')
    after=parsed(ROOT/'Self_Improving_Intelligence_v1.0.0.tex')
    missing=[];changed=[];corrected=[]
    for label,value in before.items():
        if label not in after:missing.append(label);continue
        if value==after[label]:continue
        a=tuple(x.replace('R_{\nm shortcut}',r'R_{\mathrm{shortcut}}') for x in value)
        if label=='prop:compiler-work' and a==after[label]:
            corrected.append({'label':label,'change':'Corrected inherited display subscript R_{newline m shortcut} to R_{\\mathrm{shortcut}}. Formula values, assumptions, and proof unchanged.'})
        else:changed.append(label)
    names=('repair_calculus.py','compiler_improvement.py','check_finite_models.py',
           'check_discovery_models.py','demo.py','demo_discovery.py',
           'synthesized_pruning.py','check_synthesis_models.py','demo_synthesis.py',
           'meta_synthesis.py','weighted_repair_pruning.py','check_meta_models.py','demo_meta.py')
    programs={n:{'same':digest(ROOT/'code'/n)==digest(OLD/'code'/n),
                 'sha256':digest(ROOT/'code'/n)} for n in names}
    result={'status':'PASS' if not missing and not changed and all(x['same'] for x in programs.values()) else 'FAIL',
            'predecessor_pairs':len(before),'current_pairs':len(after),
            'verbatim_pairs':len(before)-len(corrected)-len(changed)-len(missing),
            'notation_only_corrections':corrected,'unapproved_changes':changed,
            'missing':missing,'new_statements':sorted(set(after)-set(before)),
            'core_programs':programs}
    (ROOT/'validation/preservation_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],len(before),'predecessor pairs;',result['verbatim_pairs'],
          'verbatim;',len(corrected),'notation-only correction;',len(names),'unchanged core programs.')
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
