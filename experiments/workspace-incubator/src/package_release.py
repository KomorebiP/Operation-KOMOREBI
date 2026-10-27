"""Deterministic package of the retained research tree, no font/model downloads."""
from pathlib import Path
import json,hashlib,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent
SKIP={'__pycache__','.pytest_cache'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    paths=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and not SKIP.intersection(p.relative_to(ROOT).parts) and p.name!='MANIFEST.json']
    mf={'version':'0.6','scope':'exact file integrity, not scientific proof','files':{p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths}}
    (ROOT/'MANIFEST.json').write_text(json.dumps(mf,indent=2)+'\n')
    paths=sorted(paths+[ROOT/'MANIFEST.json'])
    def build(out):
        with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for p in paths:
                info=zipfile.ZipInfo(ROOT.name+'/'+p.relative_to(ROOT).as_posix(),date_time=(2026,9,27,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;info.create_system=3
                z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    archive=OUT/'Komorebi_Workspace_Incubator_v0_6.zip';tmp=OUT/'v06_rebuild_check.zip'
    build(archive);build(tmp);assert sha(archive)==sha(tmp);tmp.unlink()
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
    print(json.dumps({'archive':str(archive),'archive_sha256':sha(archive),'bytes':archive.stat().st_size,'manifest_files':len(mf['files']),'exact_rebuild':True},indent=2))
    for src,name in [('REPORT.md','Komorebi_Workspace_Incubator_v0_6_REPORT.md'),('RESULTS.json','Komorebi_Workspace_Incubator_v0_6_RESULTS.json'),
                     ('notes/MATHEMATICAL_CRUX.md','Komorebi_JSpace_Native_Access_Repair_v0_6.md'),
                     ('notes/STABLE_ACCESS_NEXT_DESIGN.md','Komorebi_JSpace_Stable_Access_v0_7_DESIGN.md'),('checks/FAILURES.md','Komorebi_Workspace_Incubator_v0_6_FAILURES.md')]:
        shutil.copy2(ROOT/src,OUT/name)
if __name__=='__main__':main()
