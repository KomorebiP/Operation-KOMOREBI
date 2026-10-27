from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
MATH=Path('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2/workspace/.lake/packages/mathlib')
REV='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
local=[
'Mathlib/FieldTheory/AbsoluteGaloisGroup.lean','Mathlib/FieldTheory/Normal/Defs.lean','Mathlib/FieldTheory/Normal/Basic.lean','Mathlib/FieldTheory/IsAlgClosed/Basic.lean','Mathlib/FieldTheory/KrullTopology.lean',
'Mathlib/RepresentationTheory/Basic.lean','Mathlib/RepresentationTheory/Intertwining.lean','Mathlib/RepresentationTheory/Subrepresentation.lean','Mathlib/RepresentationTheory/Irreducible.lean','Mathlib/RepresentationTheory/Character.lean',
'Mathlib/RingTheory/Valuation/RamificationGroup.lean','Mathlib/RingTheory/Valuation/ValuationSubring.lean','Mathlib/RingTheory/LocalRing/ResidueField/Basic.lean','Mathlib/NumberTheory/Padics/RingHoms.lean','Mathlib/NumberTheory/Padics/PadicIntegers.lean',
'Mathlib/NumberTheory/Cyclotomic/Basic.lean','Mathlib/NumberTheory/NumberField/Cyclotomic/Galois.lean','Mathlib/NumberTheory/NumberField/Cyclotomic/Ideal.lean','Mathlib/NumberTheory/LSeries/PrimesInAP.lean',
'Mathlib/RingTheory/Ideal/GoingUp.lean','Mathlib/RingTheory/Ideal/Defs.lean','Mathlib/RingTheory/Ideal/Over.lean','Mathlib/RingTheory/Ideal/Pointwise.lean','Mathlib/RingTheory/SimpleModule/Basic.lean']
child=json.loads((OUT/'stabilizer_source/SourceManifest.json').read_text())
paths=sorted(set(local+[x['relative_path'] for x in child['sources']]))
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
