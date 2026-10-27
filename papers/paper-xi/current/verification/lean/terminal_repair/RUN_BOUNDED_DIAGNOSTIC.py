#!/usr/bin/env python3
"""Run a bounded diagnostic only; never count its output as a release module replay."""
from pathlib import Path
import os, subprocess, time, json, hashlib, datetime, sys
p=Path(__file__).resolve().parents[2]
d=(p/sys.argv[1]).resolve()
if not d.is_relative_to(p/'evidence/terminal_repair'):
    raise SystemExit('Candidate must be in preserved diagnostic history')
src=d/'ActualMonomialLocalGlobal.lean'
bin=p/'.runtime/lean-4.34.0-rc2-linux/bin'
objects=p/'evidence/replay_terminal_synchronous/objects'
env=os.environ.copy()
env['PATH']=str(bin)+os.pathsep+env.get('PATH','')
env['LEAN_PATH']=os.pathsep.join(map(str,[objects,*sorted((p/'.lake/packages').glob('*/.lake/build/lib/lean'))]))
cmd=[str(bin/'lean'),'-j1','-DElab.async=false','-DmaxErrors=10','-DmaxHeartbeats=300000','-Dprofiler=true','-Dprofiler.threshold=1000',str(src.relative_to(p))]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for name in ['DIAGNOSTIC_RUNNING.json','DIAGNOSTIC_RESULT.json','DIAGNOSTIC.log','DIAGNOSTIC_RUNNER_EXECUTED.py']:
    if (d/name).exists():
        raise SystemExit('Refusing to overwrite diagnostic evidence: '+name)
(d/'DIAGNOSTIC_RUNNER_EXECUTED.py').write_bytes(Path(__file__).read_bytes())
record={'kind':'bounded_diagnostic_candidate_not_release','command':cmd,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_before_sha256':sha(src),'wall_timeout_seconds':600,'log_path':str((d/'DIAGNOSTIC.log').relative_to(p)),'cgroup_memory_events_before':Path('/sys/fs/cgroup/memory.events').read_text(),'runner_sha256':sha(Path(__file__))}
(d/'DIAGNOSTIC_RUNNING.json').write_text(json.dumps(record,indent=2)+'\n')
t=time.monotonic()
with (d/'DIAGNOSTIC.log').open('wb') as out:
    child=subprocess.Popen(cmd,cwd=p,env=env,stdout=out,stderr=subprocess.STDOUT)
    print('DIAGNOSTIC PID',child.pid,flush=True)
    try:
        code=child.wait(timeout=600)
    except subprocess.TimeoutExpired:
        child.kill();child.wait();code=124
record.update(exit_code=code,status='PASS' if code==0 else 'FAIL',elapsed_seconds=time.monotonic()-t,source_after_sha256=sha(src),log_sha256=sha(d/'DIAGNOSTIC.log'),cgroup_memory_events_after=Path('/sys/fs/cgroup/memory.events').read_text(),completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(d/'DIAGNOSTIC_RESULT.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
print((d/'DIAGNOSTIC.log').read_text()[-16000:])
