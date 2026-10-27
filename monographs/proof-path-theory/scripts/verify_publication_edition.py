"""Audit the current publication against its predecessor and fresh formal record.

This command verifies recorded source identity and finite examples. It does not
rerun Lean. Use verify_lean.py or verify_release.py to obtain a fresh formal run.
"""
from __future__ import annotations
import ast
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import difflib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from proof_path_theory import __version__


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(test,msg):
    if not test:raise RuntimeError(msg)


def main():
    report={'publication':'1.8.0','python':__version__,'status':'RUNNING',
      'scope':'Source identity, recorded fresh Lean evidence, exact figure contracts, and PDF structure. Not independent peer review or another Lean run.'}
    try:
        import fitz
        require(__version__=='1.6.0','Wrong Python version')
        tex=(ROOT/'docs/Proof_Path_Theory.tex').read_text()
        labels=re.findall(r'\\label\{([^}]+)\}',tex)
        require(len(labels)==len(set(labels)),'Duplicate source labels')
        refs=re.findall(r'\\(?:ref|eqref|pageref|autoref)\{([^}]+)\}',tex)
        require(set(refs)<=set(labels),'Undefined source reference')
        cites={k for c in re.findall(r'\\cite\{([^}]+)\}',tex) for k in c.split(',')}
        require(cites<=set(re.findall(r'\\bibitem\{([^}]+)\}',tex)),'Undefined citation')
        claims=list(csv.DictReader((ROOT/'data/claim_ledger.csv').open()))
        ids=[f'PPT-{i:03d}' for i in range(1,48)]
        require([c['claim_id'] for c in claims]==ids,'Claim CSV mismatch')
        require(re.findall(r'^(PPT-\d+)\s*&',tex,re.M)==ids,'Printed ledger mismatch')
        require(re.findall(r'^\| (PPT-\d+) \|',(ROOT/'docs/THEOREM_LEDGER.md').read_text(),re.M)==ids,'Markdown ledger mismatch')
        report['claim_groups']=len(ids)
        baseline=json.loads((ROOT/'editorial/baseline_1.7.0.json').read_text())
        identity={}
        for prefix,exceptions in [('src/',{'src/proof_path_theory/__init__.py','src/proof_path_theory/cli.py'}),('tests/',set()),
                                 ('formal/',{'formal/CONCORDANCE.json'}),('evidence/formal_1.7.0/',set())]:
            unchanged=[p for p in baseline['files'] if p.startswith(prefix) and p not in exceptions]
            for p in unchanged:require(sha(ROOT/p)==baseline['files'][p],'Unexpected predecessor change '+p)
            identity[prefix]=len(unchanged)
        report['predecessor_files_unchanged']=identity
        approved=json.loads((ROOT/'editorial/approved_extension_1.8.0.json').read_text())
        for name,h in approved['current_sources'].items():require(sha(ROOT/name)==h,'Current source drift: '+name)
        pat=re.compile(r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|problem|warning|remark|proof)\}(.*?)\\end\{\1\}',re.S)
        envs=[(m[1],hashlib.sha256(m[2].encode()).hexdigest()) for m in pat.finditer(tex)]
        old=[tuple(x) for x in approved['predecessor_environments']]
        sm=difflib.SequenceMatcher(a=old,b=envs,autojunk=False)
        require(sum(x.size for x in sm.get_matching_blocks())==len(old)==149,'Prior mathematical environment changed')
        require(len(envs)==163,'Unexpected added mathematical environment count')
        report['mathematical_environments']={'retained':149,'added':14,'total':163}
        formal=json.loads((ROOT/'evidence/formal_1.8.0/verification.json').read_text())
        require(formal['status']=='PASS','Formal record is not PASS')
        for name,h in formal['source_hashes'].items():require(sha(ROOT/name)==h,'Formal source/evidence mismatch '+name)
        rows=json.loads((ROOT/'formal/CONCORDANCE.json').read_text())['declarations']
        require(len(rows)==formal['named_declarations']==283,'Declaration inventory mismatch')
        for d in rows:
            require(d['source_sha256']==sha(ROOT/d['file']),'Concordance source drift')
            require(d['axioms']==formal['axioms'][d['name']],'Axiom concordance drift')
            require(set(d['axioms'])<={'propext','Classical.choice','Quot.sound'},'Forbidden axiom')
        builds=[x for x in formal['commands'] if x['label'].startswith('build_')]
        replays=[x for x in formal['commands'] if x['label'].startswith('replay_')]
        require(len(builds)==len(replays)==18 and all(x['exit_code']==0 for x in builds+replays),'Incomplete production verification')
        report['formal']={'builds':18,'own_kernel_replays':18,'named_theorems':formal['named_theorems'],
                         'named_declarations':283,'negative_controls':len(formal['negative_controls'])}
        contracts=json.loads((ROOT/'data/visual_contracts_1.8.0.json').read_text())
        prev=json.loads((ROOT/'data/visual_contracts_1.7.0.json').read_text())
        for k,v in prev['checks'].items():require(contracts['checks'][k]==v,'Prior visual mathematical data changed: '+k)
        stems=contracts['figures'];require(len(stems)==26,'Wrong figure inventory')
        for stem in stems:
            require(stem+'.pdf' in tex,'Unused mathematical figure: '+stem)
            for ext in ('pdf','png'):require((ROOT/'docs/figures'/(stem+'.'+ext)).is_file(),'Missing diagram '+stem)
        require(contracts['checks']['semantic_cover']['derivation']==['r0','r1'],'Semantic-cover illustration drift')
        require(contracts['checks']['protected_rule_closure']['witness']==['r0'],'Protected illustration drift')
        report['figures']={'numbered':25,'cover':1,'predecessor_model_data_preserved':True}
        checks=json.loads((ROOT/'data/recovery_extension_checks_1.8.0.json').read_text())
        require(checks['status']=='PASS','Extended finite checks not PASS')
        report['extended_counts']=checks['counts']
        exchange=json.loads((ROOT/'data/trace_exchange_1.8.0.json').read_text())
        require(exchange['status']=='PASS','Python exchange enumeration did not pass')
        conformance=formal['trace_json_conformance']
        require(conformance['status']=='PASS' and conformance['cases']==83994 and conformance['mismatches']==0,'Actual Lean JSON conformance is incomplete')
        require(exchange['case_sha256']==sha(ROOT/'data/trace_exchange_cases.ndjson')==conformance['input_sha256'],'Exchange input drift')
        require(exchange['expected_sha256']==sha(ROOT/'data/trace_exchange_expected.txt')==conformance['expected_sha256'],'Expected exchange drift')
        require(conformance['actual_log_sha256']==sha(ROOT/'evidence/formal_1.8.0/trace_json_conformance.log'),'Actual exchange log drift')
        require(contracts['checks']['trace_contract']['strict_trace']==[0,1],'Trace illustration drift')
        report['trace_exchange']={'counts':exchange['counts'],'kernel_fixture_records':exchange['kernel_fixture_records'],'actual_lean_cases':83994,'mismatches':0}
        # Grammar compatibility is separate from running on every supported interpreter.
        source_paths=list((ROOT/'src').rglob('*.py'))
        for p in source_paths:ast.parse(p.read_text(),feature_version=(3,10))
        report['python_310_grammar_files']=len(source_paths)
        doc=fitz.open(ROOT/'docs/Proof_Path_Theory.pdf');pages=[p.get_text() for p in doc]
        require('Monograph edition 1.8.0' in pages[0],'Stale cover')
        require(len(doc)==approved['pdf_pages'],'Unexpected pagination')
        require(sum(len(p.get_images()) for p in doc)==0,'Rasterized monograph content')
        outside=[]
        for i,p in enumerate(doc):
            for b in p.get_text('blocks'):
                if b[0]<-1 or b[1]<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1:outside.append(i+1)
        require(not outside,'Text outside page bounds')
        require(all(len(t.split())>=60 for t in pages[1:]),'Stray near-empty text page')
        text='\n'.join(pages)
        require(set(map(int,re.findall(r'Figure\s+(\d+)\.',text)))==set(range(1,26)),'Caption sequence mismatch')
        for cmd in ['python scripts/design_figures.py',"python -m pytest -o addopts='' -q",'python scripts/check_recovery_extension.py','python scripts/check_trace_exchange.py','proof-path wire-check trial.problem.json trial.certificate.json']:
            require(cmd in text,'Damaged executable command '+cmd)
        require('pythonscripts/' not in text,'Lost command space')

        sampler=json.loads((ROOT/'data/visual_sampler_1.8.0.json').read_text())
        require(sampler['source_pdf_sha256']==sha(ROOT/'docs/Proof_Path_Theory.pdf'),'Stale sampler source')
        require(sampler['sampler_pdf_sha256']==sha(ROOT/'docs/Proof_Path_Theory_Visual_Sampler.pdf'),'Sampler hash drift')
        with fitz.open(ROOT/'docs/Proof_Path_Theory_Visual_Sampler.pdf') as sample:
            require(len(sample)==8,'Sampler page count')
            require([p.get_text() for p in sample]==[pages[p-1] for p in sampler['source_pages']],'Sampler text mismatch')
        report['sampler']={'pages':8,'source_pages':sampler['source_pages'],'exact_text_match':True}

        questions=['What is the exact claim identifier?','What is its current status and scope?',
                   'Which justifications depend on it?','Which evidence records support or challenge it?',
                   'Which versions and compiled documents contain it?']
        require(any(all(q in t for q in questions) for t in pages),'Ledger questions split')
        report['pdf']={'pages':len(doc),'raster_images':0,'text_outside_pages':0,'sha256':sha(ROOT/'docs/Proof_Path_Theory.pdf')}
        require(not any(ROOT.rglob('*.ttf')) and not any(ROOT.rglob('*.otf')),'Standalone font in package')
        report['status']='PASS'
    except Exception as e:report['status']='FAIL';report['failure']=str(e)
    (ROOT/'data/publication_verification_1.8.0.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
