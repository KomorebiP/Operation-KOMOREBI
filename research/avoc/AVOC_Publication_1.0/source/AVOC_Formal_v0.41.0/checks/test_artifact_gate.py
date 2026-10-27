#!/usr/bin/env python3
"""Exact differential, semantic, binding and real-file mutation tests.
Bounded evidence, not a substitute for the Lean soundness theorems.
"""
from __future__ import annotations
import copy, hashlib, itertools, json, os, subprocess, sys, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from artifact_gate import ArtifactGate, LeanChecker, GateError, parse_target, encode, strict_json, wire_ticket, wire_identity
RD=ROOT/'results/v0.16.0';RD.mkdir(parents=True,exist_ok=True)

def infer(ctx,p):
    tag=p[0]
    if tag=='hyp': return p[1] if p[1] in ctx else None
    if tag=='true': return ['true']
    if tag=='pair':
        f,g=infer(ctx,p[1]),infer(ctx,p[2]);return None if f is None or g is None else ['and',f,g]
    if tag in ('fst','snd'):
        f=infer(ctx,p[1]);return f[1 if tag=='fst' else 2] if f and f[0]=='and' else None
    if tag=='intro':
        g=infer([p[1]]+ctx,p[2]);return None if g is None else ['imp',p[1],g]
    if tag=='mp':
        f,g=infer(ctx,p[1]),infer(ctx,p[2]);return f[2] if f and f[0]=='imp' and g==f[1] else None
    if tag in ('left','right'):
        f=infer(ctx,p[2]);return None if f is None else ['or',f,p[1]] if tag=='left' else ['or',p[1],f]
    if tag=='cases':
        f=infer(ctx,p[1])
        if not f or f[0]!='or':return None
        g,h=infer([f[1]]+ctx,p[2]),infer([f[2]]+ctx,p[3]);return g if g is not None and g==h else None
    if tag=='absurd':return p[1] if infer(ctx,p[2])==['false'] else None
    raise AssertionError(tag)

def truth(f,valuation):
    if f[0]=='atom':return valuation[f[1]]
    if f[0]=='true':return True
    if f[0]=='false':return False
    x,y=truth(f[1],valuation),truth(f[2],valuation)
    return (x and y) if f[0]=='and' else (x or y) if f[0]=='or' else ((not x) or y)

def batch(checker,payloads,expected):
    records=[]
    with tempfile.TemporaryDirectory(prefix='avoc_differential_') as d:
        path=Path(d)/'batch.json'
        for start in range(0,len(payloads),300):
            raw=encode(payloads[start:start+300]);path.write_text(raw)
            assert len(raw.encode())<=1048576
            env=os.environ.copy();env['LEAN_PATH']=str(ROOT/'.lake/build/lib/lean')
            cmd=[str(checker.lean),'-j1','-DwarningAsError=true','--run',str(ROOT/'tools/CertificateBatch.lean'),str(path)]
            t=time.monotonic();p=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
            assert p.returncode==0,(p.stdout,p.stderr)
            result=json.loads(p.stdout)
            if result != expected[start:start+300]:
                differences=[dict(index=start+i,actual=x,expected=y,payload=payloads[start+i]) for i,(x,y) in enumerate(zip(result,expected[start:start+300])) if x!=y]
                (RD/'differential_failure.json').write_text(json.dumps(differences,indent=2)+'\n')
                raise AssertionError(differences[:3])
            records.append(dict(start=start,count=len(result),seconds=round(time.monotonic()-t,4),returncode=p.returncode,
                                input_sha256=hashlib.sha256(raw.encode()).hexdigest(),output_sha256=hashlib.sha256(p.stdout.encode()).hexdigest()))
    return records

def main():
    checker=LeanChecker();records=[];cases=[]
    a,b=['atom',0],['atom',1]
    formulas=[a,b,['true'],['false'],['and',a,b],['or',a,b],['imp',a,b]]
    base=[['true']]+[['hyp',f] for f in formulas]
    proofs=copy.deepcopy(base)
    for p in base:
        proofs += [['fst',p],['snd',p],['intro',a,p],['intro',b,p],['left',a,p],['right',a,p],['absurd',b,p]]
    for p,q in itertools.product(base,repeat=2):proofs += [['pair',p,q],['mp',p,q]]
    proofs += [strict_json((ROOT/'examples/artifact_gate/swap.proof.json').read_text()),
               ['intro',['or',a,b],['cases',['hyp',['or',a,b]],['right',b,['hyp',a]],['left',a,['hyp',b]]]]]
    contexts=[[],[a],[b],[a,b],[['imp',a,b],a],[['and',a,b]],[['or',a,b]],[['false']]]
    payloads=[];expected=[];semantic=0
    for ctx,p in itertools.product(contexts,proofs):
        f=infer(ctx,p)
        for target in ([f] if f is not None else [])+formulas[:4]:
            ok=f==target;payloads.append([target,ctx,p]);expected.append(ok)
            if ok:
                for valuation in itertools.product([False,True],repeat=2):
                    assert not all(truth(g,valuation) for g in ctx) or truth(target,valuation)
                    semantic+=1
    records+=batch(checker,payloads,expected)
    bpayload=[];bexpected=[]
    ident=['demo',['imp',a,a],'EXACT TARGET',[],[['environment','E1']]]
    art=[ident,encode(['intro',a,['hyp',a]])];ticket=[0,art]
    baseq=['bound',ident,[1,ticket],[ticket,True]]
    bpayload.append(baseq);bexpected.append(True)
    for approved,generation,env,target,source in itertools.product([True,False],[0,1],['E1','E2'],[a,b],['',' ']):
        q=json.loads(encode(baseq));q[3][1]=approved;q[3][0][0]=generation
        q[1][4][0][1]=env;q[1][1]=['imp',target,target]
        q[3][0][1][1]+=source
        bpayload.append(q);bexpected.append(approved and generation==0 and env=='E1' and target==a and source=='')
    q=json.loads(encode(baseq));q[2][1]=None;bpayload.append(q);bexpected.append(False)
    q=json.loads(encode(baseq));q[1][3]=[['d',['true'],'bytes']];bpayload.append(q);bexpected.append(False)
    records+=batch(checker,bpayload,bexpected)
    def failure(name,fn):
        try:fn()
        except (GateError,ValueError) as e:cases.append({'name':name,'result':'REJECTED','reason':str(e)});return
        raise AssertionError('accepted invalid case '+name)
    with tempfile.TemporaryDirectory(prefix='avoc_artifact_files_') as d:
        d=Path(d);gate=ArtifactGate(d/'store',checker)
        tp=d/'target.json';cp=d/'proof.json'
        target={'schema':'avoc-proposition-1','task':'identity','statement':['imp',a,a],'dependencies':[]}
        proof=['intro',a,['hyp',a]]
        def put(t=target,p=proof):tp.write_text(encode(t));cp.write_text(encode(p))
        put();ticket=gate.register(tp,cp);assert not gate.load()['admitted']
        receipt=gate.verify();assert not gate.load()['admitted']
        rec=gate.admit(receipt);assert 'identity' in gate.load()['admitted'];cases.append({'name':'real_root_admission','result':'ACCEPTED'})
        failure('receipt_replay',lambda:gate.admit(receipt))
        put();gate.register(tp,cp);old=gate.verify();gate.register(tp,cp)
        failure('old_generation_same_bytes',lambda:gate.admit(old))
        receipt=gate.verify();cp.write_text(cp.read_text()+' ')
        failure('candidate_byte_change_same_syntax',lambda:gate.admit(receipt))
        put();gate.register(tp,cp);receipt=gate.verify()
        real_request=checker.request
        changed=[False]
        def change_during_check(payload):
            result=real_request(payload)
            if not changed[0]:
                changed[0]=True;cp.write_text(cp.read_text()+' ')
            return result
        checker.request=change_during_check
        try:failure('candidate_changed_during_admission',lambda:gate.admit(receipt))
        finally:checker.request=real_request
        put();gate.register(tp,cp);receipt=gate.verify();tp.write_text(tp.read_text()+' ')
        failure('target_byte_change_same_syntax',lambda:gate.admit(receipt))
        put();gate.register(tp,cp);receipt=gate.verify();forged=copy.deepcopy(receipt);forged['subject']['target_bytes']=encode({**target,'task':'other'})
        failure('substituted_task',lambda:gate.admit(forged))
        forged=copy.deepcopy(receipt);forged['approved']=False
        failure('explicit_rejection',lambda:gate.admit(forged))
        source=ROOT/'tools/CertificateMain.lean';original=source.read_bytes()
        try:
            source.write_bytes(original+b'\n-- controlled stale-environment regression\n')
            failure('changed_checker_environment',lambda:gate.admit(receipt))
        finally:source.write_bytes(original)
        put({**target,'task':'false-task','statement':['false']},['true'])
        t=gate.register(tp,cp)
        failure('forged_approval_of_false_proof',lambda:gate.admit({'schema':'avoc-receipt-1','subject':t,'approved':True}))
        failure('invalid_proof_at_verification',gate.verify)
        pairtarget={'schema':'avoc-proposition-1','task':'pair','statement':['and',['imp',a,a],['imp',a,a]],'dependencies':['identity']}
        pairproof=['pair',['hyp',['imp',a,a]],['hyp',['imp',a,a]]]
        put(pairtarget,pairproof);gate.register(tp,cp);r=gate.verify();gate.admit(r)
        cases.append({'name':'real_dependency_chain_admission','result':'ACCEPTED'})
        put(pairtarget,pairproof);gate.register(tp,cp);r=gate.verify();state=gate.load()
        state['admitted']['identity']['ticket']['candidate_bytes']+=' '
        gate.save(state)
        failure('changed_dependency_snapshot',lambda:gate.admit(r))
        state=gate.load();state['admitted']['identity']['ticket']['candidate_bytes']=encode(['true']);gate.save(state)
        put(pairtarget,pairproof);gate.register(tp,cp)
        failure('forged_dependency_record',gate.verify)
        put({**target,'dependencies':['missing']})
        failure('missing_dependency',lambda:gate.register(tp,cp))
        put({**target,'dependencies':['identity']})
        failure('self_dependency',lambda:gate.register(tp,cp))
        put();cp.write_text(encode(['run_tac','IO.println("forged")']))
        failure('arbitrary_code_not_a_constructor',lambda:gate.register(tp,cp))
        put();tp.write_text('{"schema":"avoc-proposition-1","schema":"other"}')
        failure('duplicate_json_keys',lambda:gate.register(tp,cp))
        failure('invalid_atom',lambda:parse_target(encode({**target,'statement':['atom',-1]})))
        put();(gate.store/'LOCK').write_text('held')
        try:failure('concurrent_store_mutation',lambda:gate.register(tp,cp))
        finally:(gate.store/'LOCK').unlink()
        put();link=d/'linked.json';link.symlink_to(cp)
        failure('symlink_candidate',lambda:gate.register(tp,link))
    source_paths=['checks/test_artifact_gate.py','tools/artifact_gate.py','tools/CertificateMain.lean','tools/CertificateBatch.lean',
                  'AVOC/CertificateLogic.lean','AVOC/CertificateCodec.lean','AVOC/BindingCodec.lean','AVOC/ArtifactBinding.lean']
    summary={'status':'PASS','counts':{'logic_comparisons':len(payloads),'truth_table_implications':semantic,
                                      'binding_comparisons':len(bpayload),'file_workflow_cases':len(cases),
                                      'file_rejections':sum(x['result']=='REJECTED' for x in cases),
                                      'real_checker_calls':len(checker.records)},
             'source_hashes':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in source_paths},
             'scope':'Finite data-only propositional certificates; Python filesystem orchestration is not formally extracted.',
             'file_cases':cases,'batch_records':records,'checker_records':checker.records}
    (RD/'artifact_gate_regression.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary['counts'],indent=2));print('PASS')

if __name__=='__main__':main()
