#!/usr/bin/env python3
"""Read-only evidence replay; does not replace a fresh Lean build."""
from pathlib import Path
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
from run_command import snapshot
ALLOWED={'propext','Quot.sound','Classical.choice'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse_declared_axioms(text):
    """Bracket-delimited records: wrapping is allowed, empty lists stop immediately."""
    records={}
    pattern=r"(?m)^'([^'\n]+)' depends on axioms: \[([^\[\]]*)\]$|^'([^'\n]+)' does not depend on any axioms$"
    for match in re.finditer(pattern,text):
        name=match.group(1) or match.group(3)
        if name in records:raise ValueError('duplicate declaration '+name)
        body=match.group(2)
        axs=set(x.strip() for x in body.split(',') if x.strip()) if body is not None else set()
        if any(not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]*',a) for a in axs):
            raise ValueError('malformed axiom list '+name)
        records[name]=axs
    return records

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--unsealed',action='store_true');args=ap.parse_args()
    errors=[];checks=0
    def ck(ok,msg):
        nonlocal checks
        checks+=1
        if not ok:errors.append(msg)
    inv=json.loads((ROOT/'verification/theorem_inventory.json').read_text());now=snapshot()
    for row in json.loads((ROOT/'verification/final_plan.json').read_text()):
        recpath=ROOT/'results'/f"{row['label']}.json";logpath=ROOT/'results'/f"{row['label']}.log"
        ck(recpath.is_file() and logpath.is_file(),'missing phase '+row['label'])
        if not (recpath.is_file() and logpath.is_file()):continue
        rec=json.loads(recpath.read_text());log=logpath.read_text()
        ck(rec['exit_status']==row['exit'],'exit '+row['label'])
        ck(rec['inputs_unchanged'] and rec['inputs_before']==rec['inputs_after']==now,'source snapshot '+row['label'])
        ck(rec['log_sha256']==sha(logpath),'log hash '+row['label'])
        if 'diagnostic' in row:ck(row['diagnostic'] in log,'negative diagnostic '+row['label'])
    old=json.loads((ROOT/'PREDECESSOR_SOURCE_HASHES.json').read_text())
    for path,h in old.items():
        q=ROOT/path
        if path=='lean/KomorebiPadic.lean':
            data=q.read_bytes();prefix=b'import KomorebiPadic.PresentationExamples\n'
            ck(data.startswith(prefix) and hashlib.sha256(data[len(prefix):]).hexdigest()==h,'root import extension')
        else:ck(q.is_file() and sha(q)==h,'inherited source '+path)
    ck(sha(ROOT/'predecessor/Block31_Checked.zip')==json.loads((ROOT/'PREDECESSOR_ARCHIVE.json').read_text())['sha256'],'predecessor exact ZIP')
    declarations={};axiom_free=0;observed=set()
    p=ROOT/'results/final_declared_axioms.log'
    if p.exists():
        for name, axs in parse_declared_axioms(p.read_text()).items():
            declarations[name]=axs
            observed |= axs; axiom_free += not axs
            ck(axs<=ALLOWED,'unexpected axioms '+name+' '+str(axs-ALLOWED))
    ck(set(declarations)==set(inv['names']),'all source theorem axiom coverage')
    kernel_names={};kernel_axioms={}
    for path,prefix,store in [('final_kernel_inventory.log','PROJECT_THEOREM',kernel_names),('final_kernel_axioms.log','PROJECT_AXIOMS',kernel_axioms)]:
        f=ROOT/'results'/path
        if not f.exists():continue
        for line in f.read_text().splitlines():
            if not line.startswith(prefix+' '):continue
            if prefix=='PROJECT_THEOREM':
                fields=line.split();name=fields[1];val=fields[2]
            else:
                fields=line[len(prefix)+1:].split('|');name=fields[0].strip();val=set(x.strip() for x in fields[2].split(',') if x.strip())
                ck(val<=ALLOWED,'kernel unexpected axioms '+name+' '+str(val-ALLOWED))
            ck(name not in store,'duplicate kernel record '+name);store[name]=val
    ck(set(kernel_names)==set(kernel_axioms),'complete kernel theorem coverage')
    ck(set(inv['names'])<=set(kernel_names),'source declarations present in kernel inventory')
    modules=list((ROOT/'lean').rglob('*.lean'))
    for q in modules:
        source=re.sub(r'/\-.*?\-/','',q.read_text(),flags=re.S);source=re.sub(r'--[^\n]*','',source)
        ck(not re.search(r'\b(sorry|admit|native_decide)\b|(?m:^\s*(?:axiom|unsafe)\b)',source),'forbidden production construct '+q.name)
    n_olean=len(list((ROOT/'compiled').rglob('*.olean')));n_ilean=len(list((ROOT/'compiled').rglob('*.ilean')))
    ck(n_olean==len(modules)==n_ilean,'compiled artifact counts')
    audit=json.loads((ROOT/'results/audit_presentation.json').read_text())
    ck(audit['status']=='PASS' and not audit['failures'],'exact audit status')
    ck(audit['generic_systems']==168 and audit['mask_cases']==49,'audit domain completeness')
    ck(audit['assertions']==sum(audit['counts'].values()),'audit accounting')
    if not args.unsealed:
        ledger=ROOT/'CHECKSUMS.sha256';ck(ledger.is_file(),'checksum ledger missing')
        if ledger.exists():
            for line in ledger.read_text().splitlines():
                h,path=line.split('  ',1);q=ROOT/path
                ck(q.is_file() and sha(q)==h,'checksum '+path)
    result={'status':'PASS' if not errors else 'FAIL','checks':checks,'errors':errors,'source_theorems':len(declarations),
        'new_theorems':inv['new'],'kernel_theorem_constants':len(kernel_names),'axiom_free_source_theorems':axiom_free,
        'observed_axioms':sorted(observed),'modules':len(modules),'compiled_olean':n_olean,'compiled_ilean':n_ilean,
        'scope':'read-only retained evidence and hash replay, not a fresh compiler run'}
    print(json.dumps(result,indent=2));return bool(errors)
if __name__=='__main__':sys.exit(main())
