#!/usr/bin/env python3
"""Portable entry point for immutable-input, bounded Paper XII Python replay."""
from __future__ import annotations
import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

HERE=Path(__file__).resolve().parent

BOUNDS={
 'integrity':{'archive_files':'all delivered files; actual census in result.json','registered_modules':96,'inherited_axiom_audits':1229,'supplementary_consumers':3,'negative_controls':3},
 'original-finite':{
  'support_masks':{'n':[1,9],'all_masks':True,'quotient_bits': '0 <= bits < 2^min(n,5)'},
  'sampled_fitting_rank':{'fields':[2,3,5,7],'matrix_rows':[1,5],'matrix_columns':[1,5],'samples_per_shape_per_prime':120,'r':'1 through n+1'},
  'adequacy':'one explicit 2x2 S3 model over F7; 13 assertions',
  'group_algebras':{'p_n_pairs':[[2,2],[2,4],[3,3],[5,5]],'exhaustive_elements':True,'dimension':[1,7],'free_rank':[1,7]},
  'patching_support':{'n':[1,13],'quotient_bits':'0 <= bits < 2^min(n,8)','branch_models':6},
  'hecke_packets':{'fields':[5,7,11],'jordan_sizes_a_b':[1,4],'eigenvalues':[1,3]},
  'stable_cores':{'dimension':[1,29],'terminal':'1 through dimension','projection_depth':[2,39],'tail_N':[2,79]},
  'support_transport':{'n':[1,11],'samples_per_n':200},
  'separator_recovery':{'rank':[1,8],'samples_per_rank':100,'multiplicities':[0,5],'field':'QQ'},
  'companion_levels':{'depth':[1,99],'explicit_periodic_scalar_model':True},
  'coefficient_two':'all four elements of F2[C2], plus denominator bookkeeping',
  'source_integrity':'original manuscript labels, refs, bibliography, proof/figure counts'},
 'appendix-exact':{
  'recorded_assertions':31,'F5_local_order3_candidates':625,'F5_local_order2_candidates':25,
  'quotient_window':'total monomial degree < 6 (21 monomials)','adic_prefix_levels':[1,6],
  'fitting':'QQ polynomial ideals for diag(x,y), diag(x^2,y), diag(x,y,1), j=0,1,2; four fiber points; x=y=t base change',
  'CRT':'one exact QQ 5x5 algebra/Jordan example with blocks2and3; empty second packet onJ2',
  'dyadic':'all four elements F2[d]/(d^2), one involution, rank/trace exampleI2',
  'stable_core':'two exact3x3matrices and eight5x5nested projectors','derived_fiber_scalars':[0,1,-1]}
}

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--project',type=Path,default=HERE.parents[1])
 ap.add_argument('--run-id',required=True,help='New label; existing run directories are never overwritten.')
 ap.add_argument('--tasks',nargs='+',choices=list(BOUNDS),default=list(BOUNDS))
 a=ap.parse_args();project=a.project.resolve();bundle=project/'source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix'
 if '/' in a.run_id or '..' in a.run_id:raise ValueError('run-id must be a simple directory name')
 software=[{'name':'Python','version':platform.python_version()}]
 if any(t!='integrity' for t in a.tasks):
  import numpy, sympy, mpmath
  software += [{'name':'NumPy','version':numpy.__version__},{'name':'SymPy','version':sympy.__version__},{'name':'mpmath','version':mpmath.__version__}]
 runner=HERE/'tools/run_experiment.py';validator=HERE/'tools/validate_manifest.py';taskscript=HERE/'replay_task.py'
 common=[runner,validator,taskscript,Path(__file__).resolve()]
 input_files=common+sorted(p for p in bundle.rglob('*') if p.is_file())
 input_files+= [project/'downloads/Paper_XII_Complete_v0.17.1_With_Visual_Appendix.zip',project/'downloads/Paper_XII_Complete_v0.17.1_With_Visual_Appendix.sha256',
               project/'downloads/PSC_Paper_XII_Strengthened_Annals_Edition_Package.zip']
 input_files+= sorted(p for p in (project/'source/original_package/PSC_Paper_XII_Strengthened_Annals_Edition_Package').rglob('*') if p.is_file())
 inputs=[str(p.relative_to(project)) for p in input_files]
 overall=0
 for task in a.tasks:
  nonclaims=['No universal theorem is inferred from finite checks.','No external arithmetic existence, classicality, automorphy, or universal companion construction is established.','No Lean compiler is executed by this Python replay.']
  contract={'claim_id':'PAPER_XII_'+task.upper().replace('-','_'),
   'mathematics':{'assertion_tested':task+' preserved-code bounded audit',
    'coefficient_domain':'SHA256 bytes and lexical/static inventories' if task=='integrity' else 'Exact modular integer matrices over F2,F3,F5,F7,F11; integers/object arrays and rational SymPy; deterministic bounded samples and explicit finite models' if task=='original-finite' else 'Exact integers,F2,F5,and SymPy QQ polynomial/matrix arithmetic',
    'conventions':'Unmodified authoritative script; isolatedcopy output; exact range below.',
    'inputs':inputs,'bounds':BOUNDS[task],'non_claims':nonclaims},
   'execution_artifacts':inputs,'software':software,
   'randomness':{'used':task=='original-finite','generator':'Python random.Random' if task=='original-finite' else '', 'seed':12012 if task=='original-finite' else None}}
  cp=HERE/'contracts'/(a.run_id+'_'+task+'.json');cp.parent.mkdir(exist_ok=True);cp.write_text(json.dumps(contract,indent=2)+'\n')
  out=project/'verification/computation/runs'/a.run_id/task
  cmd=[sys.executable,str(runner),'--root',str(project),'--contract',str(cp),'--output',str(out.relative_to(project)),
       '--result',str((out/'result.json').relative_to(project)),'--timeout','300','--max-output-bytes','4194304',
       '--max-memory-bytes','2147483648','--max-cpu-seconds','240','--max-cores','1','--max-threads','1']
  for p in inputs:cmd+=['--input',p]
  cmd+=['--',sys.executable,str(taskscript),task,'--project',str(project),'--bundle',str(bundle),'--output',str(out)]
  print('Running bounded task:',task,flush=True);r=subprocess.run(cmd)
  overall=max(overall,r.returncode)
  manifest=out/'manifest.json'
  if manifest.exists():
   validated=subprocess.run([sys.executable,str(validator),str(manifest),'--root',str(project)])
   overall=max(overall,validated.returncode)
  if r.returncode:print('Preserved unsuccessful task:',task,flush=True)
 return overall
if __name__=='__main__':sys.exit(main())
