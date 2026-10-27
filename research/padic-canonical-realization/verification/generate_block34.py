from pathlib import Path
import json,re,itertools,zipfile
ROOT=Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'PREDECESSOR_ARCHIVE.json').read_text())
with zipfile.ZipFile(ROOT/meta['path']) as archive:
    prefix=archive.namelist()[0].split('/')[0]+'/'
    pre=json.loads(archive.read(prefix+'verification/theorem_inventory.json'))
    predecessor_root=archive.read(prefix+'lean/KomorebiPadic.lean').decode()
mods=['ResidualBehavior','CanonicalLinearRealization','MinimalMaskRealization','FiniteBehaviorComparison','ResidualMinimalityExamples']
new=[];byfile={}
for mod in mods:
    # These five newly written files have no nested namespaces beyond the explicit map below.
    s=(ROOT/'lean/KomorebiPadic'/f'{mod}.lean').read_text()
    s=re.sub(r'/\-.*?\-/','',s,flags=re.S);s=re.sub(r'--[^\n]*','',s)
    prefix='KomorebiPadic.'+('' if mod=='MinimalMaskRealization' else 'ResidualRealization.')
    names=[prefix+x for x in re.findall(r'\btheorem\s+([A-Za-z_][A-Za-z_0-9\'.]*)',s)]
    byfile[mod]=names;new+=names
inv={'inherited':pre['total'],'new':len(new),'total':pre['total']+len(new),'new_names':new,'names':pre['names']+new,'new_by_file':byfile}
assert len(set(inv['names']))==inv['total']
(ROOT/'verification/theorem_inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
(ROOT/'verification/AllAxioms34.lean').write_text('import KomorebiPadic\n\n'+''.join('#print axioms '+n+'\n' for n in inv['names']))
s=predecessor_root
(ROOT/'lean/KomorebiPadic.lean').write_text('import KomorebiPadic.ResidualMinimalityExamples\n'+s)
lines=['import KomorebiPadic.ResidualMinimalityExamples','open KomorebiPadic KomorebiPadic.ResidualRealization','noncomputable section','']
ws=[list(t) for n in range(3) for t in itertools.product(range(2),repeat=n)]
def ls(w):return '['+','.join(map(str,w))+']'
for u in ws:
 for v in ws:
    value=sum(d*2**i for i,d in enumerate(u+v))%7
    lines.append(f'example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) {ls(u)} {ls(v)} = {value} := by decide +kernel')
lines += ['example : behavior constantOne [] = 1 := constantOne_observation [] 1',
          'example : behavior constantOne [(),(),()] = 1 := constantOne_observation _ 1',
          'example : behavior scaledConstant [] = 1 := by rw [scaledConstant_same_behavior]; exact constantOne_observation [] 1',
          'example : behavior trailingZero [] = 0 := trailingZero_empty',
          'example : behavior trailingZero [0] = 1 := trailingZero_single_zero',
          'example : behavior trailingZero [0,1] = 0 := trailingZero_ends_one [0]',
          'example : behavior trailingZero [1,0,1] = 0 := trailingZero_ends_one [1,0]',
          'example : LinearObservability.State LinearObservability.twiceIdentity ≃ₗ[ZMod 4] ResidualState (behavior LinearObservability.twiceIdentity) := quotientEquivResidual _ LinearObservability.twiceIdentity_reachable',
          'example : Simulation constantOne scaledConstant doubleMap := doubleMap_simulation',
          'end']
(ROOT/'verification/ResidualChecks.lean').write_text('\n'.join(lines)+'\n')
print(json.dumps({'new_theorems':len(new),'all_theorems':inv['total'],'new_modules':len(mods),'concrete_examples':len(ws)**2+9,'by_file':{k:len(v) for k,v in byfile.items()}},indent=2))
