import hashlib,json,pathlib,subprocess,zipfile,time
root=pathlib.Path('/mnt/data/lean_restore')
out=pathlib.Path('/mnt/data/lean_runtime')
h=hashlib.sha256(); parts=[]; start=time.time()
zstd=subprocess.Popen(['zstd','-dc'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
tar=subprocess.Popen(['tar','-xf','-','--no-same-owner','-C',str(out)],stdin=zstd.stdout)
zstd.stdout.close()
for n in range(1,8):
    p=root/f'Lean_Offline_{n:02}.zip'
    ph=hashlib.sha256(); count=0
    with zipfile.ZipFile(p) as z:
        names=z.namelist()
        assert len(names)==1,names
        with z.open(names[0]) as f:
            while b:=f.read(4*1024*1024):
                h.update(b); ph.update(b); count+=len(b); zstd.stdin.write(b)
    parts.append({'file':p.name,'member':names[0],'bytes':count,'sha256':ph.hexdigest()})
    print('restored part',n,count,ph.hexdigest(),flush=True)
zstd.stdin.close(); zrc=zstd.wait(); trc=tar.wait()
report={'sha256':h.hexdigest(),'expected':'66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34','zstd_exit':zrc,'tar_exit':trc,'elapsed_seconds':time.time()-start,'parts':parts}
report['passed']=h.hexdigest()==report['expected'] and zrc==trc==0
pathlib.Path('/mnt/data/kzfc_work/runtime_restore.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
assert report['passed']
