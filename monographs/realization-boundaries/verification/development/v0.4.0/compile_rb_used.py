import pathlib,os,subprocess,sys,json,time
root=pathlib.Path('/mnt/data/Realization_Boundaries_Lean_v0.4.0'); kit=pathlib.Path('/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2'); env=os.environ.copy();env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
for k in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']:env.pop(k,None)
logroot=root/'verification/development/v0.4.0'; logroot.mkdir(parents=True,exist_ok=True)
for name in sys.argv[1:]:
 src=pathlib.Path(name if name.endswith('.lean') else f'RealizationBoundaries/{name}.lean'); target=root/'.lake/build/lib/lean'/src.with_suffix('.olean'); target.parent.mkdir(parents=True,exist_ok=True)
 log=logroot/(str(time.time_ns())+'_'+src.stem+'.log'); cmd=[str(kit/'toolchain/bin/lake'),'env','lean','-DwarningAsError=true','-DautoImplicit=false','-o',str(target),str(src)]
 t=time.time()
 with log.open('w') as f:
  try:
   p=subprocess.run(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180); rc=p.returncode
  except subprocess.TimeoutExpired:rc=124
 row={'source':str(src),'command':cmd,'exit_code':rc,'seconds':time.time()-t,'log':str(log)};log.with_suffix('.json').write_text(json.dumps(row,indent=2))
 print(src,rc,round(time.time()-t,2),flush=True)
 if rc:
  print(log.read_text(),flush=True);sys.exit(rc)
