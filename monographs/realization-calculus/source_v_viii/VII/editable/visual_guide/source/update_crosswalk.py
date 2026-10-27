#!/usr/bin/env python3
"""Revise source lines from a supplied final-edition theorem register (no proof edits)."""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAP={
1:['sec:introduction','sec:channels','sec:feshbach'],2:['def:quantum_seed','def:operator_packet'],3:['prop:computational_orbit'],4:['thm:orbit_dimension','cor:schmidt_orbit'],5:['thm:quantum_seed_rank'],6:['cor:cyclic_projectors'],7:['thm:tensor_refinement','cor:tensor_selection'],8:['thm:circuit_path','ex:bell_circuit'],9:['thm:packet_unitarity','thm:path_interference'],10:['thm:invariant_packets'],11:['thm:fixed_leakage','cor:leakage_probability'],12:['thm:moving_frame'],13:['thm:kato_connection','thm:kato_transport'],14:['thm:nonabelian_connection'],15:['thm:nonabelian_connection','cor:bloch_curvature'],16:['thm:operator_packets','thm:dephasing_expectation','cor:measurement_invariance'],17:['thm:channel_blocks','ex:amplitude_damping'],18:['fact:kraus_choi'],19:['thm:kl_obstruction','thm:exact_recovery','ex:bit_flip_code'],20:['thm:kl_obstruction','prop:approximate_kl_meaning'],21:['thm:feshbach_resolvent','thm:feshbach_spectrum'],22:['thm:memory_equation','thm:local_closure'],23:['thm:euclidean_transfer','thm:finite_reflection_positivity'],24:['def:spectral_dimension','prop:finite_spectral_limits'],25:['thm:dispersion_bound'],26:['thm:constraint_closure','prop:physical_compression_trivial'],27:['cor:cyclic_projectors','thm:path_interference','thm:dephasing_expectation'],28:['sec:boundary'],29:['thm:isotypic_projectors','thm:representation_matrix_units'],30:['thm:direct_rotation','thm:short_rotation_convergence'],31:['thm:coherence_projectors','thm:choi_covariance','thm:lindblad_charge'],32:['thm:syndrome_construction','thm:exact_recovery'],33:['def:approximate_kl','prop:approximate_kl_meaning'],34:['thm:self_energy_sign','prop:self_energy_bounds','thm:self_energy_stability'],35:['thm:positive_memory','thm:local_closure'],36:['thm:transfer_logarithm','prop:ground_packet'],37:['thm:heat_trace_convergence','cor:dimension_window'],38:['thm:constraint_closure','thm:constraint_transport','prop:approx_constraint_transport'],39:['thm:bounded_direct_limit','thm:norm_summable_tower','cor:limit_leakage'],40:['thm:reflection_limit','thm:trace_norm_heat','sec:boundary']}
SECTIONS={'sec:introduction':('Section','1','Introduction','1'),'sec:channels':('Section','7','Operator packets and channels','18'),'sec:feshbach':('Section','9','Feshbach dynamics','28'),'sec:boundary':('Section','14','Continuum milestones and exact boundary','45')}
KINDS={'theorem':'Theorem','corollary':'Corollary','proposition':'Proposition','definition':'Definition','standardfact':'Standard fact'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('register',type=Path);args=ap.parse_args();obj=json.loads(args.register.read_text());records=obj.get('records',obj) if isinstance(obj,dict) else obj
 reg={}
 for r in records:
  for label in [r['label']]+r.get('original_labels',[]):
   reg[label.removeprefix('strong:')]=r
 final_labels=obj.get('labels',{}) if isinstance(obj,dict) else {}
 cross=[]
 for filename in ['pages.tex','extended_pages.tex']:
  p=ROOT/'source'/filename;s=p.read_text()
  def repl(m):
   n=int(m[1]);targets=[];refs=[]
   for label in MAP[n]:
    if label in reg:
     r=reg[label];kind=KINDS.get(r.get('environment',r.get('kind','theorem')),'Result');number=r['number'];title=r.get('title','');page=str(r.get('page',''))
    elif 'strong:'+label in final_labels:
     r=final_labels['strong:'+label];kind='Section';number=r['number'];title=r.get('title','');page=str(r['physical_page'])
    elif label in SECTIONS:kind,number,title,page=SECTIONS[label]
    else:raise ValueError('Missing final label: '+label)
    refs.append(kind+' '+number);targets.append({'label':label,'final_label':('strong:'+label) if 'strong:'+label in final_labels else label,'number':number,'kind':kind,'title':title,'traditional_page':page})
   pages=sorted({x['traditional_page'] for x in targets},key=lambda x:int(x) if x.isdigit() else 999)
   line='Traditional edition: '+', '.join(refs)+'; PDF p'+('p' if len(pages)>1 else '')+'. '+', '.join(pages)+'.'
   if n==14:line+=' Range-atlas details: saved v0.6.0 supplement, pp. 2--4.'
   if n==28:line+=' Saved formal scope: v0.6.0 ledger and completion supplement.'
   cross.append({'visual_page':n,'title':m[2],'source_line':line,'targets':targets})
   return r'\vpage{'+str(n)+'}{'+m[2]+'}{'+m[3]+'}{'+line+'}'
  s=re.sub(r'\\vpage\{(\d+)\}\{([^{}]*)\}\{([^{}]*)\}\{[^\n]*\}',repl,s)
  p.write_text(s)
 (ROOT/'provenance/FINAL_THEOREM_REGISTER.json').write_text(json.dumps(obj,indent=2)+'\n')
 (ROOT/'SOURCE_CROSSWALK.json').write_text(json.dumps(sorted(cross,key=lambda r:r['visual_page']),indent=2)+'\n')
 lines=['# Paper VII visual guide source crosswalk','', 'References are to the final traditional edition; PDF pages are physical pages. The saved formal ledger has a separate, narrower contract.','', '| Guide page | Worked page | Final-edition sources |','|---|---|---|']
 for r in sorted(cross,key=lambda r:r['visual_page']):lines.append(f"| V-{r['visual_page']} | {r['title']} | {r['source_line']} |")
 (ROOT/'SOURCE_CROSSWALK.md').write_text('\n'.join(lines)+'\n')
 print('Updated',len(cross),'source lines')
if __name__=='__main__':main()
