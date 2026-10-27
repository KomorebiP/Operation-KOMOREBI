#!/usr/bin/env python3
"""Protected local-file stage checks; no claim of a full filesystem refinement."""
from pathlib import Path
import hashlib,json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from artifact_gate import ArtifactGate, LeanChecker, GateError, encode

def main():
    checker=LeanChecker();cases=[]
    with tempfile.TemporaryDirectory(prefix='avoc_stages_') as folder:
        d=Path(folder);gate=ArtifactGate(d/'store',checker)
        target=d/'target.json';proof=d/'proof.json'
        target.write_text(encode(dict(schema='avoc-proposition-1',task='root',statement=['true'],dependencies=[])))
        proof.write_text(encode(['hyp',['atom',0]]))
        bad=gate.register(target,proof);before=gate.load()
        try:gate.verify()
        except GateError as e:
            assert gate.load()==before
            cases.append(dict(name='verification_rejection_retains_pending',result='EXPECTED_REJECTION',reason=str(e)))
        else:raise AssertionError('invalid proof accepted')
        proof.write_text(encode(['true']));first=gate.register(target,proof)
        assert first['generation']>bad['generation']
        receipt=gate.verify();assert not gate.load()['admitted']
        cases.append(dict(name='verification_does_not_admit',result='PASS'))
        before=gate.load()
        forged=json.loads(encode(receipt));forged['approved']=False
        try:gate.admit(forged)
        except GateError as e:
            assert gate.load()==before
            cases.append(dict(name='rejected_admission_retains_pending',result='EXPECTED_REJECTION',reason=str(e)))
        else:raise AssertionError('rejected receipt admitted')
        again=gate.register(target,proof);assert again['generation']>first['generation']
        before=gate.load()
        try:gate.admit(receipt)
        except GateError as e:
            assert gate.load()==before
            cases.append(dict(name='same_source_new_generation_rejects_old_receipt',result='EXPECTED_REJECTION',reason=str(e)))
        else:raise AssertionError('stale generation admitted')
        fresh=gate.verify();assert not gate.load()['admitted']
        gate.admit(fresh);assert 'root' in gate.load()['admitted'] and gate.load()['pending'] is None
        cases.append(dict(name='fresh_admission_consumes_pending',result='PASS'))
        before=gate.load()
        try:gate.admit(fresh)
        except GateError as e:
            assert gate.load()==before
            cases.append(dict(name='consumed_receipt_replay_rejected',result='EXPECTED_REJECTION',reason=str(e)))
        else:raise AssertionError('receipt replay admitted')
    inputs=['checks/test_reported_file_stages.py','tools/artifact_gate.py','tools/CertificateMain.lean','AVOC/BindingCodec.lean','AVOC/ArtifactBinding.lean','AVOC/CertificateLogic.lean']
    out=dict(status='PASS',cases=cases,real_checker_invocations=len(checker.records),checker_records=checker.records,
        source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in inputs},
        scope='Real file stages under protected-store assumptions; belief law and charged budgets belong to the separate declared controller, not to this legacy filesystem adapter.')
    (ROOT/'results/v0.17.0/reported_file_stages.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['checker_records','source_hashes']},indent=2))
if __name__=='__main__':main()
