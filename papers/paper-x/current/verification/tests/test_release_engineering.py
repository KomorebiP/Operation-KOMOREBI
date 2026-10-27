from pathlib import Path
import json,hashlib,tempfile,subprocess,sys,importlib.util,contextlib,io,shutil
sys.dont_write_bytecode=True
r=Path(__file__).resolve().parents[2]; records=[]
with tempfile.TemporaryDirectory(prefix='paperx-integrity-control-') as tmp:
 p=Path(tmp);d=b'correct reader bytes';(p/'sample.dat').write_bytes(d)
 m={'files':[{'path':'sample.dat','bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}]}
 (p/'MANIFEST.json').write_text(json.dumps(m))
 def run(name,expected):
  x=subprocess.run([sys.executable,str(r/'verify_release.py'),'--root',str(p),'--strict'],capture_output=True,text=True)
  assert (x.returncode==0)==expected,(name,x.stdout,x.stderr)
  records.append({'name':name,'returncode':x.returncode,'expected_success':expected,'output':json.loads(x.stdout)})
 run('positive',True)
 (p/'sample.dat').write_bytes(b'incorrect reader byt')
 run('modified_byte_rejected',False)
 (p/'sample.dat').unlink();run('missing_file_rejected',False)
 (p/'sample.dat').write_bytes(d);(p/'extra').write_text('x');run('strict_extra_file_rejected',False)
 (p/'extra').unlink();m['files'][0]['path']='../outside.dat';(p/'MANIFEST.json').write_text(json.dumps(m));run('unsafe_manifest_path_rejected',False)
with tempfile.TemporaryDirectory(prefix='paperx-build-control-') as tmp:
 p=Path(tmp);(p/'publication').mkdir();(p/'dummy.tex').write_text('Not compiled: intentional missing-engine test')
 (p/'publication/documents.json').write_text(json.dumps([{'main':'dummy.tex','file_name':'Negative_Control.pdf','engine':'paperx_deliberately_nonexistent_engine','kind':'visual'}]))
 (p/'out').mkdir();(p/'out/Negative_Control.pdf').write_text('STALE PDF')
 spec=importlib.util.spec_from_file_location('paperx_builder',r/'publication/build_publication.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.ROOT=p
 old=sys.argv;sys.argv=['build_publication.py','--build-directory',str(p/'build'),'--output-directory',str(p/'out')]
 out=io.StringIO()
 with contextlib.redirect_stdout(out):code=mod.main()
 sys.argv=old
 assert code==1 and not (p/'out/Negative_Control.pdf').exists()
 records.append({'name':'missing_engine_nonzero_and_stale_output_removed','returncode':code,'expected_success':False,'stale_pdf_removed':True,'output':json.loads(out.getvalue())})
report={'status':'passed','checks':records,'scientific_scope':'release-engineering controls only'}
(r/'verification/2026-10-10/RELEASE_ENGINEERING_CONTROLS.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
