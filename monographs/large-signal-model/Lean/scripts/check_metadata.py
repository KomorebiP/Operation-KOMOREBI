#!/usr/bin/env python3
"""Check source/register correspondence and axiom-parser failure behavior.
These are metadata/tooling tests, not additional mathematical proofs.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    records = []
    def record(name: str, condition: bool) -> None:
        require(condition, name)
        records.append({'name': name, 'passed': True})
    decls = json.loads((ROOT/'DECLARATIONS.json').read_text())
    by_name = {x['name']: x for x in decls}
    counts = json.loads((ROOT/'RELEASE_COUNTS.json').read_text())
    record('4454 unique named declarations', len(decls) == len(by_name) == counts['named_declarations'] == 4454)
    for d in decls:
        line = (ROOT/d['file']).read_text().splitlines()[d['line']-1]
        require(re.search(r'\b'+d['kind']+r'\s+(?:\w+\.)*'+re.escape(d['name'].split('.')[-1])+r'\b', line) is not None,
                f'incorrect source location: {d["name"]}')
    record('Every declared source location resolves', True)
    actual_count = 0
    for path in (ROOT/'KomorebiLSM').glob('*.lean'):
        actual_count += len(re.findall(r'^[ \t]*(?:@\[[^\]\n]*\][ \t]*)*(?:noncomputable[ \t]+)?(?:theorem|def|structure|abbrev|inductive|instance)[ \t]+\w+',
                                     path.read_text(), re.M))
    record('Full named-source declaration count agrees', actual_count == len(decls))
    record('2887 named theorems, 331 in example modules',
           sum(d['kind']=='theorem' for d in decls)==counts['named_theorems']==2887 and
           sum(d['kind']=='theorem' and d['module'] in ['Block10Examples', 'Block11Examples', 'Block12Examples', 'Block13Examples', 'Block14Examples', 'Block2Examples', 'Block3Examples', 'Block4Examples', 'Block5Examples', 'Block6Examples', 'Block7BoundaryExamples', 'Block7Examples', 'Block8ApproximationExamples', 'Block8Examples', 'Block9Examples', 'Examples'] for d in decls)==counts['example_theorems']==331)
    cover = json.loads((ROOT/'COVERAGE.json').read_text())
    original = json.loads((ROOT/'source/PROOF_REGISTER_1.0.0.json').read_text())
    origins = {x['id']: x for x in original['entries']}
    record('All 87 manuscript propositions appear exactly once',
           sorted(x['proposition'] for x in cover['entries'])==list(range(1,88)))
    for entry in cover['entries']:
        require(entry['theory_statement_proof_sha256'] == origins[entry['proposition']]['statement_proof_sha256'],
                f'changed manuscript linkage: {entry["proposition"]}')
        for target in entry['lean_targets']:
            require(target['name'] in by_name, 'missing Lean target')
            require(all(target[k]==by_name[target['name']][k] for k in ('kind','file','line','module')),
                    'inconsistent Lean target metadata')
            require(target['source_sha256']==digest(ROOT/target['file']), 'stale Lean target hash')
    record('Every coverage target and statement hash matches', True)
    record('Coverage matches reviewed complete/partial/unformalized IDs',
           [x['proposition'] for x in cover['entries'] if x['status']=='complete']==[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87]
           and [x['proposition'] for x in cover['entries'] if x['status']=='partial']==[]
           and [x['proposition'] for x in cover['entries'] if x['status']=='not_formalized']==[])
    lineage = json.loads((ROOT/'SOURCE_LINEAGE.json').read_text())
    record('Frozen source files match declared lineage',
           all(digest(ROOT/'source'/name)==sha for name,sha in lineage['source_files'].items()))
    record('Original manuscript matches its original proof register hash',
           digest(ROOT/'source/FOUNDATIONS_1.0.0.md')==original['source_sha256'])
    audit_names = re.findall(r'^#print axioms (\S+)$',(ROOT/'AxiomAudit.lean').read_text(),re.M)
    record('Axiom commands audit exactly the declaration inventory',
           len(audit_names)==len(set(audit_names)) and set(audit_names)==set(by_name))
    spec = importlib.util.spec_from_file_location('lsm_verify',ROOT/'scripts/verify.py')
    require(spec is not None and spec.loader is not None, 'unable to load verifier')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    record('Axiom-free parser record accepted', mod.parse_axioms("'x' does not depend on any axioms",{'x'})=={'x':[]})
    record('Standard-axiom parser record accepted',
           set(mod.parse_axioms("'x' depends on axioms: [propext, Classical.choice, Quot.sound]",{'x'})['x'])==mod.ALLOWED_AXIOMS)
    for name,text,expected in [
        ('Placeholder dependency rejected',"'x' depends on axioms: [sorryAx]",{'x'}),
        ('Custom dependency rejected',"'x' depends on axioms: [inventedAssumption]",{'x'}),
        ('Missing declaration rejected',"'x' does not depend on any axioms",{'x','y'}),
        ('Extra declaration rejected',"'x' does not depend on any axioms\n'y' does not depend on any axioms",{'x'}),
        ('Duplicate record rejected',"'x' does not depend on any axioms\n'x' does not depend on any axioms",{'x'}),
        ('Truncated dependency record rejected',"'x' depends on axioms: [propext",{'x'}),
    ]:
        rejected=False
        try: mod.parse_axioms(text,expected)
        except ValueError: rejected=True
        record(name,rejected)
    record('All 155 inherited proof files are byte-identical',
           len(lineage['inherited_proof_files'])==155 and
           all(digest(ROOT/name)==h for name,h in lineage['inherited_proof_files'].items()))
    pred=lineage['predecessor_archive']
    record('Preserved predecessor source snapshot matches its hash',digest(ROOT/pred['path'])==pred['sha256'])
    import zipfile
    with zipfile.ZipFile(ROOT/pred['path']) as z:
        entries=[n for n in z.namelist() if n=='Large_Signal_Model/Lean/DECLARATIONS.json']
        require(len(entries)==1, 'ambiguous predecessor inventory')
        previous=json.loads(z.read(entries[0]))
        record('All 2697 inherited declaration records are unchanged',
               len(previous)==2697 and all(by_name[d['name']]==d for d in previous))
    root_modules=re.findall(r'^import KomorebiLSM\.(\w+)$',(ROOT/'KomorebiLSM.lean').read_text(),re.M)
    record('All 254 proof modules are imported and verified in the same order',
           root_modules==mod.MODULES and len(root_modules)==len(set(root_modules))==254 and
           set(root_modules)=={p.stem for p in (ROOT/'KomorebiLSM').glob('*.lean')})
    record('All 183 negative controls are outside the proof import graph',
           len(list((ROOT/'negative_controls').glob('*.lean')))==counts['negative_controls']==183 and
           all('negative_controls' not in p.read_text() for p in (ROOT/'KomorebiLSM').glob('*.lean')))
    record('No old complete coverage entry lost',
           all(cover['entries'][k-1]['status']=='complete' for k in [1,2,3,4,5,6,7,8,9,10,12,22,26,27,28,29,30,36,38,39,40,41,42,43,44]))
    record('New tree and completion targets resolve',
           all('Komorebi.LSM.'+n in by_name for n in [
               'PacketTree.completeCut_branch','PacketTree.complete_cut_energy',
               'invariantSequence_exists_stable','predictiveCompletion_coordinate_realization',
               'predictiveCompletion_le_competing_summary',
               'Block2Examples.completion_is_exactly_two_coordinate_rows']))
    record('New Bayesian and joint refinement capstones resolve',
           all('Komorebi.LSM.'+n in by_name for n in [
               'FiniteBayes.bayesian_coarsening_iff',
               'FiniteBayes.bayesian_coarsening_matrix_defect',
               'FiniteBayes.one_block_commutes',
               'FinitePartitions.refinement_stabilizes',
               'FinitePartitions.jointRefinement_termination',
               'FinitePartitions.joint_closed_iff',
               'FinitePartitions.coarsest_jointly_closed',
               'Block3Examples.six_state_actual_completion',
               'Block3Examples.six_state_semantic_minimality']))
    record('P9 and P12 coverage records retain actual-domain restrictions',
           all(cover['entries'][k-1]['status']=='complete' for k in (9,12)) and
           'surjective' in cover['entries'][11]['scope'] and
           'one-block' in cover['entries'][11]['scope'] and
           'nontrivial' in cover['entries'][8]['scope'] and
           'noncomputable' in cover['entries'][8]['scope'])
    record('Independent matrix-defect and zero-evidence example declarations exist',
           all('Komorebi.LSM.'+n in by_name for n in [
               'FiniteBayes.effectiveLikelihood_product',
               'FiniteBayes.informationLossMatrix_scale_null',
               'Block3Examples.zero_evidence_is_not_an_update',
               'Block3Examples.one_prior_can_hide_a_defect']))
    record('Proof-file and rejection-control increments match the predecessor',
           len(list((ROOT/'KomorebiLSM').glob('*.lean')))-len(lineage['inherited_proof_files'])==99 and
           counts['negative_controls']-137==46)
    record('Aggregate theorem categories reconcile',
           counts['supporting_theorems']+counts['example_theorems']==counts['named_theorems'] and
           counts['new_theorems']==counts['named_theorems']-2042)
    record('Instrument construction has mass anchoring, exact word span and actual minimality',
           all('Komorebi.LSM.FiniteInstruments.'+n in by_name for n in [
               'exists_basis_first','instrumentCompletion_eq_wordSpan',
               'finite_instrument_stopping_bound','finite_instrument_coordinates',
               'finite_instrument_closure','closed_operator_unique',
               'completion_le_word_reading_summary']))
    record('Normalized closure converse includes explicit interior-prior spanning',
           all('Komorebi.LSM.FiniteInstruments.'+n in by_name for n in [
               'linearMap_eq_of_strict_priors','nonnegative_branch_mass_pos',
               'closure_of_likelihood_and_posterior','normalized_closure_defect',
               'likelihood_defect','closureDefect_projected']))
    record('P26 and P36 preserve supplied-model, domain and positive-evidence restrictions',
           cover['entries'][25]['status']=='complete' and
           'noncomputable' in cover['entries'][25]['scope'] and
           'every prior' in cover['entries'][25]['scope'] and
           'first coordinate' in cover['entries'][25]['scope'] and
           cover['entries'][35]['status']=='complete' and
           'strictly positive prior' in cover['entries'][35]['scope'] and
           'AND normalized posteriors' in cover['entries'][35]['scope'])
    record('Example boundaries include signed coordinates, missing surjectivity and posterior-only failure',
           all('Komorebi.LSM.Block4Examples.'+n in by_name for n in [
               'completion_exactly_two_rows','completion_dimension_two','order_matters',
               'mass_one_does_not_imply_realizability','impossible_branch_not_prior',
               'onto_required_for_uniqueness','posterior_alone_does_not_imply_closure',
               'example_satisfies_general_defect']))
    record('Actual behavior shift, model minimality and similarity targets resolve',
           all('Komorebi.LSM.Behavior.'+n in by_name for n in [
               'shift_mem','branch_history','word_probability','Realization.toBehavior_surjective',
               'Realization.behavior_dimension_le','Realization.minimal_realizations_similar',
               'Realization.intertwiner_unique','canonical_observable','canonical_reachable']))
    record('Observable formula is supported by rank coverage and all-word proofs',
           all('Komorebi.LSM.Behavior.'+n in by_name for n in [
               'core_rank_exact','evaluate_bijective','reconstructed_intertwines',
               'reconstructed_state','reconstructed_unique','reconstructed_conditional_update',
               'tableModel_minimal','observable_table_reconstruction']))
    record('Positive packets retain mixture and coordinate-selection restrictions',
           all('Komorebi.LSM.PositivePackets.'+n in by_name for n in [
               'mass_zero_iff','normalized_packet','positive_packet_mixture',
               'orthant_preserving_iff','unique_selected_packet',
               'positive_idempotents_are_coordinate_selections']))
    record('New scope keeps rank, measure and learned-domain boundaries explicit',
           all(cover['entries'][k-1]['status']=='complete' for k in (27,28,30)) and
           'not a sampled matrix rank' in cover['entries'][26]['scope'] and
           'global finite behavior-rank upper bound' in cover['entries'][27]['scope'] and
           'does not supply a learned cone' in cover['entries'][29]['scope'] and
           cover['entries'][28]['status']=='complete')
    record('Population and packet negative witnesses are themselves formal results',
           all('Komorebi.LSM.Block5Examples.'+n in by_name for n in [
               'finite_table_without_coverage_fails','inverse_side_matters',
               'hidden_model_not_observable','finite_rank_is_not_probability',
               'different_histories_equal_every_conditional_test',
               'haar_detail_not_probability','signed_packet_can_have_zero_mass']))
    record('Canonical cone is defined on the actual behavior span with topology and normalization',
           all('Komorebi.LSM.Behavior.'+n in by_name for n in [
               'probabilityCone_eq_tests','probabilityCone_spans','probabilityBase_compact',
               'probabilityBase_posterior','probabilityBase_core_bounds','canonical_probability_cone']))
    record('Finite all-test stopping is derived from adjacent-level equality',
           all('Komorebi.LSM.TestDomains.'+n in by_name for n in [
               'testLevel_succ','testLevel_stopping','allTests_greatest','finite_test_halfspaces',
               'finite_stopping_certificate','observe_injective_of_row_span']))
    record('Finite positive lift necessity and cone topology are present',
           all('Komorebi.LSM.PositiveLift.'+n in by_name for n in [
               'positive_lift_iff','hull_closed','hull_pointed','hull_spans',
               'normalizedHull_compact','normalizedHull_eq_convexHull','finite_positive_lift_certificate']))
    record('Robustness includes whole-family uncertainty and adaptive full-tree recursion',
           all('Komorebi.LSM.RobustDomains.'+n in by_name for n in [
               'robust_positive_lift','robust_convex_hull','mixed_lift',
               'adaptiveWord_in_cone','adaptiveWord_mass_le','adaptiveTreeMass_eq',
               'facet_norm_ball_invariant','facet_norm_ball_lift']))
    record('Correction derives validity and retains true-set membership as a hypothesis',
           all('Komorebi.LSM.CertifiedCorrection.'+n in by_name for n in [
               'FeasiblePoint.valid_family','FeasiblePoint.all_word_probabilities',
               'feasible_of_certified_member','two_center_error']))
    record('General canonical construction is not mislabeled as a finite-domain search',
           'not by finitely sampled trajectories' in cover['entries'][28]['scope'] and
           'No finite inequality description or learned cone algorithm' in cover['entries'][28]['scope'] and
           'not asserted for every family' in cover['entries'][37]['scope'])
    record('Shared coefficients, independent mass constraints and no implicit coverage retained',
           'shared convex coefficients' in cover['entries'][39]['scope'] and
           'Exact mass constraints remain separate' in cover['entries'][39]['scope'] and
           'No optimizer, empirical confidence set' in cover['entries'][40]['scope'])
    record('Negative boundary results and all-word table witness are exact declarations',
           all('Komorebi.LSM.Block6Examples.'+n in by_name for n in [
               'delayed_not_all_tests','unobserved_ray_nonzero','distinct_positive_lifts',
               'independent_branch_mixing_breaks_mass','certified_subcone_can_be_strict',
               'table_finite_stopping','interval_certificate_all_words']))
    roadmap=json.loads((ROOT/'ROADMAP_1.0.json').read_text())
    remaining=[n for track in roadmap['tracks'] for n in track['propositions']]
    record('Full 87-proposition roadmap remains exhaustive and nonoverlapping',
           len(remaining)==len(set(remaining))==0 and
           set(remaining)==set(range(1,88))-set(cover['complete']) and
           roadmap['completed']==cover['complete'])
    inherited_controls=lineage['inherited_control_files']
    control_repairs=lineage.get('inherited_control_repairs',{})
    expected_repairs={'negative_controls/PositiveLiftMustBeStrict.lean',
      'negative_controls/InconsistentDataAlwaysFits.lean',
      'negative_controls/ImpossibleConditionalPrior.lean'}
    record('Original 137 inherited-control hashes are retained',len(inherited_controls)==137)
    record('Exactly three authorized inherited-control repairs are explicit',set(control_repairs)==expected_repairs)
    changed_controls={name for name,h in inherited_controls.items() if digest(ROOT/name)!=h}
    record('Only the three documented active controls differ from the predecessor',changed_controls==expected_repairs)
    record('134 inherited controls remain byte-identical',
      sum(digest(ROOT/name)==h for name,h in inherited_controls.items())==134)
    repair_manifest=lineage['control_repair_manifest']
    require(digest(ROOT/repair_manifest['path'])==repair_manifest['sha256'],'Changed control-repair manifest')
    manifest_records=json.loads((ROOT/repair_manifest['path']).read_text())['repairs']
    require({e['control'] for e in manifest_records}==expected_repairs,'Control-repair manifest set mismatch')
    manifest_by_name={e['control']:e for e in manifest_records}
    for name,repair in control_repairs.items():
        original_hash=inherited_controls[name]
        require(repair['original_sha256']==original_hash,'Changed inherited original-control hash')
        require(digest(ROOT/repair['preserved_original'])==original_hash,'Preserved original control changed')
        require(digest(ROOT/name)==repair['active_sha256'],'Active control repair hash changed')
        require(digest(ROOT/repair['preserved_repaired'])==repair['active_sha256'],'Preserved repaired control changed')
        require(bool(repair['reason']),'Missing control repair reason')
        original_record=manifest_by_name[name]
        require(original_record['before_sha256']==original_hash and
          original_record['after_sha256']==repair['active_sha256'],'Control-repair manifest hash mismatch')
        require(digest(ROOT/repair['clean_receipt'])==repair['clean_receipt_sha256'],'Control-repair receipt changed')
        receipt=json.loads((ROOT/repair['clean_receipt']).read_text())
        require(receipt['control']==name and receipt['source_sha256']==repair['active_sha256'] and
          receipt['source_sha256_final']==repair['active_sha256'],'Control receipt/source mismatch')
        require(receipt['returncode']==1 and receipt['timed_out'] is False and
          receipt['valid_rejection'] is True and receipt['stderr']=='' and
          receipt['stdout'].count('error:')==1 and '⊢ False' in receipt['stdout'] and
          receipt['infrastructure_error_matches']==[],'Control repair lacks the sole intended False rejection')
        require(mod.classify_negative_control(receipt)['valid_rejection'],'Canonical classifier rejects a clean repaired control')
        original_stdout=(ROOT/'history/control_repairs'/(Path(name).stem+'.before.stdout.txt')).read_text()
        require(not mod.classify_negative_control({'returncode':1,'timed_out':False,'stdout':original_stdout,'stderr':''})['valid_rejection'],'Canonical classifier accepts a superseded mixed diagnostic')
        for module,pin in receipt['dependencies_execution'].items():
            if module.startswith('KomorebiLSM.'):
                source=ROOT/'KomorebiLSM'/(module.removeprefix('KomorebiLSM.')+'.lean')
                require(digest(source)==pin['source_sha256'],'Control receipt dependency source changed')
    record('All three original and repaired control bytes are preserved and hash-bound',True)
    record('All three repaired controls have current clean intended-rejection receipts',True)
    record('Canonical classifier accepts all three repaired clean diagnostics',True)
    record('Canonical classifier rejects all three original mixed diagnostics',True)
    record('Actual infimum, decomposition existence and norm objects are linked',
           all('Komorebi.LSM.BaseNorm.ProbabilityCone.'+n in by_name for n in [
               'value','exists_decomposition','le_value','value_le_cost','base_compact',
               'exists_norm_le_value','value_eq_zero_iff','groupNorm','seminorm']) and
           'sInf (C.costs x)' in (ROOT/'KomorebiLSM/BaseNorm.lean').read_text())
    record('Contraction, finite generator maximum and supremum error are derived',
           all('Komorebi.LSM.BaseNorm.ProbabilityCone.'+n in by_name for n in [
               'instrument_contraction','discrepancy_max_generator','instrumentError_le_two',
               'discrepancy_le_instrumentError','instrument_pair_step']))
    record('Finite positive-lift domains instantiate the norm construction',
           all('Komorebi.LSM.BaseNorm.'+n in by_name for n in [
               'finiteCone','finiteCone_base','value_invertible_synthesis',
               'value_synthesis_le_l1','orthant_value']))
    record('Chronological finite records have proved probabilities and accumulated error',
           all('Komorebi.LSM.ObservationTree.'+n in by_name for n in [
               'Record','recordState','record_mass','record_prior','record_state_error',
               'observation_tree_tv_bound']))
    record('Shared randomized policies and observation marginals are both formalized',
           all('Komorebi.LSM.ObservationTree.'+n in by_name for n in [
               'policyBranches','policy_instrument','policy_discrepancy','observationLaw',
               'shared_randomized_policy_tv_bound','shared_policy_observation_tv_bound',
               'shared_policy_instrumentError_bounds','deterministicPolicy_prior']))
    record('Conditioning includes comparison evidence positivity and parameterized sharpness',
           all('Komorebi.LSM.FiniteTV.'+n in by_name for n in [
               'restriction_budget','event_difference_le_distance','comparison_event_positive',
               'conditioning_tv_bound','conditioning_tv_bound_of_margin',
               'conditional_readout_bound','sharp_conditioning']))
    record('Exact examples distinguish total records, zero branches and rare evidence',
           all('Komorebi.LSM.Block7Examples.'+n in by_name for n in [
               'bernoulli_record_bound','bernoulli_quarter_two_step',
               'one_step_error_is_not_full_record_bound','zero_branch_record_is_prior',
               'rare_event_attains_bound','missing_event_conditional_not_prior']))
    record('Policy and redundant-coefficient counterexamples retain their actual structures',
           all('Komorebi.LSM.Block7BoundaryExamples.'+n in by_name for n in [
               'echo_instrument','fixedPolicy_prior','changed_policy_observation_distance',
               'leastSquareCoefficients_minimal','least_square_l1_is_not_base_norm']))
    record('New coverage retains finite dimension, common policy and positive-evidence hypotheses',
           'finite-dimensional' in cover['entries'][41]['scope'] and
           'shared deterministic or randomized' in cover['entries'][42]['scope'] and
           'No positive lower branch likelihood' in cover['entries'][42]['scope'] and
           'strictly positive event masses' in cover['entries'][43]['scope'] and
           'three-state priors' in cover['entries'][43]['scope'])
    record('All nine new isolated proof-rejection controls are present',
           all((ROOT/'negative_controls'/f'{n}.lean').is_file() for n in [
               'BaseNormEqualsSignedMass','ConditioningNeverAmplifies','OneStepBoundForEntireRecord',
               'DifferentPolicyZeroError','LeastSquareCoefficientsGiveBaseNorm',
               'PositiveButNotMassConservingContraction','IncorrectQuarterTVFactor',
               'ImpossibleConditionalPrior','NoEvidenceMarginNeeded']))
    record('Strong fixed-horizon limits and actual orthogonal projections are linked',
           all('Komorebi.LSM.Stability.'+n in by_name for n in [
               'strong_apply_varying','strong_fixed_powers','compression_error_bound',
               'compression_uniform_bound','strong_fixed_horizon_refinement',
               'estimated_refinement_fixed_horizon']))
    record('Typed local residuals generate the exact suffix-product envelope',
           all('Komorebi.LSM.Stability.'+n in by_name for n in [
               'errorEnvelope','errorEnvelope_succ','local_error_step','recurrence_product_sum',
               'compositional_defect_propagation','decoder_error_bound','constant_gain_bound']))
    record('Integer-history recurrence and actual uniform supremum are constructed',
           all('Komorebi.LSM.Stability.'+n in by_name for n in [
               'finiteMemory','finiteMemory_sub','finiteMemory_error_bound','invariant_error_radius',
               'finite_memory_prediction_bound','finite_memory_uniform_prediction_bound']))
    record('Coefficient, zero-prehistory, memory-tail and forcing budgets feed recursion',
           all('Komorebi.LSM.Stability.'+n in by_name for n in [
               'padded_sum_split','initialized_memory_split','memory_defect_identity',
               'integer_memory_tail_bound','memory_approximation_defect_bound',
               'discarded_initialized_forcing_bound','retained_initialized_forcing_bound',
               'certified_memory_truncation']))
    record('Nonlinear ordered interactions retain restricted ranges and a declared ball',
           all('Komorebi.LSM.PacketApproximation.'+n in by_name for n in [
               'HasPacketBound','omitted_interaction_identity','packet_interaction_truncation_bound',
               'packet_term_lipschitz','retained_polynomial_lipschitz_bound',
               'orthogonal_packet_lipschitz_bound','additional_model_remainder']))
    record('Frobenius reconciliation is constructed on actual operator coordinates',
           all('Komorebi.LSM.Reconciliation.'+n in by_name for n in [
               'weighted_variance_identity','frobenius_variance_identity',
               'operator_unique_frobenius_minimizer','orthonormalOperatorCoordinates',
               'hilbert_operator_unique_minimizer','reconciled_target_error']))
    record('Consistent coefficient norms, exact transports and both Lipschitz directions',
           all('Komorebi.LSM.Reconciliation.LinearAtlas.'+n in by_name for n in [
               'Coeff','decode_injective','decode_surjective','repaired_consistent',
               'repaired_intertwines','coeffNormed','coeffNormedSpace','pullback_norm',
               'transport_isometry','represented_lipschitz_iff']))
    record('New mapped statements retain horizon, trajectory, stability and domain limits',
           'Each horizon is fixed' in cover['entries'][12]['scope'] and
           'both true and predicted' in cover['entries'][17]['scope'] and
           'own recursively generated history' in cover['entries'][18]['scope'] and
           'strict norm-sum gain below one' in cover['entries'][18]['scope'] and
           'declared ball' in cover['entries'][19]['scope'] and
           'Agreement is not correctness' in cover['entries'][20]['scope'])
    record('Actual recurrence, all-time limit and nonlinear examples invoke general results',
           all('Komorebi.LSM.Block8Examples.'+n in by_name for n in [
               'expanding_prediction_general_bound','recursive_memory_uniform_bound',
               'gain_one_unbounded','alternating_amplification']) and
           all('Komorebi.LSM.Block8ApproximationExamples.'+n in by_name for n in [
               'scalar_fixed_horizon_convergence','each_resolution_has_large_late_error',
               'quadratic_general_truncation_bound','quadratic_general_lipschitz',
               'chart_unique_minimum','invalid_redundant_coefficient']))
    record('All ten new isolated boundary controls are present',
           all((ROOT/'negative_controls'/f'{n}.lean').is_file() for n in [
               'LocalResidualIsGlobalBound','GainOneUniformError','NilpotentSwitchingContractive',
               'FixedHorizonEqualsUniform','DroppedMemoryPrehistory','NonlinearDiagonalExact',
               'UnweightedReconciliation','ConsensusImpliesTruth','AmbientAtlasIsometry',
               'DropPolynomialDomain']))
    record('Block9 exact targets and boundary conditions resolve',
           all('Komorebi.LSM.'+n in by_name for n in [
             'Delay.delay_closure_rank_iff','Delay.dimension_closure','Delay.causal_future_output',
             'Identification.fit_iff_kernel','Identification.unseen_direction_not_identified',
             'Identification.penrose_one','Identification.penrose_two',
             'Identification.penrose_three','Identification.penrose_four',
             'Identification.rowGain_variational_unit','Identification.noisy_identification_bound',
             'Delay.finite_prefix_indistinguishability','Identification.learned_eq_true',
             'Identification.fitted_rollout','Identification.contracting_rollout']))
    record('Block9 predecessor completion is preserved',
           all(cover['entries'][k-1]['status']=='complete' for k in
               [1,2,3,4,5,6,7,8,9,10,12,13,18,19,20,21,22,26,27,28,29,30,36,38,39,40,41,42,43,44]))
    record('Block9 hypotheses are explicit in coverage',
           'Positive delay' in cover['entries'][13]['scope'] and
           'Strict input error' in cover['entries'][15]['scope'] and
           'Coverage and model assumptions remain supplied' in cover['entries'][24]['scope'])
    record('P45 targets cover real feasibility, computable enumeration and P39 soundness',
           all('Komorebi.LSM.RationalSearch.'+n in by_name for n in [
               'rational_feasible','rational_nonnegative_solution','rational_right_inverse',
               'rationalize_certificate','checkCode','search','search_sound','search_persistent',
               'rational_finite_certificate_search','accepted_probability_domain',
               'rational_mass_identity','accepted_all_word_probabilities']))
    record('P45 does not impose a strict-margin hypothesis',
           'boundary faces' in cover['entries'][44]['scope'] and
           'No strict margin' in cover['entries'][44]['scope'])
    record('Roadmap remaining_count matches its actual exhaustive list',roadmap['remaining_count']==len(remaining))
    progress=json.loads((ROOT/'PROGRESS.json').read_text())
    record('Roadmap and progress agree with complete, partial and unformalized coverage',
           roadmap['partial']==cover['partial']==progress['partial'] and
           roadmap['unformalized']==progress['unformalized']==[e['proposition'] for e in cover['entries'] if e['status']=='not_formalized'] and
           roadmap['unformalized_count']==len(progress['unformalized']) and
           progress['completed']==cover['complete'] and
           progress['outstanding']==sorted(set(range(1,88))-set(cover['complete'])) and
           progress['next_chronological']==(min(progress['unformalized']) if progress['unformalized'] else None))
    record('Executable examples are included in verifier source snapshot',
           'scripts/RunRationalSearch.lean' in mod.inventory())
    record('P32 is complete with its finite-table scope retained',
           cover['entries'][31]['status']=='complete' and 'does not certify' in cover['entries'][31]['scope'])
    record('P33 includes both identities and all three denominator bounds',
           all('Komorebi.LSM.Identification.'+n in by_name for n in ['core_inverse_laws','core_error_identity','core_error_bound','core_fitted_residual','core_fitted_identity','core_fitted_bound','core_checked_fitted_bound']))
    record('P34 includes exact normalization, path recurrence and uniform contraction',
           all('Komorebi.LSM.Filtering.'+n in by_name for n in ['prediction_error','fitted_mass_positive','normalized_residual','normalized_error_checked','normalized_error_margin','filtering_step','filtering_path','filtering_uniform']))
    record('Subspace coordinate inverse is constructed under the explicit gap',
           all('Komorebi.LSM.SubspaceCoordinates.'+n in by_name for n in ['coordinate_lower','coordinate_injective','coordinateEquiv','coordinate_inverse_bound']))
    record('One-sided residual implies full gap without assuming that gap',
           all('Komorebi.LSM.OneSidedSubspace.'+n in by_name for n in
             ['reverse_coordinate_lower','reverse_residual','reverse_operator_bound','projection_gap']))
    record('Earlier residual transfer and constructed spectral endpoint coexist',
           all('Komorebi.LSM.OneSidedSubspace.'+n in by_name for n in
             ['true_residual','residual_on_range','noisy_projection_gap','two_epsilon_gap']) and
           'Komorebi.LSM.Spectral.finite_table_stability' in by_name)
    record('Actual spectral lower bound and exact pseudoinverse norm are linked',
           all('Komorebi.LSM.Spectral.'+n in by_name for n in
             ['rightBasis','image_norm_sq','tail_coordinate_zero','leastPositive',
              'lower_on_kernel_orthogonal','exists_unit_minimizer','pinv_operator_norm_eq',
              'rangeInverse_right','rangeInverse_norm_eq','gap_from_observed_tail']))
    record('P32 derives actual spectral tails and basis decoder',
           cover['entries'][31]['status']=='complete' and
           all('Komorebi.LSM.'+n in by_name for n in
             ['Spectral.leadingLeft_tail_norm','Spectral.singularValue_abs_sub_le',
              'Spectral.leadingLeft_eq_span_leftModes','Spectral.singularValue_zero_at_max_rank',
              'BasisCoordinates.cross_min_singular','BasisCoordinates.decoder_matrix_formula',
              'BasisCoordinates.decoder_coordinates','BasisCoordinates.coordinates_decoder',
              'BasisCoordinates.decoder_norm_bound','FiniteTableP32.coordinates_and_decoder']))
    record('P11: accepted endpoints and mapped modules resolve', cover['entries'][10]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.StatisticalRefinement.ideal_statistical_benefit_of_integrable_sq_norm', 'Komorebi.LSM.StatisticalRefinement.ideal_statistical_risk_mono']))
    record('P23: accepted endpoints and mapped modules resolve', cover['entries'][22]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.GrammarAccounting.enumerated_grammar_accounting', 'Komorebi.LSM.GrammarAccounting.active_posterior_tv_tendsto_zero']))
    record('P24: accepted endpoints and mapped modules resolve', cover['entries'][23]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ProgramRefinement.prior_preserving_refinement', 'Komorebi.LSM.ProgramRefinement.predictive_event_unchanged']))
    record('P31: accepted endpoints and mapped modules resolve', cover['entries'][30]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.MissingIntervention.missing_intervention_nonidentifiability', 'Komorebi.LSM.MissingIntervention.no_passive_identification']))
    record('P35: accepted endpoints and mapped modules resolve', cover['entries'][34]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ResetCertificate.reset_probability_certificate', 'Komorebi.LSM.ResetCertificate.reset_table_probability_certificate', 'Komorebi.LSM.ResetCertificate.matrix_opNorm_le']))
    record('P37: accepted endpoints and mapped modules resolve', cover['entries'][36]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ConditionalStochasticCompletion.exact_stochastic_completion', 'Komorebi.LSM.ConditionalStochasticCompletion.conditional_core_history', 'Komorebi.LSM.ConditionalStochasticCompletion.reset_joint_event', 'Komorebi.LSM.ConditionalStochasticCompletion.filtering_on_joint_event']))
    record('P48: accepted endpoints and mapped modules resolve', cover['entries'][47]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.SequentialConfidence.conditional_simultaneous_coverage', 'Komorebi.LSM.SequentialConfidence.conditional_robust_certificate', 'Komorebi.LSM.SequentialConfidence.validity_at_selected_stage']))
    record('P57: accepted endpoints and mapped modules resolve', cover['entries'][56]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.AveragedCongruence.averaged_congruence_integral', 'Komorebi.LSM.AveragedCongruence.covariance_integral_posSemidef', 'Komorebi.LSM.AveragedCongruence.affine_covariance_correction', 'Komorebi.LSM.AveragedCongruence.uniformInterval_affine_correction']))
    record('P68: accepted endpoints and mapped modules resolve', cover['entries'][67]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.SequentialLowerCertificate.bounded_test_integral_le_tv', 'Komorebi.LSM.SequentialLowerCertificate.sequential_lower_certificate', 'Komorebi.LSM.SequentialLowerCertificate.simultaneous_sequential_lower_certificate']))
    record('P66: accepted endpoints and mapped modules resolve', cover['entries'][65]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.PredictableResidual.predictable_residual_certificate', 'Komorebi.LSM.PredictableResidual.time_uniform_rules', 'Komorebi.LSM.PredictableResidual.scaled_selected_bound']))
    record('P46: accepted endpoints and mapped scope resolve', cover['entries'][45]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.RotationP46.rational_rank_three_nonpolyhedral_model']))
    record('P47: accepted endpoints and mapped scope resolve', cover['entries'][46]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.LorentzBaseNorm.value_eq_sqrt', 'Komorebi.LSM.RotationApproximation.regular_polygon_positive_lift', 'Komorebi.LSM.RotationApproximation.sufficient_vertex_positive_lift', 'Komorebi.LSM.RotationApproximation.regular_polygon_policy_error', 'Komorebi.LSM.RotationApproximation.rational_diamond_certificate_data']))
    record('P49: accepted endpoints and mapped scope resolve', cover['entries'][48]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.CertificateLearning.witness_exists_iff', 'Komorebi.LSM.CertificateLearning.robust_vertex_witness', 'Komorebi.LSM.CertificateLearning.conditional_observable_learning', 'Komorebi.LSM.CertificateLearning.certified_conditioning', 'Komorebi.LSM.CertificateLearning.atlasWitness', 'Komorebi.LSM.CertificateLearning.positive_packet_state', 'Komorebi.LSM.CertificateLearning.certified_observation_conditioning', 'Komorebi.LSM.CertificateLearning.conditional_selected_learning', 'Komorebi.LSM.CertificateLearning.observable_witness_surjective']))
    record('P50: accepted endpoints and mapped scope resolve', cover['entries'][49]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.MatrixOrderUnit.exists_nonnegative_bound', 'Komorebi.LSM.MatrixEmbedding.Embedding.coneInstance', 'Komorebi.LSM.MatrixEmbedding.Embedding.base_compact', 'Komorebi.LSM.MatrixEmbedding.Embedding.CongruenceCertificate.observation_tree_prior', 'Komorebi.LSM.MatrixEmbedding.Embedding.CongruenceCertificate.transport']))
    record('P51: accepted endpoints and mapped scope resolve', cover['entries'][50]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.MatrixRotation.exact_rational_matrix_witness', 'Komorebi.LSM.MatrixRotation.embedding_posSemidef_iff', 'Komorebi.LSM.MatrixRotation.word_probability_unchanged', 'Komorebi.LSM.MatrixRotation.certificate']))
    record('P52: accepted endpoints and mapped scope resolve', cover['entries'][51]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ContinuousInstrument.DensityInstrument.kernel_markov', 'Komorebi.LSM.ContinuousInstrument.DensityInstrument.update_measurable', 'Komorebi.LSM.ContinuousRecords.recordLaw_probability', 'Komorebi.LSM.ContinuousRecords.recordLaw_compProd', 'Komorebi.LSM.ContinuousRecords.observationLaw_product_density', 'Komorebi.LSM.ContinuousRecordReference.recordLaw_reweighted', 'Komorebi.LSM.ContinuousRecordReference.observationLaw_reweighted']))
    record('P53: accepted endpoints and mapped scope resolve', cover['entries'][52]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.PolynomialGram.choi_factorization', 'Komorebi.LSM.PolynomialGramP53.polynomial_gram_probability_certificate']))
    record('P54: accepted endpoints and mapped scope resolve', cover['entries'][53]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.UniformIntervalMoments.gram_posDef', 'Komorebi.LSM.FiniteMomentIdentification.reconstructedCoefficient_eq', 'Komorebi.LSM.FiniteMomentIdentification.reconstructed_density_eq', 'Komorebi.LSM.FiniteMomentIdentification.induced_norm_coefficient_error', 'Komorebi.LSM.FiniteMomentIdentification.signed_reset_probability_certificate']))
    record('P55: accepted endpoints and mapped scope resolve', cover['entries'][54]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.LegendreCounterexample.L3_abs_integral', 'Komorebi.LSM.LegendreCounterexample.positive_law_totalVariation', 'Komorebi.LSM.LegendreCounterexample.product_moments_equal', 'Komorebi.LSM.LegendreCounterexample.rankone_event_realization', 'Komorebi.LSM.LegendreCounterexample.event_hankel_rank_one']))
    record('P56: accepted endpoints and mapped scope resolve', cover['entries'][55]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ContinuousBins.kernel_cell_posterior_average', 'Komorebi.LSM.ContinuousBins.actual_binned_recordLaw', 'Komorebi.LSM.ContinuousBins.exact_partition_coarsening']))
    record('P58: accepted endpoints and mapped scope resolve', cover['entries'][57]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.PositiveCellApproximation.positive_cell_average_certificate', 'Komorebi.LSM.PositiveCellApproximation.positive_equal_interval_certificate']))
    record('P59: accepted endpoints and mapped scope resolve', cover['entries'][58]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ContinuousTV.integrated_contraction', 'Komorebi.LSM.ContinuousTV.record_lawTV_le']))
    record('P60: accepted endpoints and mapped scope resolve', cover['entries'][59]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.CertifiedTemplate.matches_iff_scalar_system', 'Komorebi.LSM.CertifiedTemplate.observable_match_unique', 'Komorebi.LSM.CertifiedTemplate.fixed_template_recognition', 'Komorebi.LSM.CertifiedTemplate.record_law_transport', 'Komorebi.LSM.CertifiedTemplate.fitted_initial_check']))
    record('P61: accepted endpoints and mapped scope resolve', cover['entries'][60]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ContinuousPopulationBridge.fitted_density_identification', 'Komorebi.LSM.ContinuousRealizationP61.population_realization_certificate', 'Komorebi.LSM.ContinuousRealizationP61.population_record_law', 'Komorebi.LSM.ContinuousRealizationP61.recognized_population_probability', 'Komorebi.LSM.ContinuousRealizationP61.population_atlas_law', 'Komorebi.LSM.ContinuousRealizationP61.complete_packet_law', 'Komorebi.LSM.ContinuousRealizationP61.positive_packet_state', 'Komorebi.LSM.ContinuousRealizationP61.exact_population_bins', 'Komorebi.LSM.ContinuousRealizationP61.population_cell_resolution', 'Komorebi.LSM.ContinuousRealizationP61.population_equal_interval_resolution', 'Komorebi.LSM.ContinuousRealizationP61.population_common_policy_budget']))
    record('P62: accepted endpoints and mapped scope resolve', cover['entries'][61]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.OrientedEllipsoid.PolynomialCertificate.preserves', 'Komorebi.LSM.OrientedEllipsoid.PolynomialCertificate.record_law_probability', 'Komorebi.LSM.OrientedEllipsoid.PolynomialCertificate.record_law_prefix']))
    record('P63: accepted endpoints and mapped scope resolve', cover['entries'][62]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.EllipsoidDiscoveryP63.conditional_operator_only_ellipsoid_discovery', 'Komorebi.LSM.EllipsoidDiscoveryP63.finite_certificate_all_horizons']))
    record('P64: accepted endpoints and mapped scope resolve', cover['entries'][63]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.BernsteinKernel.kernel_squared_distance', 'Komorebi.LSM.PositivePolynomialApproximation.approximation_power_expansion', 'Komorebi.LSM.PositivePolynomialApproximation.approximatingInstrument', 'Komorebi.LSM.PositivePolynomialApproximation.induced_lipschitz_approximation_error', 'Komorebi.LSM.PositivePolynomialApproximation.common_policy_law_error']))
    record('P65: accepted endpoints and mapped scope resolve', cover['entries'][64]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.BernsteinCoefficientError.fitted_record_probability', 'Komorebi.LSM.BernsteinCoefficientError.uniform_bias_plus_coefficient_error', 'Komorebi.LSM.BernsteinCoefficientError.separate_correction_budget']))
    record('Nested Lean comments do not trigger prohibited tokens', mod.prohibited_source_hits('/- sorry /- axiom -/ unsafe -/\n-- admit\nexample : True := by trivial')==[])
    record('Active proof bypass tokens are rejected after comments', [h['token'] for h in mod.prohibited_source_hits('/- allowed comment -/ example : True := by sorry')]==['sorry'])
    record('Strings cannot open comments hiding later code', [h['token'] for h in mod.prohibited_source_hits('def note := "-- /-"; example : True := by admit')]==['admit'])
    record('Interpolated string expressions retain prohibited-token checks', [h['token'] for h in mod.prohibited_source_hits('def note := s!"text {by admit}"')]==['admit'])
    record('P66: accepted endpoints and mapped scope resolve', cover['entries'][65]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.PredictableResidualGeneral.predictable_residual_interval_certificate', 'Komorebi.LSM.PredictableResidualGeneral.predictable_residual_interval_finite', 'Komorebi.LSM.PredictableResidualGeneral.registration_transport', 'Komorebi.LSM.PredictableResidualGeneral.selected_interval_bound']))
    record('P67: accepted endpoints and mapped scope resolve', cover['entries'][66]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.CoveredAdaptiveActions.integral_weightedTest', 'Komorebi.LSM.CoveredAdaptiveActions.evidence_condExp', 'Komorebi.LSM.CoveredAdaptiveActions.covered_adaptive_action_certificate', 'Komorebi.LSM.CoveredAdaptiveActions.covered_bound_at_selected_time']))
    record('P69: accepted endpoints and mapped scope resolve', cover['entries'][68]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ObservationLawComparison.compProd_change', 'Komorebi.LSM.ObservationLawComparison.drift_eq_iterated', 'Komorebi.LSM.ObservationLawComparison.lawTV_le_expected', 'Komorebi.LSM.ObservationLawComparison.lawTV_same_initial', 'Komorebi.LSM.ObservationLawComparison.lawTV_same_initial_uniform', 'Komorebi.LSM.ObservationLawComparison.lawTV_fixed_history', 'Komorebi.LSM.ObservationLawComparison.lawTV_readout']))
    record('P70: accepted endpoints and mapped scope resolve', cover['entries'][69]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.TransferLearningCertificate.structural_acceptance', 'Komorebi.LSM.EllipsoidDiscoveryP63.conditional_operator_only_ellipsoid_discovery', 'Komorebi.LSM.EllipsoidDiscoveryP63.finite_certificate_all_horizons', 'Komorebi.LSM.PositivePolynomialApproximation.common_policy_law_error', 'Komorebi.LSM.TransferLearningCertificate.common_domain_upper_law', 'Komorebi.LSM.ObservationLawComparison.lawTV_same_initial', 'Komorebi.LSM.ObservationLawComparison.lawTV_le_expected', 'Komorebi.LSM.ObservationLawComparison.lawTV_same_initial_uniform', 'Komorebi.LSM.TransferLearningCertificate.simultaneous_lower_evidence', 'Komorebi.LSM.PredictableResidualGeneral.predictable_residual_interval_certificate', 'Komorebi.LSM.PredictableResidualGeneral.selected_interval_bound', 'Komorebi.LSM.CoveredAdaptiveActions.covered_adaptive_action_certificate', 'Komorebi.LSM.CoveredAdaptiveActions.covered_bound_at_selected_time']))
    record('P71: accepted endpoints and mapped scope resolve', cover['entries'][70]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.RobustOrientedMargin.exists_minimum', 'Komorebi.LSM.RobustOrientedMargin.le_sigma_iff', 'Komorebi.LSM.RobustOrientedMargin.residual_margin', 'Komorebi.LSM.RobustOrientedMargin.robust_preserves', 'Komorebi.LSM.RobustOrientedMargin.uncertainInstrument', 'Komorebi.LSM.RobustOrientedMargin.atlasUncertainInstrument', 'Komorebi.LSM.RobustOrientedMargin.atlas_record_probability']))
    record('P72: accepted endpoints and mapped scope resolve', cover['entries'][71]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.LorentzBoundaryFragility.outwardPerturbation_rank_one', 'Komorebi.LSM.LorentzBoundaryFragility.outwardPerturbation_size', 'Komorebi.LSM.LorentzBoundaryFragility.boundary_fragility', 'Komorebi.LSM.LorentzBoundaryFragility.euclidean_boundary_fragility', 'Komorebi.LSM.LorentzBoundaryFragility.zero_dimensional_impossibility']))
    record('P73: accepted endpoints and mapped scope resolve', cover['entries'][72]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.InteriorRepair.repair_margin', 'Komorebi.LSM.InteriorRepair.robust_repair_preserves', 'Komorebi.LSM.InteriorRepair.mixedFamily', 'Komorebi.LSM.InteriorRepair.ResetProfile.integrated_cost_le_two', 'Komorebi.LSM.InteriorRepair.repair_integrated_error', 'Komorebi.LSM.InteriorRepair.common_policy_law_error']))
    record('P74: accepted endpoints and mapped scope resolve', cover['entries'][73]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ProposalError.constraint_eq_target_iff', 'Komorebi.LSM.ProposalError.constraint_norm_sq', 'Komorebi.LSM.ProposalError.invariant_form_frobenius_error', 'Komorebi.LSM.ProposalError.invariant_form_matrix_budget', 'Komorebi.LSM.ProposalError.fixed_center_error']))
    record('P75: accepted endpoints and mapped scope resolve', cover['entries'][74]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.RationalSemicircle.charts_cover', 'Komorebi.LSM.RationalSemicircle.margin_of_charts', 'Komorebi.LSM.TensorBernsteinCertificate.LocalCertificate.sound', 'Komorebi.LSM.TensorBernsteinCertificate.SubdivisionWitness.sound', 'Komorebi.LSM.BernsteinRationalBasis.reconstruct', 'Komorebi.LSM.BernsteinCellPositivity.exists_small_positive', 'Komorebi.LSM.RationalBernsteinMargin.Certificate.margin', 'Komorebi.LSM.RationalBernsteinTermination.strict_family_eventual', 'Komorebi.LSM.RationalBernsteinTermination.strict_family_certificate_exists']))
    record('P76: accepted endpoints and mapped scope resolve', cover['entries'][75]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.CoefficientBox3.polynomial_output_bounds', 'Komorebi.LSM.CoefficientBox3.exact_mass_with_error', 'Komorebi.LSM.CoefficientBox3.box_record_probability', 'Komorebi.LSM.ConvexMargin.convex_feasible', 'Komorebi.LSM.ConvexMargin.convex_data_feasible', 'Komorebi.LSM.ConvexMargin.hull_feasible', 'Komorebi.LSM.ConvexMargin.hull_initial', 'Komorebi.LSM.ConvexMargin.hull_record_probability']))
    record('P77: accepted endpoints and mapped scope resolve', cover['entries'][76]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.StrictRationalGeometry.rational_strict_sector', 'Komorebi.LSM.StrictRationalSearch.candidate_exists', 'Komorebi.LSM.StrictRationalSearch.search_sound', 'Komorebi.LSM.StrictRationalSearch.conditional_search', 'Komorebi.LSM.StrictRationalSearch.conditional_search_with_hulls', 'Komorebi.LSM.StrictRationalSearch.source_hull_preserves', 'Komorebi.LSM.StrictRationalSearch.source_hull_initial_domain']))
    record('P78: accepted endpoints and mapped scope resolve', cover['entries'][77]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.DataSelectedGeometry.selected_geometry_on_coverage', 'Komorebi.LSM.DataSelectedGeometry.selected_geometry_probability', 'Komorebi.LSM.DataSelectedGeometry.false_acceptance_probability', 'Komorebi.LSM.DataSelectedGeometry.wholeInput_norm_le_sqrt_two', 'Komorebi.LSM.DataSelectedGeometry.combined_output_le_sqrt_two', 'Komorebi.LSM.DataSelectedGeometry.transformed_combined_error', 'Komorebi.LSM.DataSelectedGeometry.data_selected_transformed_error']))
    record('P79: accepted endpoints and mapped scope resolve', cover['entries'][78]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.Section88CertifiedRepair.proposedCertificate', 'Komorebi.LSM.Section88CertifiedRepair.comparisonCertificate', 'Komorebi.LSM.Section88CertifiedRepair.proposedInstrument', 'Komorebi.LSM.Section88CertifiedRepair.comparisonInstrument', 'Komorebi.LSM.Section88CertifiedRepair.initial_atlases', 'Komorebi.LSM.Section88CertifiedRepair.nominal_record_probability', 'Komorebi.LSM.Section88CertifiedRepair.robust_residual', 'Komorebi.LSM.Section88CertifiedRepair.coefficient_box_output', 'Komorebi.LSM.Section88CertifiedRepair.uncertain_record_probability', 'Komorebi.LSM.Section88CertifiedRepair.comparison_is_repair', 'Komorebi.LSM.Section88CertifiedRepair.comparison_integrated_error', 'Komorebi.LSM.Section88CertifiedRepair.comparison_law_bound', 'Komorebi.LSM.Section88CertifiedRepair.coefficientBoxInstrument', 'Komorebi.LSM.Section88CertifiedRepair.coefficient_box_record_probability', 'Komorebi.LSM.PerturbedOperatorFixture.proposed_inverse', 'Komorebi.LSM.PerturbedOperatorFixture.comparison_inverse', 'Komorebi.LSM.PerturbedOperatorFixture.nominalComparison_construction', 'Komorebi.LSM.PerturbedOperatorFixture.nominalProposed_construction', 'Komorebi.LSM.PerturbedOperatorFixture.corrected_construction']))
    record('P80: accepted endpoints and mapped scope resolve', cover['entries'][79]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ConvexRepairBracketing.feasible_interval', 'Komorebi.LSM.ConvexRepairBracketing.separator_positive', 'Komorebi.LSM.ConvexRepairBracketing.separator_ratio_lower', 'Komorebi.LSM.ConvexRepairBracketing.separator_lower_endpoint', 'Komorebi.LSM.CertifiedRepairUpper.bernstein_upper_bound', 'Komorebi.LSM.CertifiedRepairUpper.certified_bracket']))
    record('P81: accepted endpoints and mapped scope resolve', cover['entries'][80]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.RegressionConfidence.regression_confidence_certificate']))
    record('P82: accepted endpoints and mapped scope resolve', cover['entries'][81]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.ObservableMoments.observable_moment_operator_confidence']))
    record('P83: accepted endpoints and mapped scope resolve', cover['entries'][82]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.CurvedMoment.convex_hull_curve', 'Komorebi.LSM.CurvedMoment.Reference.instrument', 'Komorebi.LSM.CurvedMoment.Reference.conditional_signal_mean', 'Komorebi.LSM.CurvedMoment.Reference.conditional_legendre_mean']))
    record('P84: accepted endpoints and mapped scope resolve', cover['entries'][83]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.RationalSqrtEnclosure.integerUpperSqrt_minimal', 'Komorebi.LSM.RationalConfidenceArithmetic.scalarRadius_le_computed', 'Komorebi.LSM.RationalRegressionConfidence.two_regression_outer_certificate']))
    record('P85: accepted endpoints and mapped scope resolve', cover['entries'][84]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.CurvedMoment.Reference.observation_lawTV_le', 'Komorebi.LSM.CurvedMoment.Reference.observationLaw_lawTV_le', 'Komorebi.LSM.CurvedMoment.FiveNode.absoluteFirst_eq', 'Komorebi.LSM.CurvedMoment.FiveNode.absoluteLegendre_eq']))
    record('P86: accepted endpoints and mapped scope resolve', cover['entries'][85]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.MarkovStability.marginal_bound', 'Komorebi.LSM.MarkovStability.rollingWindow_geometric_bound', 'Komorebi.LSM.MarkovStability.BernoulliSeparation.interior_bernoulli_record_separation', 'Komorebi.LSM.MarkovStability.BernoulliSeparation.arbitrarily_small_marginal_gap']))
    record('P87: accepted endpoints and mapped scope resolve', cover['entries'][86]['status']=='complete' and all(n in by_name for n in ['Komorebi.LSM.CurvedMoment.Reference.ObservableProcess.simultaneous_rational_coverage', 'Komorebi.LSM.CurvedMoment.StructuredRectangle.Rectangle.certificate', 'Komorebi.LSM.CurvedMoment.Reference.TrueKernel.matches_certified_member', 'Komorebi.LSM.CurvedMoment.Reference.ObservableProcess.observable_structured_learning']))
    result={'kind' :'metadata_and_tooling','passed':True,'record_count':len(records),'records':records}
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(records)} metadata and tooling checks; not mathematical theorem counts.')

if __name__=='__main__': main()
