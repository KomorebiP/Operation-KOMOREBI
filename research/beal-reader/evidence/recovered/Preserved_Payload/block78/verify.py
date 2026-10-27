#!/usr/bin/env python3
import json,hashlib,subprocess,sys,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PRED=ROOT/'predecessor/Komorebi_Beal_Block77_Secondary_Adjoint_Selmer_v7.7.0.zip'
PRED_SHA='e8815ff496368ff99ca583f422f14d5a0bce6df537187691c89e7848f7a7e8ec'

def sha(p):
    h=hashlib.sha256();
    with open(p,'rb') as f:
      for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def run(script):
    cp=subprocess.run([sys.executable,'-B',str(script)],cwd=ROOT,text=True,capture_output=True,check=True)
    return json.loads(cp.stdout)
def main():
    report=None; replay=False
    args=sys.argv[1:]
    i=0
    while i<len(args):
      if args[i]=='--report': report=Path(args[i+1]); i+=2
      elif args[i]=='--replay-predecessor': replay=True; i+=1
      else: raise SystemExit('unknown arg '+args[i])
    assert sha(PRED)==PRED_SHA
    man=json.loads((ROOT/'MANIFEST.json').read_text())
    for rel,d in man['files'].items():
      p=ROOT/rel
      if not p.is_file(): raise AssertionError('missing '+rel)
      if sha(p)!=d: raise AssertionError('changed '+rel)
    p=run(ROOT/'work78/computations/primary78.py')
    q=run(ROOT/'work78/computations/independent78.py')
    assert p['status']==q['status']=='PASS'
    assert p['affine_toric_packets']==q['affine_toric_packets']==806736
    assert p['dual_action_checks']==q['dual_action_checks']==588
    assert p['wrong_sign_failures']==q['wrong_sign_failures']==691488
    assert p['canonical_sum_mod_2_64']==q['canonical_sum_mod_2_64']
    assert p['canonical_xor_64']==q['canonical_xor_64']
    # compare against frozen scientific outputs
    assert p==json.loads((ROOT/'work78/verification/primary78.json').read_text())
    assert q==json.loads((ROOT/'work78/verification/independent78.json').read_text())
    pred_tail=None
    if replay:
      with tempfile.TemporaryDirectory() as td:
        subprocess.run(['python','-m','zipfile','-e',str(PRED),td],check=True,capture_output=True)
        vp=Path(td)/'verify.py'
        cp=subprocess.run([sys.executable,'-B',str(vp)],cwd=td,text=True,capture_output=True,check=True)
        pred_tail='\n'.join(cp.stdout.strip().splitlines()[-4:])
    out={'status':'PASS_DECLARED_CHECKS','version':'7.8.0','predecessor_sha256':PRED_SHA,
         'payload_files_checked':len(man['files']),'primary_status':p['status'],'independent_status':q['status'],
         'affine_toric_packets':p['affine_toric_packets'],'dual_action_checks':p['dual_action_checks'],
         'canonical_sum_mod_2_64':p['canonical_sum_mod_2_64'],'canonical_xor_64':p['canonical_xor_64'],
         'replayed_immediate_predecessor':replay,'predecessor_stdout_tail':pred_tail,
         'nonclaims':['finite arithmetic does not prove Neukirch localization surjectivity',
                      'unrestricted localization does not control ramification outside finite prescribed sets',
                      'no Block70 bounded pattern is eliminated','no Lean compilation or independent mathematical review']}
    if report:
      report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(out,indent=2,sort_keys=True))
    print('PASS_DECLARED_CHECKS')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
