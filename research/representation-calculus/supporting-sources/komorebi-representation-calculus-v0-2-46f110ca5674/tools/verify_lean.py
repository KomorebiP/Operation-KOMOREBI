"""Cold-check all project Lean sources and audit explicit named declarations."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,platform,re,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
ORDER=['RepresentationCore','FiniteCertificates','InvariantCertificates','ConcreteExamples','GeneratedProfile']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def declarations():
    rows=[]
    for module in ORDER:
        ns=''
        for line in (ROOT/f'formalization/{module}.lean').read_text().splitlines():
            mt=re.match(r'^namespace\s+(\S+)',line)
            if mt:ns=mt.group(1)
            mt=re.match(r'^(?:noncomputable\s+)?(def|abbrev|theorem|structure)\s+([^\s{(:]+)',line)
            if mt:rows.append({'name':ns+'.'+mt.group(2),'kind':mt.group(1),'module':module})
    return rows

def main():
    pa=argparse.ArgumentParser();pa.add_argument('--lean',required=True);args=pa.parse_args()
    lean=str(Path(args.lean).resolve())
    if not Path(lean).is_file():raise SystemExit('Lean executable not found')
    version=subprocess.run([lean,'--version'],capture_output=True,text=True,check=True).stdout.strip()
    if '4.34.0-rc2' not in version:raise SystemExit('this release is pinned to Lean 4.34.0-rc2')
    names=declarations();inputs=[f'formalization/{n}.lean' for n in ORDER]+['tools/verify_lean.py']
    before={n:sha(ROOT/n) for n in inputs};tasks=[];started=datetime.now(timezone.utc).isoformat();tick=time.monotonic()
    logs=ROOT/'evidence/lean';logs.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='komorebi-repr-lean-') as temp:
      td=Path(temp);env=os.environ.copy();env['LEAN_PATH']=temp
      def call(label,argv,expect):
        now=time.monotonic()
        p=subprocess.run(argv,cwd=ROOT/'formalization',env=env,text=True,capture_output=True,timeout=45)
        text=p.stdout+p.stderr;(logs/f'{label}.log').write_text(text)
        ok=(p.returncode==0) if expect=='accept' else (p.returncode!=0)
        tasks.append({'name':label,'argv':[x.replace(temp,'<fresh-build>') for x in argv],'exit_status':p.returncode,'expected':expect,'passed':ok,'seconds':time.monotonic()-now})
        if not ok:raise RuntimeError(label+' did not have expected outcome: '+text)
        return text
      for module in ORDER:
        call('build_'+module,[lean,'-DwarningAsError=true','-o',str(td/(module+'.olean')),module+'.lean'],'accept')
      audit=td/'Audit.lean';audit.write_text('import GeneratedProfile\n'+'\n'.join('#print axioms '+row['name'] for row in names)+'\n')
      text=call('axioms',[lean,str(audit)],'accept')
      used=set()
      for match in re.finditer(r'depends on axioms:?\s*\[([^\]]*)\]',text):
        used.update(x.strip() for x in match.group(1).split(',') if x.strip())
      for row in names:
        if row['name'] not in text:raise RuntimeError('missing axiom record for '+row['name'])
      if used-{'propext','Classical.choice','Quot.sound'}:raise RuntimeError('unexpected axioms '+str(used))
      for token in ('sorryAx','Lean.ofReduceBool'):
        if token in text:raise RuntimeError('forbidden trust dependency '+token)
      pos=td/'Positive.lean';pos.write_text('import GeneratedProfile\n#check Komorebi.Representation.Generated.all_words\n')
      call('positive',[lean,'-DwarningAsError=true',str(pos)],'accept')
      neg=td/'False.lean';neg.write_text('import Std\nexample : (0 : Nat) = 1 := by decide\n')
      call('false_control',[lean,'-DwarningAsError=true',str(neg)],'reject')
      gap=td/'Placeholder.lean';gap.write_text('import Std\nexample : False := by sorry\n')
      call('placeholder_control',[lean,'-DwarningAsError=true',str(gap)],'reject')
    after={n:sha(ROOT/n) for n in inputs}
    if before!=after:raise RuntimeError('accepted inputs changed during verification')
    counts={k:sum(r['kind']==k for r in names) for k in ('theorem','def','abbrev','structure')}
    result={'status':'PASS','toolchain':version,'library_modules':len(ORDER),'explicit_declarations':len(names),
            'counts':counts,'axioms':sorted(used),'tasks':tasks,'inputs_unchanged':True,
            'runtime_seconds':time.monotonic()-tick,'boundaries':['No Mathlib imports or reuse of p-adic theorem endpoints in this branch.',
            'Generic unary observational semantics is formalized; new chain-ring matrix certificate adapter and numeric linear minimum proof are written, not formally connected here.',
            'Concrete exported finite-table system has kernel-checked all-word exact quotient and competitor-embedding proofs.',
            'Python parser, discoverer, Smith routine and exporter are not verified executable programs.']}
    (ROOT/'results/LEAN_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'evidence/DECLARATIONS.json').write_text(json.dumps(names,indent=2)+'\n')
    outputs=['results/LEAN_AUDIT.json','evidence/DECLARATIONS.json']+[str(p.relative_to(ROOT)) for p in sorted(logs.glob('*.log'))]
    manifest={'schema_version':2,'claim_id':'KRC-0.2-LEAN-SEMANTICS','repository':{'commit':'unavailable: standalone branch','dirty':True},
      'command':[sys.executable,'tools/verify_lean.py','--lean',lean],
      'environment':{'software':[{'name':'Lean','version':version},{'name':'Python','version':sys.version}], 'platform':platform.platform()},
      'mathematics':{'assertion_tested':'Generic exact observational quotient, transport and invariant-certificate soundness; explicit finite profiles and one automatically exported all-word exact quotient.',
        'coefficient_domain':'Arbitrary typed deterministic unary systems, including finite examples. Source and target observations share a type.',
        'conventions':'Words read left-to-right. All initial states admissible. Local checks and generated witnesses are kernel-evaluated by decide; no native_decide.',
        'inputs':inputs,'bounds':{'modules':5,'per_task_wall_seconds':45},'non_claims':result['boundaries']},
      'randomness':{'used':False,'seed':None,'generator':'none'},
      'run':{'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':result['runtime_seconds'],
        'exit_status':0,'status':'completed','wall_cap_seconds':45*9,
        'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},'missing_results':[],'invalid_results':[]},
      'input_artifacts':[{'path':n,'sha256':before[n],'sha256_after':after[n]} for n in inputs],
      'execution_artifacts':inputs,'declared_results':['results/LEAN_AUDIT.json','evidence/DECLARATIONS.json'],
      'outputs':[{'path':n,'sha256':sha(ROOT/n),'kind':'result' if n.startswith('results/') or n.endswith('.json') else 'log'} for n in outputs],
      'checks':[{'name':x['name'],'status':'PASS'} for x in tasks],
      'result':'kernel accepted declared sources; expected negative controls rejected',
      'residual_risks':result['boundaries']+['Proof interpretation self-review only; kernel/runtime trust remains.']}
    (ROOT/'LEAN_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='tasks'},indent=2))
if __name__=='__main__':main()
