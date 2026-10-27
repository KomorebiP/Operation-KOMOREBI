#!/usr/bin/env python3
"""Project-local validator for the reviewed computation-manifest v1 contract.
This is a v1-only implementation, not a bundled copy of the full plugin validator.
Schema-v1 provenance limitations remain explicit in the evidence record.
"""
from pathlib import Path
import argparse,hashlib,json,math,re

def need(x,m):
 if not x:raise AssertionError(m)
def main():
 p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('--root',type=Path,required=True);a=p.parse_args();d=json.loads(a.manifest.read_text())
 for k in ['schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks']:need(k in d,'Missing v1 key '+k)
 need(type(d['schema_version'])is int and d['schema_version']==1,'Only v1 is supported')
 nonempty=lambda x:isinstance(x,str) and bool(x.strip())
 for k in ['claim_id','result']:need(nonempty(d[k]),'Empty '+k)
 need(nonempty(d['command'])or isinstance(d['command'],list)and d['command'] and all(nonempty(x)for x in d['command']),'Empty command')
 need(type(d['repository']['dirty'])is bool,'Wrong revision dirty field')
 m=d['mathematics']
 for k in ['assertion_tested','coefficient_domain','conventions']:need(nonempty(m.get(k)),'Missing math '+k)
 need(isinstance(m.get('inputs'),list),'Missing inputs');need(isinstance(m.get('bounds'),dict)and m['bounds'],'Missing bounds');need(isinstance(m.get('non_claims'),list)and m['non_claims']and all(map(nonempty,m['non_claims'])),'Missing nonclaims')
 need(isinstance(d['environment'].get('software'),list)and d['environment']['software'],'Missing software versions')
 for x in d['environment']['software']:need(nonempty(x)or isinstance(x,dict)and nonempty(x.get('name'))and nonempty(x.get('version')),'Invalid software version')
 need(type(d['randomness'].get('used'))is bool,'Missing randomness declaration')
 if d['randomness']['used']:need(nonempty(d['randomness'].get('generator'))and d['randomness'].get('seed')is not None,'Missing seed')
 run=d['run'];need(nonempty(run.get('started_at')),'Missing start time');t=run.get('runtime_seconds');need(type(t)in(int,float)and math.isfinite(t)and t>=0,'Invalid runtime');need(type(run.get('exit_status'))is int,'Missing exit status')
 need(d['outputs']and isinstance(d['outputs'],list),'Missing hashed outputs')
 for x in d['outputs']:
  path=Path(x['path']);need(not path.is_absolute()and '..'not in path.parts,'Unsafe output path');f=(a.root/path).resolve();need(f.is_relative_to(a.root.resolve())and f.is_file(),'Missing output');need(bool(re.fullmatch('[0-9a-f]{64}',x['sha256'])),'Invalid hash');need(hashlib.sha256(f.read_bytes()).hexdigest()==x['sha256'],'Output hash changed')
 for k in ['checks','residual_risks']:need(isinstance(d[k],list),'Invalid '+k)
 print('PASS_PROJECT_LOCAL_V1_RECORD; legacy v1 provenance limits remain; mathematical interpretation needs review')
if __name__=='__main__':main()
