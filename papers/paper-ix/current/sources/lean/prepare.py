#!/usr/bin/env python3
from pathlib import Path
import argparse,csv,hashlib,json,re,zipfile,collections,subprocess
from fontTools.ttLib import TTFont
H=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);a=ap.parse_args();B=a.source.resolve()
for n in ['chapters','generated','excerpts','qa']: (H/n).mkdir(exist_ok=True)
rows=list(csv.DictReader((H/'audit/reconciled/DECLARATIONS.csv').open()));stmt=json.loads((B/'consolidation/audit/STATEMENT_INDEX.json').read_text())
def sha(x):return hashlib.sha256(x).hexdigest()
def blob(p):
 if '!'in p or'::'in p:
  z,n=re.split(r'!|::',p,maxsplit=1)
  with zipfile.ZipFile(B/z)as f:return f.read(n)
 return (B/p).read_bytes()
def esc(s):
 return ''.join({'\\':r'\textbackslash{}','_':r'\_','%':r'\%','&':r'\&','#':r'\#','$':r'\$','{':r'\{','}':r'\}','^':r'\textasciicircum{}','~':r'\textasciitilde{}'}.get(c,c)for c in s)
picks=[
('packet','foundations','ResiduePackets','packet_reconstruction'),('triangular','foundations','Triangular','solve_unique'),('denominator','foundations','Triangular','solve_denominator_integral'),('egf','foundations','EGFCoordinates','egf_product'),('mahler','foundations','FiniteMahler','finite_mahler_reconstruction'),('unit','foundations','FiniteUnits','decomposition_unique'),('crt','foundations','CRTPackets','addressEquiv'),
('precision','arithmetic','GlobalEulerBoundary','precision'),('global_bound','arithmetic','AllResidueEuler','global_unnormalized_bound'),('period','arithmetic','PeriodFromDifferences','prime_power_period'),('degree_shift','arithmetic','NishibuchiCompletion','original_degree_shift'),('conjecture','arithmetic','NishibuchiCompletion','conjecture_3_9'),
('odd_euler','dyadic','OddEulerReconstruction','odd_euler_reconstruction'),('odd_tail','dyadic','OddEulerReconstruction','odd_euler_supercongruence'),('dyadic_reconstruct','dyadic','DyadicReconstruction','dyadic_reconstruction'),
('finite_affine','affine','AffineObstructionCore','finite_affine_obstruction'),('representative','affine','AffineObstructionCore','obstruction_representative_independent'),('shared','affine','AffineSharedCorrection','joint_lift_iff_class_eq'),('fiber','affine','FiniteFiberCounts','fiberEquivKernel'),('fiber_card','affine','FiniteFiberCounts','fiber_card'),
('taylor','polynomial','PolynomialTaylor','taylor_dvd'),('next_digit','polynomial','PolynomialObstruction','next_level_iff_digit'),('poly_obstruction','polynomial','PolynomialObstruction','finite_polynomial_obstruction'),('digit_lifts','polynomial','PolynomialLiftCounts','digitEquivLifts'),('lift_count','polynomial','PolynomialLiftCounts','finite_polynomial_lift_count'),
('tower','towers','PolynomialIntegerTower','exists_compatible_tower_strong'),('padic_root','towers','PolynomialPadicLift','exists_padic_root_with_tower'),('unique_root','towers','PolynomialPadicUnique','exists_unique_padic_root'),
('chart','parameters','PolynomialParameterChart','parameterHomeomorph'),('prescribed','parameters','PolynomialPrescribedSystem','prescribed_equation_iff'),('prescribed_root','parameters','PolynomialPrescribedPadicTower','exists_prescribed_padic_root_with_tower'),('prescribed_unique','parameters','PolynomialPrescribedPadicTower','exists_unique_prescribed_padic_root'),
('inverse','weighted','PolynomialWeightedInverse','bounded_inverse_iff_certificate'),('contraction','weighted','PolynomialPadicContraction','exists_unique_fixedPoint'),('weighted_root','weighted','PolynomialWeightedLift','exists_weighted_root'),('motion','weighted','PolynomialRootMotion','exists_unique_root_motion'),('joint_motion','weighted','PolynomialJointMotion','exists_joint_root_motion'),
('actual_derivative','regularity','PolynomialAnalyticEvaluation','hasStrictFDerivAt_evalSystem'),('analytic_inverse','regularity','PolynomialAnalyticInverse','analyticAt_inverse'),('inverse_block','regularity','PolynomialAnalyticBlocks','inverse_solved_zero'),('analytic_implicit','regularity','PolynomialAnalyticImplicit','exists_analytic_implicit'),('selection','regularity','PolynomialAnalyticSelection','continuous_selection_regularity'),('integral','regularity','PolynomialRegularityIntegral','exists_analytic_integral_implicit')]
# These sharp arithmetic sources are selected from the manuscript's exact named references.
for id,label,short in [('sharp_displacement','thm:arith-exact','normalized_exact_displacement'),('least_period','cor:arith-least-period','period_iff_dvd'),('sharp_tail','thm:arith-sharp-tower','dyadic_supercongruence_sharp'),('isometry','thm:arith-isometry','existsUnique_isometry')]:
 s=next(x for x in stmt['statements']if x['label']==label);r=next(x for x in s['references']if x['declaration'].split('.')[-1]==short);mod=Path(r['source']).stem;picks.append((id,'dyadic',mod,short))
font=TTFont(subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans Mono'],text=True).strip());cmap={k for t in font['cmap'].tables for k in t.cmap}
mathfont=TTFont(subprocess.check_output(['fc-match','-f','%{file}','Latin Modern Math'],text=True).strip());mathcmap={k for t in mathfont['cmap'].tables for k in t.cmap}
fallback=set()
records=[]
for id,ch,mod,short in picks:
 candidates=[r for r in rows if r['module']==mod and r['qualified_name'].split('.')[-1]==short];assert candidates,(id,mod,short)
 # Prefer the current source if a historical version remains; source rows retain both in the full catalog.
 candidates.sort(key=lambda r:(r['frontier_classification']=='current_polynomial',r['canonical_source']),reverse=True);r=candidates[0];data=blob(r['canonical_source']);assert sha(data)==r['source_sha256'];lines=data.decode().splitlines(keepends=True)
 match=[i for i,l in enumerate(lines)if re.search(r'\b(?:theorem|lemma|def|abbrev)\s+'+re.escape(short)+r'(?=[\s(:{])',l)];assert len(match)==1,(id,match);start=match[0];end=start+1
 while end<len(lines):
  l=lines[end]
  if re.match(r'^(?:@\[|theorem |lemma |def |abbrev |variable |namespace |end |/--|omit |#print )',l):break
  end+=1
 while end>start and not lines[end-1].strip():end-=1
 raw=''.join(lines[start:end]);(H/'excerpts'/f'{id}.lean.txt').write_text(raw)
 # The rendered text retains every source character; XeTeX code glyph fallback added later if required.
 render=''
 for c in raw:
  if c in '\\{}':render+=r'\CodeChar{'+str(ord(c))+'}'
  elif ord(c)>127 and ord(c)not in cmap:
   fallback.add(ord(c));assert ord(c)in mathcmap or ord(c)in{0x29F8,0x2B1D},hex(ord(c));render+=r'\CodeSymbol{'+f'{ord(c):X}'+'}'
  else:render+=c
 (H/'excerpts'/f'{id}.render.txt').write_text(render)
 rec={'id':id,'chapter':ch,'module':mod,'declaration':r['qualified_name'],'source':r['canonical_source'],'source_sha256':r['source_sha256'],'start_line':start+1,'end_line':end,'excerpt_sha256':sha(raw.encode()),'line_count':end-start,'exact_contiguous':True,'ambient_variable_lines':[l.rstrip()for l in lines[:start]if l.startswith('variable ')]};records.append(rec)
 (H/'generated'/f'excerpt_{id}.tex').write_text(r'\label{ex:'+id+r'}\source{'+r['canonical_source']+r'}'+'\n'+r'{\footnotesize Lines '+str(start+1)+'--'+str(end)+r'; \code{'+r['qualified_name']+r'}.}\par'+'\n')
(H/'audit/GLYPH_FALLBACKS.json').write_text(json.dumps([f'U+{x:04X}'for x in sorted(fallback)],indent=2)+'\n')
(H/'audit/EXCERPTS.json').write_text(json.dumps(records,indent=2)+'\n')
# Full source catalog. Names are listed under an exact canonical source and namespace.
by=collections.defaultdict(list)
for r in rows:by[(r['canonical_source'],r['source_sha256'])].append(r)
t=[r'\section{Complete named-source catalog}\label{sec:catalog}',r'This catalog contains all 1,876 declaration/source-version rows from the preserved frontier inventory, grouped under 199 canonical source files. The paired CSV retains every exact-copy location, role, source version, frontier, and inherited axiom closure. A theorem command, a control, a construction, and a source version are different quantities. A new name does not establish a new mathematical result.']
for j,((source,h),rr)in enumerate(sorted(by.items())):
 t += [r'\subsection*{'+esc(Path(source).stem)+r'}',r'\source{'+source+r'}',r'{\footnotesize SHA-256: \code{'+h+r'}; '+str(len(rr))+r' rows.}\par',r'\begingroup\small']
 namespaces=collections.defaultdict(list)
 for r in rr:namespaces[r['qualified_name'].rsplit('.',1)[0]].append(r)
 for namespace,nn in sorted(namespaces.items()):
  t += [r'\textbf{Namespace:} \code{'+namespace+r'}\par']
  for r in sorted(nn,key=lambda r:r['qualified_name']):
   t += [r'\noindent\code{'+r['qualified_name'].split('.')[-1]+r'} {\scriptsize ('+esc(r['kind'])+'; '+esc(r['role'])+(' ; '+r['source_version_count_for_name']+' source versions'if int(r['source_version_count_for_name'])>1 else'')+r')}\par']
 t += [r'\endgroup']
(H/'generated/catalog.tex').write_text('\n'.join(t)+'\n')
# Frontiers table does not sum repeated inherited modules.
t=[r'\section{The retained verification frontiers}\label{sec:frontiers}',r'Each row is one retained compilation checkpoint. Later polynomial rows carry earlier sources, so their counts must not be added. Compilation is historical; the source/log reconciliation was freshly repeated for this edition.',r'\begin{longtable}{p{.36\linewidth}rrrrr}',r'\toprule Frontier & Proof & Support & Contracts & Negative & Audits\\\midrule\endhead']
e=json.loads((H/'audit/reconciled/EVIDENCE_INDEX.json').read_text())
for f in e['frontiers']:
 g=f['source_groups'];count=lambda key:g.get(key,{}).get('files',0)
 t.append(esc(f['frontier'])+' & '+' & '.join(map(str,[count('modules'),count('control_support'),count('contracts'),count('negative_controls')or count('controls'),f['axiom_closures']]))+r'\\')
t.append(r'\bottomrule\end{longtable}');(H/'generated/frontiers.tex').write_text('\n'.join(t)+'\n')
print({'excerpts':len(records),'exact_lines':sum(r['line_count']for r in records),'source_catalog_files':len(by),'catalog_rows':len(rows)})

chapter_for={}
for st in stmt['statements']:
 label=st['label']
 if ':arith-'in label:
  ch='arithmetic'if any(x in label for x in ['euler','precision','nishibuchi','divisor-base','newton-period','denominator','lucas-window','normalization-loss','window-period'])else'dyadic'
 elif any(x in label for x in ['residue-reconstruction','egf-coordinates','hurwitz-product','triangular-foundation','filtered-foundation','mahler-foundation','unit-modes-foundation','finite-unit-foundation','companion-foundation','crt-foundation']):ch='foundations'
 elif any(x in label for x in ['affine-obstruction','representative-independence','common-correction','shared-polynomial']):ch='affine'
 elif any(x in label for x in ['polynomial-taylor','finite-polynomial-obstruction','lift-torsor-count']):ch='polynomial'
 elif any(x in label for x in ['smooth-tower','smooth-padic-root','smooth-coefficient-stability']):ch='towers'
 elif any(x in label for x in ['continuous-parameter-chart','prescribed-']):ch='parameters'
 elif any(x in label for x in ['weighted-lifting','coefficient-motion','joint-deformation','weighted-boundary','motion-boundary']):ch='weighted'
 else:ch='regularity'
 chapter_for[label]=ch
t=[r'\section{Manuscript-to-guide navigation}\label{sec:crosswalk}',r'The preserved consolidated manuscript labels identify each mapped result. The page locators below refer to this guide. Every one of the 62 indexed statements has a teaching destination, and all 202 source links are retained in the paired JSON/CSV. Source correspondence is separately limited for the restored Bernoulli example.',r'\begin{longtable}{p{.55\linewidth}p{.28\linewidth}r}',r'\toprule Manuscript label & Teaching chapter & Page\\\midrule\endhead']
for st in stmt['statements']:
 label=st['label'];ch=chapter_for[label];t.append(r'\code{'+label+r'} & \nameref{sec:'+ch+r'} & \pageref{sec:'+ch+r'}\\')
t += [r'\code{ex:arith-bernoulli} & Classical derivation; formal boundary & \pageref{sec:reading}\\',r'\bottomrule\end{longtable}']
(H/'generated/crosswalk.tex').write_text('\n'.join(t)+'\n')
(H/'audit/CROSSWALK.json').write_text(json.dumps([{'manuscript_label':st['label'],'guide_chapter':chapter_for[st['label']],'guide_section_label':'sec:'+chapter_for[st['label']],'source_links':st['references']}for st in stmt['statements']],indent=2)+'\n')
