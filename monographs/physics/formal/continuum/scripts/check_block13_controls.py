#!/usr/bin/env python3
"""Compile the eight new false controls in a bounded, line-mapped batch.
An import failure, unrelated error, timeout or missing individual diagnostic fails.
This development check does not replace the cumulative production audit.
"""
from pathlib import Path
import json,re,hashlib,subprocess,sys,time
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    kit=Path(sys.argv[1]).resolve()
    names=json.loads((ROOT/'reference/block13_negative_control_names.json').read_text())
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out=ROOT/'verification/development/block13'/('controls_'+stamp);out.mkdir(parents=True)
    sources=[ROOT/'negative_controls'/f'{n}.lean' for n in names]
    imports=sorted({l for p in sources for l in p.read_text().splitlines() if l.startswith('import ')})
    lines=imports+['']; records=[]
    for n,p in zip(names,sources):
        body=[l for l in p.read_text().splitlines() if not l.startswith('import ')]
        lines.append('namespace Check_'+n); start=len(lines)+1
        lines.extend(body)
        records.append(dict(name=n,start_line=start,end_line=len(lines),sha256=sha(p)))
        lines+=['end Check_'+n,'']
    source=out/'controls.lean';source.write_text('\n'.join(lines)+'\n')
    cmd=['bash',str(kit/'run.sh'),'lake','env','lean','-j1','-DwarningAsError=true',str(source)]
    t=time.monotonic(); report=dict(status='INCOMPLETE',argv=cmd,source_sha256=sha(source),controls=records)
    try:
        proc=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
        log=proc.stdout;(out/'compile.log').write_text(log)
        headers=list(re.finditer(r'^.*?:(\d+):\d+: (?:error(?:\([^\n]*?\))?|warning):',log,re.M))
        errors=[(int(m[1]),log[m.start():headers[i+1].start() if i+1<len(headers) else len(log)]) for i,m in enumerate(headers)]
        for r in records:
            msgs=[msg for ln,msg in errors if r['start_line']<=ln<=r['end_line']]
            r['status']='PASS' if msgs and all('unsolved goals' in msg for msg in msgs) else 'FAIL'
        matched=all(any(r['start_line']<=ln<=r['end_line'] for r in records) for ln,_ in errors)
        report.update(status='PASS' if proc.returncode!=0 and matched and all(r['status']=='PASS' for r in records) else 'FAIL',returncode=proc.returncode,diagnostics=len(errors),log_sha256=sha(out/'compile.log'))
    except subprocess.TimeoutExpired as e:
        log=e.stdout or b''
        if isinstance(log,bytes):log=log.decode(errors='replace')
        (out/'compile.log').write_text(log+'\nTIMEOUT\n')
        report.update(status='TIMEOUT')
    report['seconds']=round(time.monotonic()-t,4)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],out,flush=True)
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
