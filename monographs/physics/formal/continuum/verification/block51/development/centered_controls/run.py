import datetime, hashlib, json, os, pathlib, re, shutil, subprocess, sys, time
root=pathlib.Path('/workspace/scratch/6a8ff46cf015')
project=root/'physics_next/work/Komorebi_Physics_Lean_v0.49.0_Checked_Block_49'
kit=root/'physics_next/runtime/Komorebi_Portable_Lean_4.34.0-rc2'
out=pathlib.Path(__file__).parent
env=os.environ.copy()
env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env.get('PATH','')
env['LD_PRELOAD']=str(kit/'compat/app_path.so')
files=sorted(project.glob('positive_controls/block51/centered/*.lean'))+sorted(project.glob('negative_controls/block51/centered/*.lean'))
if len(sys.argv)>1:
    files=[p for p in files if p.stem in sys.argv[1:]]
for path in files:
    relative=path.relative_to(project).as_posix()
    run_id=len(list(out.glob('run_*.json')))+1
    name=f'run_{run_id:03}_{path.stem}'
    argv=['lake','env','lean','-j1','-DwarningAsError=true',relative]
    record={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':argv,'cwd':str(project),'source':relative,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'expected_exit':0 if 'positive_controls' in relative else 1}
    shutil.copyfile(path,out/(name+'.lean'))
    start=time.monotonic()
    try:
        process=subprocess.run(argv,cwd=project,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120,text=True)
        output,code=process.stdout,process.returncode
    except subprocess.TimeoutExpired as e:
        output=str(e.stdout or '')+'\nTIMEOUT\n'; code=124
    (out/(name+'.log')).write_text(output)
    record.update(exit_code=code,seconds=time.monotonic()-start,log=name+'.log',log_sha256=hashlib.sha256((out/(name+'.log')).read_bytes()).hexdigest())
    (out/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record)); print(output,flush=True)
