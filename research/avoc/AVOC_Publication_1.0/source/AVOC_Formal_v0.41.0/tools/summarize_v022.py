#!/usr/bin/env python3
"""Validate current proof/runtime evidence. No historical log is treated as fresh."""
from pathlib import Path
import argparse,hashlib,json,re,zipfile,sys
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.22.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def require(x,msg):
    if not x:raise RuntimeError(msg)
def record_ok(path,output=None):
    r=read(path);source=Path(r['command'][-1])
    if not source.is_absolute():source=ROOT/source
    require(r['returncode']==0 and not r['timed_out'],str(path)+' not successful')
    require(r['source_sha256']==sha(source) and r.get('source_unchanged'),str(path)+' source changed')
    require(r['log_sha256']==sha(ROOT/r['log']),str(path)+' log changed')
    if output:require(output.is_file() and r['output_sha256']==sha(output),str(path)+' output changed')
    return r

def without_comments(s):
    out=[];i=0;depth=0
    while i<len(s):
        if depth:
            if s[i:i+2]=='/-':depth+=1;i+=2
            elif s[i:i+2]=='-/':depth-=1;i+=2
            else:
                out.append('\n' if s[i]=='\n' else ' ');i+=1
        elif s[i:i+2]=='/-':depth=1;i+=2
        elif s[i:i+2]=='--':
            e=s.find('\n',i);i=len(s) if e<0 else e
        elif s[i]=='"':
            out.append(' ');i+=1
            while i<len(s):
                if s[i]=='\\':i+=2
                elif s[i]=='"':i+=1;break
                else:i+=1
        else:out.append(s[i]);i+=1
    return ''.join(out)

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);a=p.parse_args()
    order=read(RD/'build_order.json');build=[]
    for f in order:
        build.append(record_ok(RD/f'clean_{Path(f).stem}.json',ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean')))
    audit=record_ok(RD/'full_axiom_audit.json')
    text=(RD/'full_axiom_audit.log').read_text()
    names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
    inventory=read(RD/'declaration_inventory.json')
    require(set(names)=={x['qualified_name'] for x in inventory} and len(names)==len(inventory),'axiom name mismatch')
    axioms=set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):axioms.update(x.strip() for x in block.split(',') if x.strip())
    require(axioms<={'propext','Classical.choice','Quot.sound'},'unapproved axiom')
    neg=[]
    for f in sorted((ROOT/'tests/negative').glob('*.lean')):
        r=read(RD/f'negative_{f.stem}.json');log=ROOT/r['log'];t=log.read_text()
        require(r['returncode']!=0 and not r['timed_out'],'negative not rejected: '+f.name)
        require(r['source_sha256']==sha(f) and r['log_sha256']==sha(log),'negative hashes changed: '+f.name)
        require(not re.search(r'object file .*does not exist|unknown module|failed to locate application',t),'negative setup failure: '+f.name)
        require('error' in t,'negative has no substantive diagnostic: '+f.name)
        neg.append(dict(file=str(f.relative_to(ROOT)),returncode=r['returncode'],source_sha256=sha(f),log_sha256=sha(log)))
    inherited=[]
    with zipfile.ZipFile(a.baseline) as z:
        for n in z.namelist():
            if re.match(r'[^/]+/AVOC/[^/]+\.lean$',n) and Path(n).name not in ['FullAudit.lean','Audit.lean']:
                rel='/'.join(n.split('/')[1:]);require((ROOT/rel).read_bytes()==z.read(n),'changed inherited source: '+rel);inherited.append(rel)
    forbidden=[]
    for f in (ROOT/'AVOC').glob('*.lean'):
        if f.name in ['Audit.lean','FullAudit.lean']:continue
        s=without_comments(f.read_text())
        for pat in [r'\bsorry\b',r'\bnative_decide\b',r'(?m)^\s*(?:unsafe\s+|axiom\s+)',r'(?m)^\s*admit\s*$',r':=\s*admit\b']:
            if re.search(pat,s):forbidden.append((str(f.relative_to(ROOT)),pat))
    require(not forbidden,'forbidden shortcuts: '+repr(forbidden))
    regression=read(RD/'advisor_regression.json')
    require(regression['passed'],'regression failed')
    require(regression['source_sha256']==sha(ROOT/'checks/test_retry_advisor.py'),'regression source changed')
    require(regression['requests_sha256']==sha(RD/'advisor_requests.jsonl') and regression['results_sha256']==sha(RD/'advisor_results.jsonl'),'regression data changed')
    runtime=read(RD/'advisor_execution_records.json')
    for r in runtime:
        require(r['returncode']==0 and r['main_sha256']==sha(ROOT/'tools/RetryDecisionMain.lean') and r['codec_sha256']==sha(ROOT/'AVOC/RetryDecisionCodec.lean'),'runtime record mismatch')
    pins=read(RD/'dependency_pins.json');require(all(p['passed'] for p in pins),'pin mismatch')
    summary=dict(passed=True,local_targets=len(build),theorems=len(inventory),new_theorems=len(read(RD/'new_declarations.json')),
        axiom_reports=len(names),axioms=sorted(axioms),negative_rejections=len(neg),inherited_modules_unchanged=len(inherited),
        baseline_sha256=sha(a.baseline),source_scan_hits=forbidden,dependency_pins=len(pins),regression=regression,
        scope='fresh local-source build, pinned external cache retained; inherited live filesystem/crash suites not rerun in this block')
    (RD/'negative_final.json').write_text(json.dumps(neg,indent=2)+'\n')
    (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
