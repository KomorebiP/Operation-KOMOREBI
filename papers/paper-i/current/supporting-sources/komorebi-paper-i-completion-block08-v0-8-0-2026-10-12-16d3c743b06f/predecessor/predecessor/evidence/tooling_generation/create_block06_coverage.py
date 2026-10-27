from pathlib import Path
import json
r=Path('/mnt/data/Komorebi_Paper_I_Completion_Block06_v0.6.0_2026-10-11')
s=(r/'predecessor/scripts/update_coverage.py').read_text()
s=s.replace("root=Path(__file__).resolve().parents[1]", "root=Path(__file__).resolve().parents[1]\naccepted=json.loads((root/'evidence/final_audit/verification.json').read_text())\nassert accepted['status']=='PASS', 'Coverage acceptance requires completed verification'\nassert len(accepted['same_kernel_modules_replayed'])==42")
s=s.replace('block05','block06').replace('0.5.0','0.6.0').replace('18 covered, 31 partial','19 covered, 30 partial')
(r/'scripts/update_coverage.py').write_text(s)
base='Komorebi.PaperICompletion6.'
names=[
'ScalarExtension.minpoly_baseChange','ScalarExtension.minpoly_natDegree_baseChange',
'ScalarExtension.minpoly_eq_charpoly_baseChange_iff','ScalarExtension.hasCyclicVector_baseChange_iff',
'ScalarExtension.hasCyclicVector_iff_extended_spectral_multiplicities_one',
'PrimaryCyclicCriterion.hasCyclicVector_iff_polynomialModule_cyclic',
'PrimaryCyclicCriterion.submodule_cyclic_of_hasCyclicVector',
'PrimaryCyclicCriterion.hasCyclicVector_iff_nonzero_primary_cyclic',
'OneInvariantFactor.HasOneInvariantFactor','OneInvariantFactor.factor_eq_minpoly',
'OneInvariantFactor.hasCyclicVector_iff_oneInvariantFactor',
'OneInvariantFactor.quotientVectorEquiv_intertwines',
'OneInvariantFactor.toMatrix_quotientCompanionBasis',
'OneInvariantFactor.exists_companion_basis_of_cyclic',
'SixWayCyclicCriterion.cyclic_iff_invariantFactor_count_one',
'SixWayCyclicCriterion.cyclic_six_way','SixWayCyclicCriterion.cyclic_six_way_algebraicClosure']
d={'schema':'paper-i-coverage-delta/0.6.0','updates':[{'stable_id':'PSC-I-C-CYCLIC-MATRIX','status':'covered','scope_and_remaining_work':
'Block 06 closes the exact six-way criterion for a nonzero finite-dimensional operator over an arbitrary field. The final List.TFAE includes actual cyclicity, canonical seed rank one, cyclicity of every nonzero intrinsic primary component, an actual monic positive-degree one-invariant-factor presentation, minpoly=charpoly, and one-dimensional eigenspaces at every spectral value of the literal tensor extension to AlgebraicClosure k. Minimal-polynomial preservation and cyclicity preservation/descent are proved, not supplied as hypotheses. The one-factor presentation has a constructed basis in which the original operator is the standard companion matrix; its factor is proved to be the minimal polynomial. A separate theorem proves that any actual nonconstant invariant-factor chain has exactly one factor iff the operator is cyclic. This is a mathematical existence and equivalence theorem, not an executable normal-form algorithm or a full sorted invariant-factor construction for arbitrary noncyclic operators. The nonzero-space guard is retained in the six-way statement. Legacy conditional wrappers are preserved unchanged for compatibility, but the new public criterion needs no decomposition, multiplicity, polynomial-preservation, spectral, or seed-number certificates.',
'add_declarations':[base+x for x in names]}]}
(r/'coverage/DELTA_108.json').write_text(json.dumps(d,indent=2)+'\n')
