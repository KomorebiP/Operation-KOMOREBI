from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'privatechecks/block27_independent'
BASE=Path('/root/.codex/tmp/paperx_block26')
KIT=Path('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2')
MATH=KIT/'workspace/.lake/packages/mathlib'
NAMES=['AbsoluteFrobeniusWitnesses', 'FrobeniusChoiceIndependence', 'NumberFieldPrimeRestriction', 'NumberFieldFrobeniusRestriction', 'UnramifiedFrobeniusUniqueness', 'NumberFieldWitnessIndependence', 'RestrictionEmbeddingConjugacy', 'GeneralArithmeticCoverage']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p,**kw):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),**kw}
allnew=[ROOT/f'lean/PaperX/{n}.lean' for n in NAMES]
assert len(list((BASE/'lean/PaperX').glob('*.lean')))==170
unchanged=[]
for p in sorted((BASE/'lean/PaperX').glob('*.lean')):
 q=ROOT/'lean/PaperX'/p.name
 assert sha(p)==sha(q),f'Predecessor changed: {q}'
 unchanged.append(entry(q))
assert {p.name for p in (ROOT/'lean/PaperX').glob('*.lean')}-{p.name for p in (BASE/'lean/PaperX').glob('*.lean')}=={p.name for p in allnew}
compile_records=[]
for p in allnew:
 r=json.loads((OUT/(p.stem+'.json')).read_text())
 assert r['returncode']==0 and r['sha256']==sha(p),f'Uncompiled final source: {p}'
 compile_records.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'returncode':0,'evidence':str((OUT/(p.stem+'.json')).relative_to(ROOT))})
(OUT/'CompileSummary.json').write_text(json.dumps({'initial_predecessor_object_count':170,'new_source_count':len(allnew),'production_count':178,'predecessor_sources_unchanged':True,'compilations':compile_records},indent=2)+'\n')
axiomrows=[]
for name in ['Inventory']:
 data=json.loads((OUT/(name+'.json')).read_text());assert data['returncode']==0
 for mod,decl,axs in re.findall(r'AUDIT_DECL\s+(\S+)\s+(\S+)\s+\[([^\]]*)\]',data['stdout'],re.S):
  ax=[x.strip() for x in axs.split(',') if x.strip()]
  assert set(ax)<={'propext','Classical.choice','Quot.sound'},(decl,ax)
  axiomrows.append({'module':mod,'declaration':decl,'axioms':ax})
assert len({r['declaration'] for r in axiomrows})==len(axiomrows)
assert {r['module'] for r in axiomrows}=={'PaperX.'+n for n in NAMES}
(OUT/'AxiomSummary.json').write_text(json.dumps({'audit_method':'Lean environment module-identity enumeration and transitive Lean.collectAxioms, including generated declarations and anonymous instances','total_declarations':len(axiomrows),'module_counts':{n:sum(r['module']=='PaperX.'+n for r in axiomrows) for n in NAMES},'axiom_union':sorted({a for r in axiomrows for a in r['axioms']}),'declarations':sorted(axiomrows,key=lambda r:r['declaration'])},indent=2)+'\n')
def strip_comments(s):
 out=[];i=0;depth=0;string=False
 while i<len(s):
  if depth:
   if s.startswith('/-',i):depth+=1;i+=2
   elif s.startswith('-/',i):depth-=1;i+=2
   else:
    if s[i]=='\n':out.append('\n')
    i+=1
  elif string:
   if s[i]=='\\':i+=2
   elif s[i]=='"':string=False;out.append(' ');i+=1
   else:i+=1
  elif s.startswith('/-',i):depth=1;i+=2
  elif s.startswith('--',i):
   k=s.find('\n',i);i=len(s) if k<0 else k
  elif s[i]=='"':string=True;i+=1
  else:out.append(s[i]);i+=1
 return ''.join(out)
scans=[]
for p in allnew:
 matches=re.findall(r'\b(?:axiom|sorry|admit|native_decide|unsafe|extern|implemented_by)\b',strip_comments(p.read_text()))
 assert not matches,(p,matches)
 scans.append(entry(p,forbidden_token_matches=matches))
(OUT/'SourceSafetyScan.json').write_text(json.dumps({'method':'lexically exclude nested block comments, line comments and strings; inspect production sources for forbidden assertion/runtime constructs','sources':scans},indent=2)+'\n')
closure=set()
def visit(p):
 if p in closure:return
 closure.add(p)
 for m in re.findall(r'^\s*(?:public\s+)?import\s+(PaperX\.\w+)',p.read_text(),re.M):visit(ROOT/'lean'/Path(*m.split('.')).with_suffix('.lean'))
for p in allnew:visit(p)
(OUT/'DependencyClosure.json').write_text(json.dumps({'count':len(closure),'sources':[entry(p) for p in sorted(closure)]},indent=2)+'\n')
(OUT/'PredecessorPreservation.json').write_text(json.dumps({'source_count':len(unchanged),'unchanged':True,'sources':unchanged},indent=2)+'\n')
print(json.dumps({'new_sources':len(allnew),'closure_count':len(closure),'axiom_declarations':len(axiomrows),'module_counts':{n:sum(r['module']=='PaperX.'+n for r in axiomrows) for n in NAMES}},indent=2))
