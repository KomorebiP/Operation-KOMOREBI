#!/usr/bin/env python3
"""Raw-text adversarial probes of both actual endpoints, independent of main oracle."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/v0.41.0/review_raw_probes'
KIT=Path(os.environ['AVOC_LEAN_KIT'])
ENV=os.environ.copy()
ENV['LEAN_PATH']=':'.join(map(str,[ROOT/'.lake/build/lib/lean']+[p/'.lake/build/lib/lean' for p in sorted((KIT/'workspace/.lake/packages').iterdir()) if p.is_dir()]))
ENV['PATH']=str(KIT/'toolchain/bin')+':'+ENV.get('PATH','')

def wrapped(command):
    return '["observation-recorder-v1",['+command+']]'

def main():
    cases=[
      ('bool_id',wrapped('["begin",true,0]'),False),
      ('bool_key',wrapped('["begin",0,false]'),False),
      ('negative_id',wrapped('["begin",-1,0]'),False),
      ('overflow_id',wrapped('["begin",2147483648,0]'),False),
      ('decimal_id',wrapped('["begin",0.0,0]'),False),
      ('exponent_id',wrapped('["begin",0e0,0]'),False),
      ('uppercase_exponent_key',wrapped('["begin",0,1E0]'),False),
      ('nonfinite',wrapped('["begin",NaN,0]'),False),
      ('null_key',wrapped('["begin",0,null]'),False),
      ('string_id',wrapped('["begin","0",0]'),False),
      ('extra_field',wrapped('["begin",0,0,1]'),False),
      ('missing_field',wrapped('["finish",0,0]'),False),
      ('unfinished',wrapped('["finish",0,0,"unfinished"]'),False),
      ('unknown_schema','["observation-recorder-v2",[]]',False),
      ('malformed_suffix','["observation-recorder-v1",[["begin",0,0],null]]',False),
      ('mixed_batch','["observation-recorder-batch-v1",[[],[["begin",false,0]]]]',False),
      ('duplicate_object','{"schema":"observation-recorder-v1","schema":"observation-recorder-v1"}',False),
      ('unterminated','["observation-recorder-v1",[',False),
      ('unicode_begin',wrapped('["b\\u0065gin",0,0]'),True),
      ('empty','["observation-recorder-v1",[]]',True),
      ('unknown_finish',wrapped('["finish",0,0,"success"]'),True),
      ('different_bit_replay','["observation-recorder-v1",[["begin",0,0],["finish",0,0,"rejection"],["finish",0,0,"success"]]]',True),
      ('global_pending','["observation-recorder-v1",[["begin",0,0],["finish",0,0,"success"],["begin",1,1]]]',True),
      ('late_begin','["observation-recorder-v1",[["begin",0,0],["finish",0,0,"rejection"],["begin",0,0]]]',True),
      ('invalid_suffix','["observation-recorder-v1",[["begin",0,0],["finish",0,0,"success"],["finish",1,0,"success"]]]',True),
      ('max_nat',wrapped('["begin",2147483647,2147483647]'),True),
      ('minus_zero',wrapped('["begin",-0,0]'),True),
    ]
    OUT.mkdir(exist_ok=True)
    def check(item):
        name,raw,valid=item
        path=OUT/(name+'.json');path.write_text(raw)
        commands={
          'python':[sys.executable,str(ROOT/'tools/observation_recorder.py'),str(path)],
          'lean':[str(KIT/'toolchain/bin/lean'),'-j1','--run',str(ROOT/'tools/RecorderMain.lean'),str(path)]}
        runs={}
        for runtime,cmd in commands.items():
            cp=subprocess.run(cmd,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=60)
            runs[runtime]={'returncode':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}
        passed=all(value['returncode']==(0 if valid else 2) for value in runs.values())
        if valid:
            passed=passed and json.loads(runs['python']['stdout'])==json.loads(runs['lean']['stdout'])
        return {'name':name,'schema_valid':valid,'passed':passed,'runs':runs,'request_sha256':hashlib.sha256(raw.encode()).hexdigest()}
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(check,cases))
    source_files=['AVOC/ObservationRecorder.lean','AVOC/RecorderCodec.lean','AVOC/CalibrationCodec.lean','tools/RecorderMain.lean','tools/observation_recorder.py','results/v0.41.0/review_raw_probes.py']
    report={'status':'passed' if all(r['passed'] for r in results) else 'failed','total':len(results),'passed':sum(r['passed'] for r in results),'cases':results,'source_sha256':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in source_files}}
    (ROOT/'results/v0.41.0/review_raw_probes.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':report['status'],'total':report['total'],'passed':report['passed'],'failed':[r for r in results if not r['passed']]},indent=2))
    return 0 if report['status']=='passed' else 1
if __name__=='__main__':raise SystemExit(main())
