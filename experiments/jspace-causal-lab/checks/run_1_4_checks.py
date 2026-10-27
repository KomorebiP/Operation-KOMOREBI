"""Foreground verification supervisor. Captures real OS exit status for each child.
No asynchronous work is left running. Output artifacts are bounded to this folder.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time,datetime,shutil,os,signal
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'checks/relay';journal=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(argv,label,timeout=65):
    inputs=[ROOT/'app/weights.bin',ROOT/'app/frames.json',ROOT/'app/relay_engine.js']
    before={str(p.relative_to(ROOT)):digest(p) for p in inputs};start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter()
    child=subprocess.Popen(argv,cwd=ROOT,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','PYTHONUNBUFFERED':'1'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
    timed_out=False
    try:stdout,stderr=child.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out=True
        os.killpg(child.pid,signal.SIGTERM)
        try:stdout,stderr=child.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate()
    cp=subprocess.CompletedProcess(argv,child.returncode,stdout,stderr)
    log=OUT/(label+'.log');log.write_text(cp.stdout+'\nSTDERR:\n'+cp.stderr+('\nSUPERVISOR TIMEOUT\n' if timed_out else ''))
    after={str(p.relative_to(ROOT)):digest(p) for p in inputs}
    entry=dict(argv=argv,started_at=start,seconds=time.perf_counter()-t,returncode=cp.returncode,timed_out=timed_out,log=str(log.relative_to(ROOT)),log_sha256=digest(log),input_hashes_before=before,input_hashes_after=after)
    journal.append(entry);(OUT/'COMMANDS.json').write_text(json.dumps(journal,indent=2))
    assert before==after,entry
    if cp.returncode:raise RuntimeError(cp.stderr or cp.stdout)
    print(label,'PASS',round(entry['seconds'],3))
# Preserve first execution record; replaying it does not create new evidence cases.
if not (OUT/'assay_first_execution.json').exists():
    shutil.copy2(OUT/'assay.json',OUT/'assay_first_execution.json');shutil.copy2(OUT/'SOURCE_FREEZE.json',OUT/'FIRST_SOURCE_FREEZE.json')
raw_before=digest(OUT/'raw.json.gz');ref_before=digest(OUT/'reference.json');first=json.loads((OUT/'assay.json').read_text())
run(['node','checks/run_relay_assay.js'],'assay_replay')
second=json.loads((OUT/'assay.json').read_text());replay={'status':'PASS','raw_archive_bytes_identical':raw_before==digest(OUT/'raw.json.gz'),'numeric_reference_bytes_identical':ref_before==digest(OUT/'reference.json'),'all_aggregate_cells_identical':first['cells']==second['cells'],'scope':'Same frozen weights, inputs, software and engine. No training and no independent statistical replication.'}
assert all(replay[k] for k in ['raw_archive_bytes_identical','numeric_reference_bytes_identical','all_aggregate_cells_identical']);(OUT/'assay_replay.json').write_text(json.dumps(replay,indent=2))
for argv,label in [
 (['node','checks/test_relay_engine.js'],'new_engine'),
 ([sys.executable,'checks/check_relay_pytorch.py'],'original_pytorch'),
 ([sys.executable,'checks/audit_relay_results.py'],'independent_audit'),
 (['node','checks/test_causal_port.js'],'inherited_causal'),
 (['node','checks/test_refine_engine.js'],'inherited_session'),
 (['node','checks/test_challenge_engine.js'],'inherited_challenge'),
 ([sys.executable,'checks/test_relay_browser.py'],'new_browser'),
 ([sys.executable,'checks/test_previous_ui_on_1_4.py'],'inherited_browser')]:run(argv,label)
print('All foreground commands completed with captured return code zero.')
