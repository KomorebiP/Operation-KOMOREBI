"""Independent replay of the exact Block 19 production sources plus boundary API probe.
Usage: python3 checks/family_audit/run_audit.py /path/to/pinned/kit
Creates temporary proof objects; preserves only small logs and source hashes.
"""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'checks'))
from lean_env import lean_env

def main():
    lean,env=lean_env(sys.argv[1])
    mods=['OrthogonalProjectors','CornerProjectors','OrthogonalPartial','OrthogonalLifting',
          'FamilySummands','FamilyRigidity','FamilyBoundary','FamilyExamples','FamilyClassification']
    records=[]
    with tempfile.TemporaryDirectory(prefix='paperx_family_audit_',dir=os.environ.get('PAPERX_AUDIT_TMPDIR')) as tmp:
        audit=Path(tmp);(audit/'PaperX').mkdir()
        for obj in (ROOT/'build/PaperX').glob('*.olean'):
            if obj.stem not in mods:(audit/'PaperX'/obj.name).symlink_to(obj)
        env['LEAN_PATH']=str(audit)+os.pathsep+env['LEAN_PATH'].split(os.pathsep,1)[1]
        for mod in mods:
            src=ROOT/'lean/PaperX'/f'{mod}.lean'
            digest=hashlib.sha256(src.read_bytes()).hexdigest()
            p=subprocess.run([lean,'-DwarningAsError=true','-o',str(audit/'PaperX'/f'{mod}.olean'),str(src)],
                env=env,cwd=ROOT/'lean',text=True,capture_output=True,timeout=180)
            (HERE/f'{mod}.log').write_text(p.stdout+p.stderr)
            record={'module':mod,'source_sha256':digest,'exit_code':p.returncode,
                'source_unchanged_during_compile':digest==hashlib.sha256(src.read_bytes()).hexdigest()}
            records.append(record)
            print(mod,p.returncode,flush=True)
            assert p.returncode==0 and record['source_unchanged_during_compile'],p.stdout+p.stderr
        p=subprocess.run([lean,'-DwarningAsError=true',str(HERE/'FamilyAuditSmoke.lean')],
            env=env,cwd=ROOT/'lean',text=True,capture_output=True,timeout=180)
        output=p.stdout+p.stderr;(HERE/'FamilyAuditSmoke.log').write_text(output)
        print('FamilyAuditSmoke',p.returncode,flush=True)
        assert p.returncode==0,output
        ax=re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",output)
        assert len(ax)==8
        assert all({x.strip() for x in a.split(',')} <= {'propext','Classical.choice','Quot.sound'} for _,a in ax)
    (HERE/'compile.json').write_text(json.dumps(records,indent=2)+'\n')

if __name__=='__main__':main()
