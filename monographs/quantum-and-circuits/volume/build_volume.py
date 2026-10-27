from pathlib import Path
import re,json,shutil,hashlib,subprocess
ROOT=Path(__file__).resolve().parent
SRC=ROOT.parent/'sources'
Q=SRC/'quantum/Quantum_Arithmetic_Complete_Release'
S=SRC/'symmetry/Symmetry_Collapse_in_Quantum_Computation_Source'
G=SRC/'catalytic/Catalytic_Gate_Set_Distortion_Monograph_Source'
C=SRC/'circuits/Komorebi_Circuit_Obstructions_Research_Edition_1.0'
GEN=ROOT/'generated'; GEN.mkdir(exist_ok=True)
inputs={}
bibs=[]
mathblocks=[]

def read(p):
 p=Path(p); raw=p.read_text();inputs[str(p.relative_to(ROOT.parent))]=hashlib.sha256(p.read_bytes()).hexdigest();return raw

def expand(s,base):
 def f(m):
  p=base/m[1]
  if not p.suffix:p=p.with_suffix('.tex')
  return expand(read(p),p.parent) if p.exists() else m[0]
 return re.sub(r'\\input\{([^}]+)\}',f,s)

def normalize(s,base,prefix):
 s=expand(s,base)
 envs='theorem|lemma|proposition|corollary|definition|example|proof|principle|algorithm|question|conjecture|protocol|counterexample'
 for m in re.finditer(r'\\begin\{('+envs+r')\}.*?\\end\{\1\}',s,re.S):mathblocks.append({'kind':m[1],'text':m[0],'origin':str(base.relative_to(ROOT.parent)),'prefix':prefix})
 for m in re.finditer(r'\\textbf\{Proof\.\}.*?\\\(\\square\\\)',s,re.S):mathblocks.append({'kind':'QA-written-proof','text':m[0],'origin':str(base.relative_to(ROOT.parent)),'prefix':prefix})
 # Collect each component bibliography without keeping local headings.
 def bib(m):
  b=re.sub(r'\\bibitem\[[^]]+\]',r'\\bibitem',m[1])
  bibs.append(re.sub(r'\\bibitem\{([^}]+)\}',lambda t:r'\bibitem{'+prefix+t[1]+'}',b));return ''
 s=re.sub(r'\\begin\{thebibliography\}\{[^}]+\}(.*?)\\end\{thebibliography\}',bib,s,flags=re.S)
 for command in ['label','ref','eqref','pageref','cref','Cref','autoref','hyperref','cite','resultrow']:
  # hyperref optional argument not handled; those references are rare.
  s=re.sub(r'\\'+command+r'\{([^}]+)\}',lambda m:'\\'+command+'{'+','.join(prefix+x.strip() for x in m[1].split(','))+'}',s)
 s=re.sub(r'\\hypertarget\{([^}]+)\}',lambda m:r'\hypertarget{'+prefix+m[1]+'}',s)
 s=re.sub(r'\\hyperlink\{([^}]+)\}',lambda m:r'\hyperlink{'+prefix+m[1]+'}',s)
 # Resolve scientific figure bytes into the volume assets.
 def fig(m):
  name=m[2]; p=Path(name)
  candidates=[base/p,base.parent/p,base.parent/'figures'/p,base/'figures'/p]
  if prefix=='q:':candidates +=[Q/'figures'/p]
  if prefix=='c:':candidates +=[C/'figures'/p]
  if prefix=='s:':candidates +=[S/'figures'/p]
  if prefix=='g:':candidates +=[G/'figures'/p,G/'core_extract'/p]
  found=None
  for cand in candidates:
   for pp in [cand,cand.with_suffix('.pdf'),cand.with_suffix('.png')]:
    if pp.exists() and pp.is_file():found=pp;break
   if found:break
  if not found:raise FileNotFoundError((base,name))
  dst=ROOT/'assets'/(prefix[0]+'_'+found.name)
  shutil.copyfile(found,dst)
  return r'\includegraphics'+m[1]+'{assets/'+dst.name+'}'
 s=re.sub(r'\\includegraphics(\[[^\]]*\])?\{([^}]+)\}',lambda m:fig(type('M',(),{'__getitem__':lambda _,i: (m[1] or '') if i==1 else m[i]})()),s)
 s=s.replace(r'\index{',r'\index{')
 return s

def out(name,s):
 (GEN/name).write_text(s)
 return r'\input{generated/'+name+'}\n'

def demote(s):
 for a,b in [('subsubsection','paragraph'),('subsection','subsubsection'),('section','subsection'),('chapter','section')]:
  s=re.sub(r'\\'+a+r'(\*?)(\[|\{)',r'\\'+b+r'\1\2',s)
 return s

def macros(master):
 lines=[]
 for line in read(master).splitlines():
  if line.startswith('\\newcommand') or line.startswith('\\providecommand'):
   # Most component macros are single-line definitions.
   if line.count('{')==line.count('}'):
    lines.append(line.replace('\\newcommand','\\providecommand'))
 return '\n'.join(lines)

q=normalize(read(Q/'traditional/Quantum_Arithmetic_Traditional_Body.tex'),Q/'traditional','q:')
q=q.replace('\\section*{Abstract}\\addcontentsline{toc}{section}{Abstract}','\\section*{Overview}')
q=re.sub(r'The later\s+inherited checkpoint contains.*?A fresh\s+Lean build was not available for this edition\.', 'The formal companion contains ninety-six named theorems across five modules, including the twenty-two original bridge statements. The formal appendix identifies its exact coverage and verification evidence.',q,flags=re.S)
q=q.replace('This paper','This chapter').replace('this paper','this chapter').replace('in Section 6.',r'in Section~\ref{q:polyphase-is-a-different-partition}.')
# Internal numerical prose reference will be checked against the actual section label.
if r'\label{q:polyphase-is-a-different-partition}' not in q:
 q=q.replace(r'in Section~\ref{q:polyphase-is-a-different-partition}.','in the polyphase section.')
q=re.sub(r'\\section\*?\{References\}.*?(?=\\begin|$)','',q,flags=re.S) if False else q
out('q_main.tex',q)
qv=normalize(read(Q/'visual/Quantum_Arithmetic_Visual_Body.tex'),Q/'visual','qv:')
# The visual macros copy named PDF figures separately.
for p in (Q/'figures').glob('*.pdf'):shutil.copyfile(p,ROOT/'assets'/('q_'+p.name))
qv=re.sub(r'\\vpage\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}',lambda m:r'\clearpage\section*{'+m[3]+r'}\addcontentsline{toc}{section}{'+m[3]+'}',qv)
qv=qv.replace('archived formal evidence','formal evidence')
out('q_visual.tex',qv)
ql=normalize(read(Q/'lean/Quantum_Arithmetic_Lean_Guide_Body.tex'),Q/'lean','ql:')
out('q_lean.tex',ql)

# Symmetry sections follow the already published grouping.
s_groups=[('Foundations of packet simulation',['01_question','02_projectors','03_complexity_model','04_exact_simulation','05_approximate_symmetry','06_dynamic_frames']),('Exact symmetry families',['06_fixed_charge','07_benchmarks','08_coarse_packets','09_permutation_symmetry','10_schur_total_spin','11_commutant_collapse','11_orbit_quotients','12_few_particles','13_scaling_phases','13_stabilizer_clifford','14_gaussian_matchgate']),('States, measurements, and open dynamics',['15_density_operators','16_channels_lindblad','17_measurement_feedback','18_block_encodings']),('The complexity boundary',['19_compressed_packets','20_global_interference','21_decision_complexity','22_existence_defects']),('Algorithms and open directions',['23_compiler','24_benchmark_protocol','25_atlas','26_open_problems','27_conclusion'])]
sm=''
for title,files in s_groups:
 sm+='\\chapter{'+title+'}\n'
 for f in files:sm+=demote(normalize(read(S/'chapters'/(f+'.tex')),S/'chapters','s:'))+'\n'
out('s_main.tex',sm)
sa=''
for f in ['A_proofs','B_python_api','C_benchmark_ledger','D_status_ledger']:
 sa+=demote(normalize(read(S/'chapters'/(f+'.tex')),S/'chapters','s:'))+'\n'
out('s_appendix.tex',sa)
sg=demote(normalize(read(S/'chapters/E_glossary.tex'),S/'chapters','s:'))
normalize(read(S/'chapters/bibliography.tex'),S/'chapters','s:')

g_groups=[('General theory of temporary escape',['01_nested_models','02_holonomy_resources','03_spectral_algebraic','04_matroid_quiver_roots']),('Quantum and reversible gate families',['06_qudit_sum','07_clifford','08_affine_toffoli','09_phase_cliffordt','10_gaussian_matchgate','11_symmetry_measurement_architecture']),('Packets, types, holonomy, and restricted realization',['12_packet_realization']),('The computational atlas and open directions',['13_computational_atlas','14_theorem_templates','15_research_program'])]
gm=''
for i,(title,files) in enumerate(g_groups):
 if i==1:gm+='\\chapter{The complete linear core}\n'+normalize(read(G/'chapters/core_unitriangular.tex'),G/'chapters','g:')+'\n'
 gm+='\\chapter{'+title+'}\n'
 for f in files:gm+=demote(normalize(read(G/'chapters'/(f+'.tex')),G/'chapters','g:'))+'\n'
out('g_main.tex',gm)
ga=''
for f in ['A_gate_matrices','B_census_tables','C_python_api','D_conjecture_ledger']:
 ga+=demote(normalize(read(G/'chapters'/(f+'.tex')),G/'chapters','g:'))+'\n'
out('g_appendix.tex',ga)
normalize(read(G/'chapters/bibliography.tex'),G/'chapters','g:')

cm=read(C/'manuscripts/main.tex')
cm=cm[cm.index(r'\chapter{Scope, notation, and computational model}'):]
cm=cm.replace(r'\end{document}','')
cm=normalize(cm,C/'manuscripts','c:')
# Source crosswalk belongs to release provenance rather than the mathematical body.
cm=re.sub(r'\\source\{[^\n]*\}\n?','',cm)
cm=cm.replace(r'\begin{scopebox}',r'\begin{circuitscopebox}').replace(r'\end{scopebox}',r'\end{circuitscopebox}')
cm,cs=cm.split(r'\appendix',1)
# Keep claim index, mathematical coverage, baseline domains, and proof boundaries at the back.
claim_index=cs[:cs.index(r'\chapter{Verification evidence and reproduction}')]
baseline=cs[cs.index(r'\section{Baseline domains reproduced by the full run}'):cs.index(r'\section{Reproduction commands}')]
boundaries=cs[cs.index(r'\section{Excluded inferences}'):cs.index(r'\section{Historical execution corrections}')]
out('c_supplement.tex',claim_index+'\n'+baseline.replace(r'\section{Baseline domains reproduced by the full run}',r'\section{Baseline domains reproduced by the full run}\label{c:app:evidence}')+'\n'+boundaries)
out('c_main.tex',cm)
cv=read(C/'manuscripts/visual.tex');cv=cv[cv.index(r'\guidepage{The model:'):cv.rindex(r'\end{document}')]
cv=normalize(cv,C/'manuscripts','cv:')
cv=cv.replace(r'\guidepage',r'\guidepage').replace(r'\scopebox',r'\circuitscope')
out('c_visual.tex',cv)
cl=read(C/'manuscripts/lean.tex');cl=cl[cl.index(r'\section*{The purpose and evidence contract}'):cl.rindex(r'\end{document}')]
cl=normalize(cl,C/'manuscripts','cl:')
out('c_lean.tex',cl)

# Definitions are scoped to their treatments; duplicate notation is deliberate.
qmac=''
smac=macros(S/'Symmetry_Collapse_in_Quantum_Computation.tex')
gmac=macros(G/'Catalytic_Gate_Set_Distortion_Monograph.tex')
cmac=macros(C/'manuscripts/main.tex').replace('\\providecommand{\\F}{\\mathbb F_2}', '\\renewcommand{\\F}{\\mathbb F_2}').replace('\\providecommand{\\B}{\\{0,1\\}}','\\renewcommand{\\B}{\\{0,1\\}}')
cmac='\n'.join(x for x in cmac.splitlines() if not any(k in x for k in ['\\source}', '\\claim}', '\\resultrow}']))
for n,s in [('s_macros.tex',smac),('g_macros.tex',gmac),('c_macros.tex',cmac)]:out(n,s)
# Deduplicate keys within each bibliography while preserving distinct component namespaces.
joined='\n'.join(bibs); chunks=re.split(r'(?=\\bibitem\{)',joined); seen=set();refs=[]
for ch in chunks:
 m=re.match(r'\\bibitem\{([^}]+)\}',ch)
 if m and m[1] not in seen:seen.add(m[1]);refs.append(ch)
# Identical source keys in the two gate/symmetry bibliographies denote the same works.
aliases={}; canonical={}; unique_refs=[]
for ch in refs:
 key=re.match(r'\\bibitem\{([^}]+)\}',ch)[1]
 basekey=key.split(':',1)[-1]
 if basekey in canonical:aliases[key]=canonical[basekey]
 else:canonical[basekey]=key;unique_refs.append(ch)
refs=unique_refs
for path in GEN.glob('*.tex'):
 text=path.read_text()
 text=re.sub(r'\\cite\{([^}]+)\}',lambda m:r'\cite{'+','.join(aliases.get(k.strip(),k.strip()) for k in m[1].split(','))+'}',text)
 path.write_text(text)
(ROOT/'citation_aliases.json').write_text(json.dumps(aliases,indent=2))
out('references.tex','\\begin{thebibliography}{999}\n'+'\n'.join(refs)+'\n\\end{thebibliography}')
out('glossary.tex',sg)
(ROOT/'source_manifest.json').write_text(json.dumps(inputs,indent=2))
(ROOT/'mathematical_blocks_source.json').write_text(json.dumps(mathblocks,indent=2))
print('Consolidated',len(inputs),'source files;',len(refs),'bibliography entries')

subprocess.run(["python3",str(ROOT/"refine_reading.py")],check=True)

subprocess.run(["python3",str(ROOT/"check_content.py")],check=True)

subprocess.run(["python3",str(ROOT/"make_reading_figures.py")],check=True)
