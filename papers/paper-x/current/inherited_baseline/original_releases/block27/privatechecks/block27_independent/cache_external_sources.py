from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
MATH=Path('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2/workspace/.lake/packages/mathlib')
REV='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
local=['Mathlib/FieldTheory/AbsoluteGaloisGroup.lean', 'Mathlib/FieldTheory/Normal/Defs.lean', 'Mathlib/FieldTheory/Normal/Basic.lean', 'Mathlib/FieldTheory/Galois/Infinite.lean', 'Mathlib/FieldTheory/KrullTopology.lean', 'Mathlib/FieldTheory/Galois/Profinite.lean', 'Mathlib/RingTheory/Invariant/Defs.lean', 'Mathlib/RingTheory/Invariant/Basic.lean', 'Mathlib/RingTheory/Invariant/Profinite.lean', 'Mathlib/RingTheory/Ideal/Pointwise.lean', 'Mathlib/RingTheory/Ideal/Quotient/Operations.lean', 'Mathlib/RingTheory/SimpleModule/Basic.lean', 'Mathlib/Topology/Algebra/Category/ProfiniteGrp/Limits.lean', 'Mathlib/Topology/Algebra/ClopenNhdofOne.lean', 'Mathlib/CategoryTheory/CofilteredSystem.lean', 'Mathlib/Topology/Algebra/MulAction.lean', 'Mathlib/RingTheory/Ideal/GoingUp.lean']
child=json.loads((OUT/"ramification_review/source_paths.json").read_text())
paths=sorted(set(local+[str(Path(x["path"]).relative_to(MATH)) for x in child["sources"] if str(MATH) in x["path"]]))
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=MATH,text=True).strip()==REV
rows=[]
for rel in paths:
 p=MATH/rel; data=p.read_bytes()
 assert data==subprocess.check_output(['git','show',f'{REV}:{rel}'],cwd=MATH),rel
 dst=OUT/'external_sources'/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 rows.append({'path':str(dst.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'original_path':str(p),'upstream_path':rel,'revision':REV,'role':'primary','review_mode':'independent_exact_source','matches_committed_bytes':True})
license=OUT/'external_sources/LICENSE';license.write_bytes((MATH/'LICENSE').read_bytes())
manifest={'source':'Mathlib official repository, pinned runtime Git checkout','revision':REV,'retention_basis':'Apache-2.0 source code; exact-source audit authorized by project task','sources':rows,'license':{'path':str(license.relative_to(ROOT)),'sha256':hashlib.sha256(license.read_bytes()).hexdigest()},'boundary':'These copies preserve exact reviewed theorem and definition sources; Mathlib itself was not rebuilt by this audit.'}
(OUT/'ExternalSourceCache.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('cached authenticated Mathlib sources',len(rows))
