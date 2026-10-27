"""Fail-closed source, diagram-data and inherited-evidence audit for edition 1.5.0.

This command does not run Lean or replace pytest. Those scopes are recorded
separately. It writes data/visual_verification_1.5.0.json.
"""
from __future__ import annotations
import csv
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from proof_path_theory import __version__,analyze_affine_realizations,load_proof_field,unique_and_dag_certificate


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def require(value:bool,message:str)->None:
    if not value:raise RuntimeError(message)


def main()->int:
    report={'publication_edition':'1.5.0','technical_package_version':__version__,'fresh_lean_compilation':False,'status':'RUNNING'}
    try:
        require(__version__=='1.3.0','Technical source version changed')
        tex=(ROOT/'docs/Proof_Path_Theory.tex').read_text()
        labels=re.findall(r'\\label\{([^}]+)\}',tex)
        require(len(labels)==len(set(labels)),'Duplicate source labels')
        refs=re.findall(r'\\(?:ref|eqref|pageref|autoref)\{([^}]+)\}',tex)
        require(set(refs)<=set(labels),'Unresolved source references')
        claims=list(csv.DictReader((ROOT/'data/claim_ledger.csv').open()))
        ids=[x['claim_id'] for x in claims];expect=[f'PPT-{i:03d}' for i in range(1,34)]
        require(ids==expect,'Claim IDs changed')
        require(re.findall(r'^(PPT-\d+)\s*&',tex,re.M)==expect,'Printed result ledger changed')
        report['result_groups']=len(ids)
        report['source_labels']=len(labels)
        baseline=json.loads((ROOT/'editorial/visual_baseline_1.4.0.json').read_text())
        for category in ['package_sources','test_sources','formal_sources']:
            for rel,value in baseline[category].items():require(sha(ROOT/rel)==value,'Changed '+rel)
            report[category+'_unchanged']=len(baseline[category])
        oldformal=json.loads((ROOT/'editorial/formal_baseline_v1.2.0.json').read_text())
        for cat in ['formal_source_hashes','inherited_lean_evidence_hashes']:
            for rel,value in oldformal[cat].items():require(sha(ROOT/rel)==value,'Inherited record changed: '+rel)
            report[cat+'_matched']=len(oldformal[cat])
        pat=re.compile(r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|problem|warning|remark|proof)\}(.*?)\\end\{\1\}',re.S)
        envs=[(m.group(1),m.group(2)) for m in pat.finditer(tex)]
        require(hashlib.sha256(repr(envs).encode()).hexdigest()==baseline['mathematical_environments_sha256'],'A statement/proof environment changed')
        report['mathematical_environments_unchanged']=len(envs)
        require(len(envs)==131,'Unexpected statement/proof count')
        contracts=json.loads((ROOT/'data/visual_contracts_1.5.0.json').read_text())
        stems=[k for k in contracts['figures'] if k.startswith('fig_')]
        require(len(stems)==22,'Expected 22 mathematical figures')
        for name in contracts['figures']:
            for ext in ['pdf','png']:require((ROOT/'docs/figures'/f'{name}.{ext}').is_file(),'Missing visual '+name)
        for name in stems:require(name+'.pdf' in tex,'Figure not used in manuscript: '+name)
        report['numbered_figures']=22;report['cover_motifs']=1
        field=load_proof_field(ROOT/'examples/and_dag.json');core=unique_and_dag_certificate(field)
        require(sorted(core.node_ids)==contracts['checks']['and_dag_core'],'Core display mismatch')
        pts=list(itertools.product([0,1],repeat=3))
        require(sum(sum(p)%2==0 for p in pts)==4,'Parity count')
        sols=[p for p in pts if sum(p)%2==0 and p[0]==0]
        require(sols==[(0,0,0),(0,1,1)],'Protected cube vertices')
        all_models=[p for p in pts if not(p[0] and p[1]) or p[2]]
        require(len(all_models)==7,'Rule model count')
        require((1,1,0) not in all_models,'Gluing counterexample')
        gains=[]
        for obs in [[[1,0,0]],[[0,1,0]],[[0,1,0],[0,1,0]]]:
            out=analyze_affine_realizations(dimension=3,compatibility=[[1,1,1]],protected=[[1,0,0]],candidate=[0,0,0],observation=obs)
            require(out.realization_count==2,'Fiber count changed')
            gains.append(out.observation_gain_bits)
        require(gains==[0,1,1],'Observation diagram ranks')
        out=analyze_affine_realizations(dimension=3,compatibility=[[1,1,0]],protected=[[1,0,0],[0,1,0]],candidate=[0,1,0],observation=[[0,0,1]])
        require(not out.feasible and tuple(out.obstruction_witness)==(1,1,1),'Negative witness display mismatch')
        # Independent decoder collision: identical encoded inputs, different task answers.
        archives=[('C0',0),('C0',1)]
        require(archives[0][0]==archives[1][0] and archives[0][1]!=archives[1][1],'Collision example')
        report['new_example_checks']={'binary_states':8,'parity_states':4,'protected_states':2,'field_models':7,'gluing_counterexample':True,'observation_gains':gains,'negative_witness':[1,1,1],'compression_collision':True}
        # Validate the actual final PDF, not an old copied artifact.
        import fitz
        doc=fitz.open(ROOT/'docs/Proof_Path_Theory.pdf')
        report['pdf_pages']=len(doc);require(len(doc)==60,'Unexpected final pagination')
        images=sum(len(p.get_images()) for p in doc);report['embedded_raster_images']=images
        require(images==0,'A visual is rasterized')
        bounds=[]
        for i,p in enumerate(doc):
            for b in p.get_text('blocks'):
                if b[0]<-1 or b[1]<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1:bounds.append(i+1)
        require(not bounds,'Text outside PDF page boundaries')
        report['page_bound_violations']=0
        text='\n'.join(p.get_text() for p in doc)
        numbers={int(x) for x in re.findall(r'Figure\s+(\d+)\.',text)}
        require(numbers==set(range(1,23)),'Figure caption numbering is incomplete')
        report['caption_numbers']=sorted(numbers)
        report['pdf_sha256']=sha(ROOT/'docs/Proof_Path_Theory.pdf')
        require(not any(ROOT.rglob('*.ttf')) and not any(ROOT.rglob('*.otf')),'Standalone font found in delivery')
        report['status']='PASS'
    except Exception as exc:
        report['status']='FAIL';report['failure']=str(exc)
    (ROOT/'data/visual_verification_1.5.0.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
