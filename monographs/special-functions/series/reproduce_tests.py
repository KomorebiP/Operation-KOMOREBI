#!/usr/bin/env python3
"""Extract preserved releases into temporary directories and run the eight suites."""
from pathlib import Path
from zipfile import ZipFile
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
ROMANS = ('I','II','III','IV','V','VI','VII','VIII')
NESTED = {'III':'Projector_Generated_Special_Functions_III_Source','V':'source','VII':'Source'}

def main():
    destination = ROOT / 'rerun_evidence' / dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    destination.mkdir(parents=True, exist_ok=False)
    report = {'python':sys.version,'generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'papers':[],
              'scope':'Independent pytest suites only; no figure or complete built-in batch rebuild.'}
    with tempfile.TemporaryDirectory(prefix='komorebi_special_tests_') as tmp:
        for roman in ROMANS:
            name = f'Projector_Generated_Special_Functions_{roman}'
            archive = ROOT / 'original_releases' / f'{name}_Release.zip'
            before = hashlib.sha256(archive.read_bytes()).hexdigest()
            parent = Path(tmp) / roman
            parent.mkdir()
            with ZipFile(archive) as z:
                for member in z.infolist():
                    if not (parent/member.filename).resolve().is_relative_to(parent.resolve()):
                        raise ValueError('Unsafe ZIP member')
                z.extractall(parent)
            source = parent / (name+'_Release')
            if roman in NESTED:
                source /= NESTED[roman]
            junit = destination / f'Paper_{roman}_junit.xml'
            command = [sys.executable,'-m','pytest','-q','tests','-p','no:cacheprovider','--junitxml',str(junit)]
            env = os.environ.copy()
            env.update({'MPLBACKEND':'Agg','PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','PYTHONPATH':os.pathsep.join(filter(None,(str(source),env.get('PYTHONPATH')))),
                        'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
            started = time.perf_counter()
            result = subprocess.run(command,cwd=source,env=env,capture_output=True,text=True,timeout=900)
            (destination/f'Paper_{roman}_pytest.txt').write_text(result.stdout+result.stderr)
            counts = dict(tests=0,failures=0,errors=0,skipped=0)
            if junit.exists():
                for suite in ET.parse(junit).getroot().iter('testsuite'):
                    for key in counts:
                        counts[key] += int(suite.attrib.get(key,0))
            record = {'paper':roman,'command_argv':command,'exit_code':result.returncode,
                      'seconds':time.perf_counter()-started,'archive_sha256':before,
                      'archive_unchanged':before==hashlib.sha256(archive.read_bytes()).hexdigest(),**counts}
            report['papers'].append(record)
            print(json.dumps(record),flush=True)
            (destination/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    report['totals'] = {key:sum(r[key] for r in report['papers']) for key in ('tests','failures','errors','skipped')}
    (destination/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if all(r['exit_code']==0 and r['archive_unchanged'] for r in report['papers']) else 1

if __name__ == '__main__':
    raise SystemExit(main())
