#!/usr/bin/env python3
"""Replay recovered Paper IX examples, evidence indices, and the consolidated TeX.

No Lean compiler, external web source, or historical missing experiment suite is
invoked. All scripts that write beside themselves are run from isolated copies.
"""
from __future__ import annotations
import argparse,collections,hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'original_snapshot'
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(p:Path)->dict[str,str]:return {str(x.relative_to(p)):sha(x)for x in sorted(p.rglob('*'))if x.is_file()}
def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',required=True,type=Path);ap.add_argument('--skip-tex',action='store_true');args=ap.parse_args();out=args.output_dir.resolve()
    for p in [SOURCE,ROOT/'visual_appendix',ROOT/'reading_editions',ROOT/'editorial_evidence']:
        if out==p or p in out.parents:raise SystemExit('Output must be outside preserved source and evidence trees.')
    if out.exists() and any(out.iterdir()):raise SystemExit('Use a new or empty output directory.')
    out.mkdir(parents=True,exist_ok=True);before=snapshot(SOURCE);records=[]
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',SOURCE_DATE_EPOCH='1789171200',FORCE_SOURCE_DATE='1')
    with tempfile.TemporaryDirectory(prefix='paper_ix_original_')as td:
        w=Path(td)
        def run(name:str,argv:list[str],cwd:Path)->Path:
            dest=out/name;dest.mkdir(exist_ok=True);t=time.monotonic()
            with (dest/'stdout.log').open('w')as h:p=subprocess.run(argv,cwd=cwd,env=env,stdout=h,stderr=subprocess.STDOUT,timeout=240)
            records.append({'name':name,'argv':argv,'exit_code':p.returncode,'seconds':time.monotonic()-t,'log_sha256':sha(dest/'stdout.log')})
            if p.returncode:raise RuntimeError('Replay failed: '+str(dest/'stdout.log'))
            return dest
        run('evidence_index',[sys.executable,str(SOURCE/'consolidation/tools/evidence_index.py'),'--source',str(SOURCE),'--output',str(out/'evidence_index')],w)
        # The original indexer has fixed source globals. A wrapper redirects only
        # those filesystem locations into an isolated output, not proof content.
        audit=out/'statement_index';audit.mkdir()
        for name in ['arithmetic_map.json','foundations_map.json','lifting_map.json','regularity_map.json']:
            shutil.copy2(SOURCE/'consolidation/audit'/name,audit/name)
        shutil.copy2(out/'evidence_index/DECLARATIONS.csv',audit/'DECLARATIONS.csv')
        wrapper=w/'run_statement_index.py'
        wrapper.write_text('import importlib.util,sys\nfrom pathlib import Path\nsrc=Path(sys.argv[1]);out=Path(sys.argv[2])\nspec=importlib.util.spec_from_file_location("saved_statement_index",src/"consolidation/tools/statement_index.py")\nm=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)\nm.SOURCE=src;m.MANUSCRIPT=src/"manuscript/consolidated";m.AUDIT=out\nm.main()\n')
        run('statement_index',[sys.executable,str(wrapper),str(SOURCE),str(audit)],w)
        parity={name:sha(audit/name)==sha(SOURCE/'consolidation/audit'/name)for name in ['STATEMENT_INDEX.json','STATEMENT_INDEX.csv']}
        (audit/'SAVED_PARITY.json').write_text(json.dumps(parity,indent=2)+'\n')
        if not all(parity.values()):raise RuntimeError('Recomputed statement index differs from preserved output.')
        for name,rel in [('polynomial_obstructions','native/check_polynomial_obstructions.py'),('mahler_kernel','research/mahler_kernel/check_kernel_formulas.py'),('least_periods','research/least_periods/check_period_candidates.py')]:
            p=w/name;p.mkdir();script=p/Path(rel).name;shutil.copy2(SOURCE/rel,script)
            dest=run(name,[sys.executable,str(script)],p)
            for f in p.glob('*.json'):shutil.copy2(f,dest/f.name)
            records[-1].update({'source_sha256':sha(script),'same_source_as_preserved':sha(script)==sha(SOURCE/rel)})
        comparison=None;typesetting=None
        if not args.skip_tex:
            import fitz
            texout=w/'manuscript'
            dest=run('manuscript',[sys.executable,str(SOURCE/'consolidation/tools/build_manuscript.py'),'--source',str(SOURCE/'manuscript/consolidated'),'--output',str(texout)],w)
            for p in texout.iterdir():
                if p.suffix in ['.txt','.log','.json']:shutil.copy2(p,dest/p.name)
            typesetting=json.loads((dest/'BUILD_REPORT.json').read_text())
            with fitz.open(SOURCE/'manuscript/consolidated/Paper_IX_Consolidated.pdf')as a,fitz.open(texout/'Paper_IX_Consolidated.pdf')as b:
                pages=[]
                for i in range(min(len(a),len(b))):
                    pa,pb=a[i].get_pixmap(alpha=False),b[i].get_pixmap(alpha=False)
                    pages.append({'page':i+1,'same_text':a[i].get_text()==b[i].get_text(),'same_render_at_72_dpi':(pa.width,pa.height,pa.samples)==(pb.width,pb.height,pb.samples)})
                comparison={'original_pages':len(a),'rebuilt_pages':len(b),'all_text_and_render_match':len(a)==len(b)and all(x['same_text']and x['same_render_at_72_dpi']for x in pages),'page_checks':pages}
            (dest/'PAGE_COMPARISON.json').write_text(json.dumps(comparison,indent=2)+'\n')
            if not comparison['all_text_and_render_match']:raise RuntimeError('Original manuscript replay differs from the saved pages.')
        after=snapshot(SOURCE)
        if before!=after:raise RuntimeError('Original snapshot changed during replay.')
        # Summaries below describe the actual source-selected bounded jobs.
        exact=json.loads((out/'polynomial_obstructions/polynomial_obstruction_checks.json').read_text())
        kernel=json.loads((out/'mahler_kernel/kernel_check_results.json').read_text())
        periods=json.loads((out/'least_periods/period_candidates_results.json').read_text())
        evidence=json.loads((out/'evidence_index/EVIDENCE_INDEX.json').read_text())
        statements=json.loads((out/'statement_index/STATEMENT_INDEX.json').read_text())
        report={'status':'PASS','generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'Recovered exact examples, preserved evidence/source indices, and optional original TeX rebuild; no Lean invocation.','source_files_preserved':len(before),'all_original_source_hashes_unchanged':True,'runs':records,'statement_index_identical_to_saved':parity,
          'statement_map':{k:statements[k]for k in ['mapped_statements','resolved_statement_source_links','unique_declarations_referenced','labels_checked','local_references_checked']},
          'polynomial_obstruction_counts':exact['counts'],'mahler_kernel':{'binary_cases':kernel['binary_address_formula']['checked_cases'],'top_edges':kernel['top_edge']['checked_cases'],'cancellation_examples':len(kernel['cancellation_examples'])},'dyadic_displacement_cases':periods['direct_difference_cases'],
          'manuscript_page_comparison':comparison,'typesetting_warning_count':len(typesetting['warnings'])if typesetting else None,'no_lean_run':True,
          'limits':['Saved compiler evidence was checked for integrity, not recompiled.','The complete original historical numerical package was not recovered.','Historical exploratory status labels in old exact scripts are preserved; the consolidated ledger is the current mathematical status.','Four legacy logs have no older hashes; fingerprinting them is not an independent historical comparison.','External Nishibuchi wording and priority were not reauthenticated.']}
        (out/'ORIGINAL_REPLAY_SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['runs','manuscript_page_comparison']},indent=2))
if __name__=='__main__':
    try:main()
    except (OSError,RuntimeError,subprocess.SubprocessError)as exc:raise SystemExit(str(exc))from exc
