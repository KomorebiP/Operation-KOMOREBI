from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'release_package/Komorebi_Paper_II_Release_2026-10-15'
C=ROOT/'paper2_work/computation_final'
paths=[]
paths += list((R/'source/canonical_v1.2.1/code/python').rglob('*.py'))
paths += [R/'source/canonical_v1.2.1/code/python/requirements.lock',R/'source/canonical_v1.2.1/code/python/pyproject.toml']
paths += list((R/'source/canonical_v1.2.1/results').glob('*'))
paths += list((R/'editable/visual_guide/source').glob('*.py'))
paths += list((R/'editable/visual_guide/checks').glob('*.py'))
paths += [R/'editable/visual_guide/checks/EXACT_CHECKS.json']
paths += list((R/'editable/visual_guide/graphics').glob('*.tex'))
paths += list((R/'editable/traditional/visual_graphics').glob('*.tex'))
paths += list((R/'editable/traditional/figure_sources').glob('*.py'))
paths += list((R/'editable/traditional/figure_sources').glob('*.json'))
paths += list((R/'editable/traditional/fonts').glob('*'))
paths += [R/'source/annals_expanded/verification/verify_revised_results.py',R/'source/annals_expanded/PSC_Paper_II_Annals_Human_Edition.tex']
paths += [C/'run_selected.py',C/'launch.py',C/'tools/run_experiment.py',C/'tools/validate_manifest.py']
inputs=sorted(set(str(p.relative_to(ROOT)) for p in paths if p.is_file()))
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONPATH']=str(ROOT/'release_work/runtime/python-venv/lib/python3.12/site-packages')
versions=json.loads(subprocess.check_output([sys.executable,'-c',"import sys,json,importlib.metadata as m;print(json.dumps([{'name':'Python','version':sys.version}]+[{'name':x,'version':m.version(x)} for x in ['numpy','sympy','mpmath','matplotlib']]))"],env=env,text=True))
contract={'claim_id':'PAPER-II-FINAL-BOUNDED-EXAMPLES-2026-10-15','mathematics':{'assertion_tested':'Existing displayed finite examples and numerical records reproduce under their original bounded assertions; current atlas source graphics and data records agree.','coefficient_domain':'Exact integers, Fraction rationals, SymPy symbolic algebra, finite fields and modular quotients; declared NumPy real/complex residuals remain floating.','conventions':'Walks count repeated edges and loops; positive integer edge multiplicities in original Python model. Matrix packet row is output, column input; graph adjacency row is source. Zero-extended finite signals. Smith checks use supplied diagonal/basis data.','inputs':['Canonical v1.2.1 run_experiments and stored full JSON/9-row CSV','Current visual-guide models,118 checks,and22 source plates','Current13 main-figure generator data/assertion paths,rendering hook suppressed','Expanded verifier9 mathematical groups and archived source-integrity group'],'bounds':{'canonical_packet_length':97,'canonical_packet_moduli':[2,3,4,6,8,12],'canonical_refinement_length':128,'canonical_refinement_pairs':[[2,4],[2,8],[3,6],[3,12],[4,8],[4,12],[6,12]],'canonical_Fourier_orders':[2,3,4,5,8,12],'canonical_CRT_length_moduli':[[145,4,3],[193,8,3],[241,4,5],[321,8,5]],'canonical_walk_weight':[0,30],'canonical_inverse_prime_depth':[[2,10],[3,8],[5,7]],'canonical_perturbed_powers':[1,9],'canonical_resolvent_parameter':'3.1+0.7i','canonical_orbit_radius_order':[0.73,16],'exact_visual_checks':118,'visual_walk_weight':[0,24],'visual_literal_walk_weight':[0,10],'visual_inverse_depth':[1,8],'visual_power_defect':[1,8],'main_figure_data_paths':13,'main_walk_weight':[0,36],'main_inverse_cutoff_depth':[1,12],'main_defect_powers':[1,12],'main_smith_radius':0.72,'main_smith_orders':[2,4,8,16],'main_weight_field_grid':[300,300],'atlas_source_byte_comparisons':22,'expanded_groups':{'mathematical':9,'historical_source_integrity':1},'expanded_refinement_dimension':4,'expanded_residue_positions':36,'expanded_inverse_prime_depth':[3,6],'expanded_gluing_prime_exponent':[2,3],'expanded_precision_prime_weight_depth_box':[2,2,3,-2,2],'expanded_Smith_modulus_dimension':[8,3],'expanded_defect_powers':[1,6],'expanded_resolvent_parameter':11},'non_claims':['No universal theorem follows from these bounded checks.','No fresh pytest48-case run; pytest unavailable.','No PDF/PNG regeneration or rendering-quality assertion.','No current manuscript integrity claim from archived annals source check.','No Lean replay by this run.']},'execution_artifacts':inputs,'software':versions,'randomness':{'used':True,'generator':'NumPy default_rng(20260726), PCG64; visual and expanded exact checks deterministic','seed':20260726}}
(C/'contract.json').write_text(json.dumps(contract,indent=2)+'\n')
output='paper2_work/computation_final/run_2026-10-15'
argv=[sys.executable,str(C/'tools/run_experiment.py'),'--root',str(ROOT),'--contract',str(C/'contract.json'),'--output',output,'--timeout','180','--max-output-bytes','1048576','--max-memory-bytes','2147483648','--max-cpu-seconds','120','--max-cores','1','--max-threads','1']
for p in inputs: argv+=['--input',p]
for p in ['RESULT.json','canonical_comparison.json','canonical/results/numerical_results.json','canonical/results/numerical_summary.csv','EXACT_CHECKS.json','atlas_comparison.json','figure_data.json','figure_data_command.py']:
 argv+=['--result',output+'/'+p]
argv += ['--',sys.executable,'paper2_work/computation_final/run_selected.py',output]
(C/'argv.json').write_text(json.dumps(argv,indent=2)+'\n')
(C/'runtime_environment.json').write_text(json.dumps({'python':sys.executable,'extra_pythonpath':env['PYTHONPATH'],'software':versions,'pytest_available':False,'install_performed':False},indent=2)+'\n')
print('Launching bounded replay with',len(inputs),'pinned input artifacts.',flush=True)
raise SystemExit(subprocess.call(argv,cwd=ROOT,env=env))
