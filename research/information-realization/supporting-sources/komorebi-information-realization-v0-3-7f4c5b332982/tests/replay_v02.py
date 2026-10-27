"""Replay unchanged v0.2 suites without overwriting their preserved reports."""
from __future__ import annotations
import argparse,importlib.util,json,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'prior_v0_2'/'tests'/'run_audit.py'
spec=importlib.util.spec_from_file_location('preserved_v02_audit',path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite',choices=tuple(module.SUITES)+('all',),default='all')
    args=parser.parse_args()
    names=tuple(module.SUITES) if args.suite=='all' else (args.suite,)
    for name in names:
        start=time.perf_counter();print('REPLAY',name,flush=True)
        try:
            data=module.SUITES[name]()
            report={'suite':name,'status':'PASS','python':sys.version,'optimization_level':sys.flags.optimize,
                    'elapsed_seconds':round(time.perf_counter()-start,3),**data}
        except Exception:
            report={'suite':name,'status':'FAIL','traceback':traceback.format_exc()}
        suffix='_optimized' if sys.flags.optimize else ''
        (ROOT/'reports'/f'v02_replay_{name}{suffix}.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2),flush=True)
        if report['status']!='PASS':return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
