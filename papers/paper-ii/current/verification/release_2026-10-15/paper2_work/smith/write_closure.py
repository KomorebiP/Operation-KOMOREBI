from pathlib import Path
import hashlib,json,shutil
root=Path('/workspace/scratch/9f53d520971c')
draft=root/'paper2_work/smith/KomorebiVerification/PaperII'
release=root/'release_package/Komorebi_Paper_II_Release_2026-10-15/formal/current/KomorebiVerification/PaperII'
accepted={'ReleaseSmithDVR':'dvr04','ReleaseSmithRectangular':'rectangular05','ReleaseSmithTransport':'transport03','ReleaseSmithSign':'sign04','ReleaseSmithCharacters':'characters02'}
modules=[]
for name,run in accepted.items():
    source=draft/(name+'.lean')
    receipt_path=root/'paper2_work/smith_checks'/run/'CHECK.json'
    receipt=json.loads(receipt_path.read_text())
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    assert receipt['status']=='PASS' and receipt['source_sha256']==sha and receipt['source_unchanged']
    dest=release/source.name
    assert not dest.exists(),dest
    shutil.copy2(source,dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==sha
    modules.append({'module':'KomorebiVerification.PaperII.'+name,'source':str(dest),'draft':str(source),'sha256':sha,'receipt':str(receipt_path),'elapsed_seconds':receipt['elapsed_seconds'],'max_rss_kib':receipt['max_rss_kib']})
report={
'branch':'General DVR Smith congruence/count and actual sign/character lattice integrality',
'status':'NEW_SOURCES_STRICT_PASS_AND_PROMOTED; aggregate replay pending root',
'modules':modules,
'aggregate_imports':['KomorebiVerification.PaperII.ReleaseSmithTransport','KomorebiVerification.PaperII.ReleaseSmithSign','KomorebiVerification.PaperII.ReleaseSmithCharacters'],
'claims':[
{'manuscript':'thm:smith_congruence / cor:smith_obstruction','declarations':['SmithDVR.quotientAt_card','SmithDVR.multiplyPower_ker_card','SmithDVR.scalarFiber_nonempty_iff','SmithDVR.scalarFiber_card','SmithDVR.rectangularFiberEquiv','SmithDVR.rectangularFiber_nonempty_iff','SmithDVR.rectangularFiber_card','SmithDVR.rectangularMatrix_mulVec','SmithDVR.smithMatrixFiberEquiv','SmithDVR.quotient_smith_identity','SmithDVR.smithCongruenceEquiv','SmithDVR.smith_congruence_nonempty_iff','SmithDVR.smith_congruence_card'],
 'exact_scope':'O is an arbitrary commutative domain DVR, pi irreducible, residue field finite of cardinal q. Actual quotient O/(pi^L), actual integral rectangular M, actual matrix units U,V and equality U M V=diag(pi^s,0). No supplied solvability/count certificate. Columns Fin r + Fin f, rows Fin r + Fin z, so n=r+f,m=r+z, f=n-r. Exponents need not be ordered for congruence/count. L=0, rank zero, zero/free rows and columns are included.',
 'proof':'Derive pi-power ideal=maximalIdeal^L. Mathlib cardQuot_pow_of_prime gives q^L. Compute kernel of O→O/(pi^L), x↦pi^s*x, by cancellation, then image and kernel cardinalities via first isomorphism theorem. Exact inhabited scalar fibres translate to kernel. Explicit rectangular solution equivalence separates active scalar fibres and all free columns. A genuine x↔V^-1 x equivalence carries original fibre to D fibre with target U b, after applying quotient ring hom to U M V=D.',
 'boundary':'No matrix Smith-form existence algorithm is asserted here. The statement takes the supplied Smith form, as the manuscript congruence theorem does. The classical existence standard fact remains a separate mathematical dependency.'},
{'manuscript':'prop:sign_projectors','declarations':['PadicSign.standardLattice','PadicSign.positiveSign','PadicSign.negativeSign','PadicSign.positive_preserves_of_odd','PadicSign.negative_preserves_of_odd','PadicSign.positive_dyadic_not_preserves','PadicSign.negative_dyadic_not_preserves','PadicSign.positive_dyadic_separationWeight','PadicSign.negative_dyadic_separationWeight'],
 'exact_scope':'The literal rational matrices from SmithDyadic act through Rat.castHom on Fin 2→Padic p. The standard lattice is exactly coordinatewise membership in PadicInt.subring p, bundled as a PadicInt p-submodule. For every prime p≠2 both preserve it. At p=2 each fails on e_2, 2E preserves it, and the existing actual least-exponent separationWeight is exactly 1.',
 'proof':'For odd primes, coprime(p,2) gives norm(2)=1 and integral inverse. For p=2, norm(1/2)=2>1 supplies the actual lattice failure. Explicit formulas show twice each projector has integral coordinates. Existing SmithDyadic already proves the rational projector algebra and resultant=2.'},
{'manuscript':'prop:character_integrality','declarations':['IntegralCharacters.power_preserves','IntegralCharacters.characterAverage','IntegralCharacters.characterAverage_preserves','IntegralCharacters.manuscript_character_integrality'],
 'exact_scope':'Any commutative coefficient ring O, field K with an O-algebra structure, K-vector space with compatible O-module structure, O-submodule L, positive N unit in O, primitive Nth root omega∈O, and L stable under the actual K-linear U. The actual field-valued average is (N:K)^-1 sum_k ((algebraMap omega)^-1)^(j*k) U^k. Therefore this applies to every U-stable O-lattice in the manuscript; U^N=I is included by the manuscript wrapper, though not required merely for integrality.',
 'proof':'Primitive root at positive order yields omega a unit. Ring-hom preservation of unit inverses realizes every reciprocal scalar in O. Inductively all actual operator powers preserve L, so the finite O-linear combination does too.'}],
'validation':{'compiler':'Lean 4.34.0-rc2','mathlib_commit':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06','launcher':'paper2_work/tools/check_module.py; serialized; baseline and accepted dependency object hashes authenticated','axioms':'All printed target axioms: propext, Classical.choice, Quot.sound only; no sorryAx','failures_preserved':'All numbered failed run receipts/logs remain under paper2_work/smith_checks; syntax/elaboration/linter iterations only','semantic_review':'Root independently reviewed all five raw current sources and recorded PASS at paper2_work/audit/smith_independent_review.json; compare hashes when finalizing'},
'manuscript_edits':'No additional statement correction needed for these four labels.',
'not_claimed':['Smith normal form existence algorithm','Full independent Mathlib rebuild','Final aggregate/release package replay (root owned)']}
audit=root/'paper2_work/audit'
(audit/'smith_closure.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['GENERAL DVR SMITH / SIGN / CHARACTER CLOSURE','',report['status'],'', 'Import endpoints:']+['  '+x for x in report['aggregate_imports']]
for claim in report['claims']:
    lines += ['',claim['manuscript'],claim['exact_scope'],'Proof: '+claim['proof']]
    if 'boundary' in claim: lines+=['Boundary: '+claim['boundary']]
    lines+=['Declarations: '+', '.join(claim['declarations'])]
lines+=['','Accepted sources and receipts:']
for m in modules: lines += [m['module'], '  '+m['source'], '  sha256 '+m['sha256'], '  '+m['receipt']]
lines+=['','No additional manuscript correction required. All accepted source hashes equal receipt snapshot hashes and promoted file hashes. Only standard Lean axioms in printed target closures. Root owns final aggregate/release replay.']
(audit/'smith_closure.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'promoted':len(modules),'reports':['paper2_work/audit/smith_closure.json','paper2_work/audit/smith_closure.txt']},indent=2))
