import json,subprocess,zipfile,pathlib,sys
root=pathlib.Path('/workspace/scratch/2e8d212e9ca7');req=json.load(open(root/'.helpers11/request.json'))
base=req['result']['structuredContent']['structuredContent']; entries=base['results']; lookup={e['name']:i for i,e in enumerate(entries)}
tar=subprocess.Popen(['tar','-xf','-','-C',str(root/'runtime11'),'--wildcards','*.olean.server'],stdin=subprocess.PIPE)
zstd=subprocess.Popen(['zstd','-d','-c'],stdin=subprocess.PIPE,stdout=tar.stdin);tar.stdin.close()
for n in range(1,8):
 name=f'Lean_Offline_{n:02}.zip'; req['selection']=f'{lookup[name]:03}'
 r=subprocess.run([sys.executable,str(root/'.helpers11/library_download.py')],input=json.dumps(req),text=True,capture_output=True,cwd=root)
 if r.returncode: raise RuntimeError(r.stderr)
 p=pathlib.Path(json.loads(r.stdout)['files'][0])
 with zipfile.ZipFile(p) as f:
  with f.open(f.namelist()[0]) as stream:
   while b:=stream.read(4*1024*1024): zstd.stdin.write(b)
 p.unlink();print('RESTORED part',n,flush=True)
zstd.stdin.close();assert zstd.wait()==0;assert tar.wait()==0
