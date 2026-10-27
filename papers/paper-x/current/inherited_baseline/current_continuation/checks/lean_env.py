from pathlib import Path
import os,subprocess
ROOT=Path(__file__).resolve().parents[1]
def lean_env(kit):
 kit=Path(kit).resolve();env=os.environ.copy();env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env['PATH']
 lean=kit/'toolchain/bin/lean'
 probe=subprocess.run([str(lean),'--version'],env=env,capture_output=True,text=True)
 if probe.returncode and 'failed to locate application' in probe.stderr+probe.stdout:
  env['LD_PRELOAD']=str(kit/'compat/app_path.so')
 elif probe.returncode:raise RuntimeError(f'Lean startup failed {probe.returncode}: {probe.stderr}')
 lp=subprocess.check_output([str(kit/'toolchain/bin/lake'),'env','printenv','LEAN_PATH'],cwd=kit/'workspace',env=env,text=True).strip()
 env['LEAN_PATH']=str(ROOT/'build')+os.pathsep+lp
 return str(lean),env
if __name__=='__main__':
 import sys
 lean,env=lean_env(sys.argv[1]);src=sys.argv[2]
 cmd=[lean,'-DwarningAsError=true']
 if len(sys.argv)>3:cmd+=['-o',str(ROOT/'build/PaperX'/sys.argv[3])]
 p=subprocess.run(cmd+[str(Path(src).resolve())],cwd=ROOT/'lean',env=env)
 sys.exit(p.returncode)
