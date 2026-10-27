"""Save a resumable, explicitly unscored work checkpoint. Author: Komorebi P."""
import hashlib,json,zipfile
from pathlib import Path
import engine
ROOT=Path(__file__).resolve().parent

def build(output):
    output=Path(output);manifest={};completed=0
    paths=sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in paths:
            name=p.relative_to(ROOT).as_posix();data=p.read_bytes()
            if name.startswith('results/final_legacy_census.tasks/'):
                try:item=json.loads(data);engine.verify(item);engine.verify(item['record'])
                except (ValueError,KeyError):continue
                completed+=1
            z.writestr('block17/'+name,data)
            manifest[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
        state={'author':'Komorebi P.','status':'in_progress_unscored','completed_tasks':completed,'total_tasks':1000,
          'engine_hash':engine.code_hash(),'bank_hash':engine.bank_hash(),
          'source_freeze_hash':engine.read(ROOT/'results/pre_score_source_freeze.json')['content_hash'],
          'resume_command':'python run_scan.py --challenges data/challenges.json --output results/final_legacy_census.json --workers 8',
          'preserved_frontier':'G47: 864/1076 exact outputs, 804/1000 whole tasks',
          'files':manifest}
        z.writestr('block17/WORK_CHECKPOINT_STATE.json',json.dumps(state,sort_keys=True,indent=2))
    return {'author':'Komorebi P.','status':'in_progress_unscored','completed_tasks':completed,'total_tasks':1000,
            'file':output.name,'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'resume_command':state['resume_command'],'engine_hash':engine.code_hash(),'bank_hash':engine.bank_hash()}

if __name__=='__main__':
    out=ROOT.parent/'Komorebi_PR_LASM_Block17_Work_Checkpoint.zip'
    result=build(out)
    engine.write(ROOT.parent/'Komorebi_PR_LASM_Block17_Checkpoint_State.json',result)
    print(json.dumps(result,indent=2))
