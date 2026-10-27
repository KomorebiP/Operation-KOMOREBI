#!/usr/bin/env python3
"""Validate current records. This collector does not replace proof/test execution."""
from pathlib import Path
import hashlib,json,re,zipfile,sys,platform,datetime,time
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.29.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check_record(rec,source,output=None):
    assert rec['returncode']==0 and not rec['timed_out'],source
    assert rec['source_unchanged'] and rec['imports_unchanged'],source
    assert rec['source_before_sha256']==rec['source_sha256']==sha(ROOT/source),source
    assert rec['log_sha256']==sha(ROOT/rec['log']),source
    if output:assert rec['output_sha256']==sha(output),source
    expected={}
    for d in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',(ROOT/source).read_text(),re.M):
        p=ROOT/'.lake/build/lib/lean'/Path(d.replace('.','/')).with_suffix('.olean')
        expected[d]=sha(p)
    assert rec['import_outputs']==expected,source

def strip_comments_strings(text):
    out=[];i=0;depth=0;string=False
    while i<len(text):
        if depth:
            if text[i:i+2]=='/-':depth+=1;i+=2
            elif text[i:i+2]=='-/':depth-=1;i+=2
            else:
                if text[i]=='\n':out.append('\n')
                i+=1
        elif string:
            if text[i]=='\\':i+=2
            elif text[i]=='"':string=False;i+=1
            else:i+=1
        elif text[i:i+2]=='/-':depth=1;i+=2
        elif text[i:i+2]=='--':
            j=text.find('\n',i);i=len(text) if j<0 else j
        elif text[i]=='"':string=True;i+=1
        else:out.append(text[i]);i+=1
    return ''.join(out)

def main():
    start=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    order=json.loads((RD/'build_order.json').read_text())
    for f in order:
        rec=json.loads((RD/f'clean_{Path(f).stem}.json').read_text())
        check_record(rec,f,ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean'))
    inv=json.loads((RD/'declaration_inventory.json').read_text());audit=json.loads((RD/'axiom_audit_summary.json').read_text())
    assert audit['passed'] and audit['audited']==len(inv)
    check_record(json.loads((RD/'full_axiom_audit.json').read_text()),'AVOC/FullAudit.lean')
    negatives=sorted((ROOT/'tests/negative').glob('*.lean'))
    for f in negatives:
        rec=json.loads((RD/f'negative_{f.stem}.json').read_text());log=(ROOT/rec['log']).read_text()
        assert rec['returncode']!=0 and not rec['timed_out'] and 'error' in log,f
        assert not re.search(r'object file .*does not exist|unknown module|failed to locate application',log),f
        assert rec['source_sha256']==sha(f) and rec['log_sha256']==sha(ROOT/rec['log']),f
        for d,h in rec['import_outputs'].items():assert sha(ROOT/'.lake/build/lib/lean'/Path(d.replace('.','/')).with_suffix('.olean'))==h
    baseline=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'AVOC_Formal_v0.28.0.zip'
    same=0
    with zipfile.ZipFile(baseline) as z:
        pref='AVOC_Formal_v0.28.0/'
        for n in z.namelist():
            rel=n.removeprefix(pref)
            if rel.startswith('AVOC/') and rel.endswith('.lean') and Path(rel).name not in ['Audit.lean','FullAudit.lean']:
                assert z.read(n)==(ROOT/rel).read_bytes(),rel;same+=1
    modules=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
    bad=[];census=[]
    for p in modules:
        s=strip_comments_strings(p.read_text())
        hits=re.findall(r'\b(?:sorry|native_decide|axiom|unsafe)\b|\bby\s+admit\b|^\s*admit\s*$',s,re.M)
        if hits:bad.append((p.name,hits))
        census.extend(re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',s,re.M))
    assert not bad,bad;assert len(census)==len(inv)
    tests=json.loads((RD/'factor_tests/summary.json').read_text());assert tests['passed']
    assert tests['source_sha256']==sha(ROOT/'checks/test_affine_factorization.py')
    assert tests['generator_sha256']==sha(ROOT/'tools/factor_affine.py')
    for run in tests['runs']:
        assert run['returncode']==0
        ip=Path(run['command'][-1]);op=ip.with_name(ip.name.replace('requests_','output_')).with_suffix('.jsonl')
        assert sha(ip)==run['input_sha256'] and sha(op)==run['output_sha256']
    pins=json.loads((RD/'dependency_pins.json').read_text());assert len(pins)==9 and all(x['passed'] for x in pins)
    summary={'passed':True,'current_compilations':len(order),'theorems':len(inv),'new_theorems':len(json.loads((RD/'new_declarations.json').read_text())),
      'axioms':audit['axioms'],'negative_rejections':len(negatives),'inherited_unchanged':same,'non_audit_modules':len(modules),
      'positive_source_scan_hits':bad,'test_requests':tests['requests'],'test_statuses':tests['statuses'],
      'input_vector_comparisons':tests['vector_comparisons'],'generator_budget_cases':tests['generation_budget_cases'],
      'python_validation_rejections':tests['wrapper_validation_rejections'],'baseline_sha256':sha(baseline),
      'scope':'Fresh local source builds against pinned caches; new exact factorization regression. Older live/runtime suites not rerun.'}
    (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
    manifest={'schema_version':1,'claim_id':'AVOC-v029-minimum-width-factorization-audit',
      'repository':{'commit':'archive:'+sha(baseline),'dirty':True},
      'command':'python tools/summarize_v029.py '+str(baseline),
      'environment':{'software':['Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],'hardware':platform.platform()},
      'mathematics':{'assertion_tested':'Current-source compilation, all theorem axioms and negative records; exact GF(5) factor-certificate execution. Collector timing excludes earlier builds/tests.',
        'coefficient_domain':'Generic Field proofs; GF(5) runtime','conventions':'column vectors; second after first; explicit affine biases; dense tariff; rank proof via U*A*V=I',
        'inputs':['frozen v0.28 archive','four new Lean modules','metered Python RREF generator','independent exact image-span/homogeneous oracle'],
        'bounds':{'theorems':len(inv),'local_targets':len(order),'wire_requests':tests['requests'],'max_runtime_dimension':8,'seed':20260913},
        'non_claims':['No arbitrary affine circuit cost optimum','No formal proof of generator completeness/physical cost','No new mathlib source build','No production LLM benefit']},
      'randomness':{'used':True,'generator':'random.Random for earlier recorded regression','seed':20260913},
      'run':{'started_at':stamp,'runtime_seconds':time.monotonic()-start,'exit_status':0},
      'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [RD/'verification_summary.json',RD/'source_counts.json',RD/'axiom_audit_summary.json',RD/'factor_tests/summary.json']],
      'checks':['current source/import/output/log hashes','complete axiom census','substantive negative errors','unchanged baseline Lean sources','finite exact differential regression'],
      'result':'PASS in the specified proof and execution scopes',
      'residual_risks':['compiler/kernel and exact dependency caches','Python generator, parser, filesystem and host','declared tariffs not all physical work','v1 metadata format not a proof of interpretation']}
    (RD/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
