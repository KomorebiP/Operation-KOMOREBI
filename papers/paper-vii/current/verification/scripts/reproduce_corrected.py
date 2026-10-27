#!/usr/bin/env python3
"""Portable separately manifested corrected-edition numerical gate."""
import argparse,json,platform,subprocess,sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--downloads',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--root',type=Path,default=Path.cwd());a=ap.parse_args()
    root=a.root.resolve();base=Path(__file__).resolve().parents[1]
    def rel(p):return str(p.resolve().relative_to(root))
    source=(root/a.source).resolve();downloads=(root/a.downloads).resolve();out=(root/a.out).resolve()
    inputs=sorted(rel(p) for tree in (source,downloads,base/'scripts',base/'tools',base/'corrected_strengthened') for p in tree.rglob('*') if p.is_file() and p.suffix!='.pyc')
    import numpy,scipy
    contract={'claim_id':'PAPER_VII_CORRECTED_ODD_N_REPRESENTATIVES',
        'mathematics':{'assertion_tested':'Corrected representative lists contain exactly N unique residue classes and |k|<=N/2 for N4..32; two-endpoint corrected strengthened suite passes on preserved assets.',
            'coefficient_domain':'Exact integers for representative count/residues; IEEE binary64 complex matrices for original finite numerical assertions.',
            'conventions':'Only both lower endpoints -N//2 become -(N//2); every other raw verifier byte is unchanged. Original norm, tensor, Choi and tolerance conventions retained.',
            'inputs':['725 complete and59 strengthened source files','two archive originals','two-endpoint corrected verifier'],
            'bounds':{'N_min':4,'N_max':32,'representative_assertions':87,'strengthened_groups':15,'original_unchanged_suite_check_count':18049,'expected_corrected_check_count':17699},
            'non_claims':['Does not edit the preserved raw verifier or replace its separately recorded fresh result.',
                'No fresh Lean check, universal theorem, continuum limit or physical quantum-gravity conclusion.']},
        'execution_artifacts':inputs,'software':[{'name':'Python','version':platform.python_version()},{'name':'NumPy','version':numpy.__version__},{'name':'SciPy','version':scipy.__version__}],
        'randomness':{'used':True,'generator':'NumPy default_rng PCG64 in unchanged random code','seed':20260814}}
    path=base/'contracts'/(out.name+'.json');path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(contract,indent=2)+'\n')
    cmd=[sys.executable,str(base/'tools/run_experiment.py'),'--root',str(root),'--contract',str(path),
        '--output',rel(out),'--result',rel(out/'results.json'),'--timeout','600','--max-output-bytes','10485760',
        '--max-memory-bytes','2147483648','--max-cpu-seconds','480','--max-cores','1','--max-threads','1']
    for p in inputs:cmd.extend(['--input',p])
    cmd.extend(['--',sys.executable,rel(base/'scripts/replay_corrected.py'),'--source',rel(source),
        '--corrected',rel(base/'corrected_strengthened/verify_paper_vii.py'),'--out',rel(out)])
    rc=subprocess.call(cmd,cwd=root)
    if rc:return rc
    return subprocess.call([sys.executable,str(base/'tools/validate_manifest.py'),str(out/'manifest.json'),'--root',str(root)],cwd=root)

if __name__=='__main__':raise SystemExit(main())
