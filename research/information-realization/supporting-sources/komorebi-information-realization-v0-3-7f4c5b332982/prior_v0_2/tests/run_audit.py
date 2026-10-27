"""Adversarial, exhaustive and independent-oracle tests for v0.2.

Run from the package root:
    python tests/run_audit.py --suite all
Each suite writes a machine-readable report and exits nonzero on failure.
No test uses Python's `assert`, so checks remain active under python -O.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from fractions import Fraction as Q
from itertools import product
import importlib.util
import json
from math import ceil, log2
from pathlib import Path
from random import Random
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from information import (FiniteModel, canonical_partition, fixed_width_bits,
                         partitions, refines, predictive_refinement, rank_mod,
                         matvec, linear_repair_rows)


def require(condition, message='check failed'):
    if not condition:
        raise AssertionError(message)


def expect_error(function, exception=ValueError):
    try:
        function()
    except exception:
        return
    raise AssertionError(f'{exception.__name__} was not raised')


def raw_kappa(r, f):
    return max(len({f[i] for i in range(len(r)) if r[i] == z}) for z in set(r))


def decoder_oracle(r, f, w):
    """Explicitly enumerate every deterministic decoder, independent of API."""
    labels = tuple(dict.fromkeys(r))
    targets = tuple(dict.fromkeys(f))
    idx = {v: i for i, v in enumerate(labels)}
    best, evaluated = -1, 0
    for decoder in product(targets, repeat=len(labels)):
        score = sum(w[i] for i in range(len(r)) if decoder[idx[r[i]]] == f[i])
        best = max(best, score)
        evaluated += 1
    return Q(best, sum(w)), evaluated


def cell_success_oracle(r, f, w):
    """Independent direct sums, used inside exhaustive code search."""
    return Q(sum(max(sum(w[i] for i in range(len(r)) if r[i] == z and f[i] == y)
                     for y in set(f)) for z in set(r)), sum(w))


def structural():
    pairs, chains, repair_checks, witnesses = 0, 0, 0, 0
    by_n = []
    for n in range(1, 7):
        ps = partitions(n)
        k = {(r, f): raw_kappa(r, f) for r in ps for f in ps}
        for r in ps:
            for f in ps:
                model = FiniteModel(r, f)
                require(model.kappa() == k[r, f], 'kappa oracle')
                obs = model.obstruction()
                require((obs is None) == (k[r, f] == 1), 'obstruction iff recoverability')
                if obs is not None:
                    i, j = obs
                    require(r[i] == r[j] and f[i] != f[j], 'invalid obstruction certificate')
                    witnesses += 1
                code, decoder = model.exact_repair()
                require(len(set(code)) == k[r, f], 'nonminimal constructive repair')
                require(all(decoder[r[i], code[i]] == f[i] for i in range(n)), 'bad decoder')
                repair_checks += 1
                pairs += 1
        local = 0
        for r in ps:
            for s in partitions(max(r) + 1):
                coarse = canonical_partition(s[z] for z in r)
                for f in ps:
                    a, b, c = k[r, f], k[coarse, f], k[coarse, r]
                    require(a <= b <= a * c, 'composition cardinality')
                    require(fixed_width_bits(a) <= fixed_width_bits(b)
                            <= fixed_width_bits(a) + fixed_width_bits(c), 'composition bits')
                    chains += 1
                    local += 1
        by_n.append({'states': n, 'partitions': len(ps), 'composition_cases': local})
    return {'realization_task_pairs': pairs, 'composition_configurations': chains,
            'constructive_minimal_repairs': repair_checks, 'obstruction_witnesses': witnesses,
            'coverage': 'All observation/task partitions and observation coarsenings on 1..6 states, up to alphabet relabeling.',
            'by_state_size': by_n}


def probability():
    models, decoder_candidates, code_candidates, budgets, transports = 0, 0, 0, 0, 0
    zero_models, nonzero_models = 0, 0
    for n in range(1, 5):
        ps = partitions(n)
        weights = tuple(w for w in product(range(3), repeat=n) if sum(w))
        for r in ps:
            coarsenings = [canonical_partition(s[z] for z in r)
                           for s in partitions(max(r) + 1)]
            for f in ps:
                for w in weights:
                    model = FiniteModel(r, f, w)
                    hc = model.entropy_certificate()
                    require(hc.ratio >= 1, 'negative entropy')
                    require(hc.ratio <= model.kappa() ** model.total, 'entropy exceeds log kappa')
                    v, e = model.categorical_residual(), model.bayes_error()
                    require(e <= v <= 2*e-e*e, 'categorical residual risk bounds')
                    onehot_mse = sum((model.mse(tuple(int(y == label) for y in f)) for label in set(f)), Q(0))
                    require(v == onehot_mse, 'one-hot projector oracle')
                    require(hc.ratio >= (1/(1-v))**model.total, 'exact entropy-collision lower bound')
                    success, count = decoder_oracle(r, f, w)
                    decoder_candidates += count
                    require(1 - model.bayes_error() == success, 'Bayes risk oracle mismatch')
                    support_sufficient = model.obstruction(support_only=True) is None
                    require((hc.ratio == 1) == support_sufficient, 'zero entropy iff support recovery')
                    require((model.bayes_error() == 0) == support_sufficient, 'zero risk iff support recovery')
                    # All possible deterministic encoders, modulo their message labels.
                    candidate_scores = []
                    for code in ps:
                        joined = tuple(zip(r, code))
                        candidate_scores.append((max(code) + 1, cell_success_oracle(joined, f, w)))
                        code_candidates += 1
                    for m in range(1, n + 1):
                        best = max(score for k, score in candidate_scores if k <= m)
                        require(model.optimal_success(m) == best, 'budget optimum mismatch')
                        code, decoder = model.budget_repair(m)
                        actual = Q(sum(w[i] for i in range(n)
                                       if decoder[r[i], code[i]] == f[i]), sum(w))
                        require(actual == best, 'budget repair failed to attain optimum')
                        require(len(set(code)) <= m, 'over-budget code')
                        budgets += 1
                    for coarse in coarsenings:
                        cm = FiniteModel(coarse, f, w)
                        inter = FiniteModel(coarse, r, w)
                        cs, ci = cm.entropy_certificate(), inter.entropy_certificate()
                        require(hc.ratio <= cs.ratio <= hc.ratio * ci.ratio, 'EXACT entropy transport')
                        require(model.bayes_error() <= cm.bayes_error()
                                <= model.bayes_error() + inter.bayes_error(), 'risk transport')
                        require(cm.mse(f) - model.mse(f) == model.projection_distance(cm, f),
                                'exact deterministic projector loss')
                        require(cm.categorical_residual() - model.categorical_residual()
                                == model.categorical_projection_distance(cm), 'categorical projector loss')
                        # Orthogonality is tested directly, not only via MSE subtraction.
                        residual = tuple(Q(y) - z for y, z in zip(f, model.projected_values(f)))
                        require(all(v == 0 for v in model.projected_values(residual)), 'residual orthogonality')
                        require(cm.projected_values(model.projected_values(f)) == cm.projected_values(f), 'tower property')
                        transports += 1
                    zero_models += 0 in w
                    nonzero_models += 0 not in w
                    models += 1
    return {'weighted_models': models, 'models_with_zero_weights': zero_models,
            'models_with_full_support': nonzero_models,
            'explicit_decoder_candidates': decoder_candidates,
            'encoder_partitions_evaluated': code_candidates,
            'optimal_repair_budget_instances': budgets,
            'exact_entropy_risk_projection_transport_instances': transports,
            'coverage': 'All observation/task partitions on 1..4 states; every nonzero weight vector in {0,1,2}^n; all coarsenings; every code partition and m=1..n.',
            'entropy_arithmetic': 'Exact rational exponential certificates. No floating tolerance used for theorem inequalities.',
            'categorical_residual_checks': 'One-hot MSE oracle, Bayes-error bounds, exact entropy-collision bound, and exact transfer-loss identity.'}


def markov():
    count, zeros, decimal_crosschecks = 0, 0, 0
    triples = tuple(product(range(2), repeat=3))
    # Five grid parameters: P(F=1), P(R=1|F=0/1), P(S=1|R=0/1).
    for a, b, c, d, e in product(range(5), repeat=5):
        w = tuple((a if f else 4-a)
                  * ((b, c)[f] if r else 4-(b, c)[f])
                  * ((d, e)[r] if s else 4-(d, e)[r]) for f, r, s in triples)
        f = tuple(t[0] for t in triples)
        r = tuple(t[1] for t in triples)
        s = tuple(t[2] for t in triples)
        fine, coarse, inter = FiniteModel(r, f, w), FiniteModel(s, f, w), FiniteModel(s, r, w)
        hr, hs, hi = [m.entropy_certificate() for m in (fine, coarse, inter)]
        require(hr.ratio <= hs.ratio <= hr.ratio * hi.ratio, 'exact Markov entropy law')
        require(fine.bayes_error() <= coarse.bayes_error()
                <= fine.bayes_error() + inter.bayes_error(), 'Markov Bayes-risk law')
        require(coarse.mse(f) - fine.mse(f) == fine.projection_distance(coarse, f), 'Markov projection identity')
        require(coarse.categorical_residual() - fine.categorical_residual()
                == fine.categorical_projection_distance(coarse), 'Markov categorical projection identity')
        both = FiniteModel(tuple(zip(r, s)), f, w)
        # Equal a.s. on the common support. Null-cell versions can differ.
        mr, mrs = fine.projected_values(f), both.projected_values(f)
        require(all(not ww or u == v for ww, u, v in zip(w, mr, mrs)), 'Markov conditional independence')
        if count % 7 == 0:
            for m in (fine, coarse, inter):
                require(abs(float(m.entropy_certificate().decimal()) - m.entropy()) < 1e-12,
                        'independent 60-digit entropy display check')
                decimal_crosschecks += 1
        count += 1
        zeros += 0 in w
    return {'binary_markov_models': count, 'models_with_zero_weights': zeros,
            'decimal_display_crosschecks': decimal_crosschecks,
            'coverage': 'Every binary Markov chain with each of its five probability parameters in {0,1/4,1/2,3/4,1}.',
            'probability_and_entropy_inequalities': 'EXACT'}


def linear():
    exhaustive, seeded = 0, 0
    def check(p, n, R, F):
        states = tuple(product(range(p), repeat=n))
        r = tuple(matvec(R, x, p) for x in states)
        f = tuple(matvec(F, x, p) for x in states)
        model = FiniteModel(r, f)
        d = rank_mod(tuple(R) + tuple(F), p, n) - rank_mod(R, p, n)
        # Independent kernel-image enumeration.
        image = {fx for rx, fx in zip(r, f) if all(v == 0 for v in rx)}
        require(len(image) == p ** d == model.kappa(), 'rank/kernel/fiber bridge')
        require(model.bayes_error() == 1 - Q(1, p ** d), 'uniform linear risk formula')
        require(model.entropy_certificate().ratio == (p ** d) ** model.total, 'uniform linear entropy formula')
        C = linear_repair_rows(R, F, p, n)
        require(len(C) == d, 'minimal repair dimension')
        joined = tuple((rx, matvec(C, x, p)) for rx, x in zip(r, states))
        require(FiniteModel(joined, f).kappa() == 1, 'linear repair did not recover task')
    for p, n, rows in ((2, 3, 2), (3, 2, 2)):
        matrices = tuple(tuple(tuple(v[i*n:(i+1)*n]) for i in range(rows))
                         for v in product(range(p), repeat=rows*n))
        for R in matrices:
            for F in matrices:
                check(p, n, R, F)
                exhaustive += 1
    rng = Random(2601015)
    for _ in range(300):
        p, n = 5, 4
        R = tuple(tuple(rng.randrange(p) for _ in range(n)) for _ in range(rng.randrange(6)))
        F = tuple(tuple(rng.randrange(p) for _ in range(n)) for _ in range(rng.randrange(5)))
        check(p, n, R, F)
        seeded += 1
    return {'exhaustive_linear_map_pairs': exhaustive, 'seeded_GF5_four_dimensional_pairs': seeded,
            'coverage': 'All pairs of 2x3 GF(2) matrices and 2x2 GF(3) matrices; 300 seed-2601015 GF(5)^4 instances, including empty/redundant task and observation row sets.',
            'independent_oracles': 'State-fiber enumeration, kernel-image enumeration, modular row reduction, constructive task-row repair.'}


def pair_oracle(obs, actions):
    """Pair-product reachability, independent of iterative partition refinement."""
    n = len(obs)
    equivalent = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            todo, visited, ok = [(i, j)], set(), True
            while todo:
                a, b = todo.pop()
                if (a, b) in visited:
                    continue
                visited.add((a, b))
                if obs[a] != obs[b]:
                    ok = False
                    break
                todo.extend((t[a], t[b]) for t in actions)
            equivalent[i][j] = ok
    return equivalent


def dynamics():
    exhaustive, multi = 0, 0
    def check(obs, actions, minimality=False):
        n = len(obs)
        answer, history = predictive_refinement(obs, actions)
        eq = pair_oracle(obs, actions)
        require(all((answer[i] == answer[j]) == eq[i][j]
                    for i in range(n) for j in range(n)), 'pair-reachability mismatch')
        require(len(history) - 1 <= n - len(set(obs)), 'finite termination bound')
        require(refines(answer, obs), 'lost original observation')
        for t in actions:
            require(refines(answer, tuple(answer[t[i]] for i in range(n))), 'not dynamically stable')
        if minimality:
            for candidate in partitions(n):
                if refines(candidate, obs) and all(refines(candidate, tuple(candidate[t[i]] for i in range(n))) for t in actions):
                    require(refines(candidate, answer), 'result is not coarsest stable refinement')
    for n in range(1, 5):
        for obs in partitions(n):
            for t in product(range(n), repeat=n):
                check(obs, (t,), True)
                exhaustive += 1
    rng = Random(2602015)
    for _ in range(1000):
        n = rng.randrange(2, 13)
        obs = canonical_partition(rng.randrange(4) for _ in range(n))
        actions = tuple(tuple(rng.randrange(n) for _ in range(n)) for _ in range(rng.randrange(2, 5)))
        check(obs, actions)
        multi += 1
    return {'exhaustive_single_action_models': exhaustive, 'seeded_multiple_action_models': multi,
            'coverage': 'All transitions and observation partitions on 1..4 states; 1000 seed-2602015 systems on 2..12 states with 2..4 actions.',
            'oracles': 'Product-state reachability and exhaustive minimality among partitions for n<=4.'}


def metamorphic():
    rng, count = Random(2603015), 0
    for _ in range(1000):
        n = rng.randrange(1, 21)
        r, f = tuple(rng.randrange(6) for _ in range(n)), tuple(rng.randrange(6) for _ in range(n))
        w = tuple(rng.randrange(6) for _ in range(n))
        if not sum(w):
            w = (1,) + w[1:]
        m = FiniteModel(r, f, w)
        permutation = list(range(n)); rng.shuffle(permutation)
        other = FiniteModel(tuple(('obs', r[i]) for i in permutation),
                            tuple(('target', f[i]) for i in permutation), tuple(w[i] for i in permutation))
        require(other.kappa() == m.kappa() and other.bayes_error() == m.bayes_error(), 'relabel/permutation invariance')
        require(other.entropy_certificate() == m.entropy_certificate(), 'entropy relabel invariance')
        require(other.categorical_residual() == m.categorical_residual(), 'categorical relabel invariance')
        scale = rng.randrange(1, 6)
        scaled = FiniteModel(r, f, tuple(scale*v for v in w))
        require(scaled.bayes_error() == m.bayes_error(), 'probability scaling invariance')
        require(scaled.entropy_certificate().ratio == m.entropy_certificate().ratio ** scale, 'entropy scaling certificate')
        j = rng.randrange(n)
        split = rng.randrange(w[j] + 1)
        splitw = list(w); splitw[j] -= split
        duplicate = FiniteModel(r + (r[j],), f + (f[j],), tuple(splitw) + (split,))
        require(duplicate.kappa() == m.kappa() and duplicate.bayes_error() == m.bayes_error(), 'splitting a latent state')
        require(duplicate.entropy_certificate() == m.entropy_certificate(), 'entropy splitting invariance')
        count += 1
    return {'metamorphic_models': count, 'coverage': 'Seed 2603015. State permutations, bijective label recodings, weight rescaling, splitting a latent state (including null duplicates).'}


def negative():
    spec = importlib.util.spec_from_file_location('v01', ROOT/'baseline'/'komorebi_information_probe_v0_1.py')
    old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    findings = []
    states, pmf = (0, 1), {0: Q(1), 1: Q(0)}
    failures = []
    for name, args in [('optimal_squared_error', (states, pmf, lambda x:x, lambda x:x)),
                       ('projection_increment', (states, pmf, lambda x:x, lambda x:0, lambda x:x))]:
        try:
            getattr(old, name)(*args)
        except KeyError as exc:
            failures.append({'routine': name, 'exception': type(exc).__name__, 'missing_key': str(exc)})
        else:
            raise AssertionError('documented v0.1 failure did not reproduce')
    fixed = FiniteModel((0, 1), (0, 1), (1, 0))
    coarse = FiniteModel((0, 0), (0, 1), (1, 0))
    require(fixed.mse((0, 1)) == 0 and fixed.projection_distance(coarse, (0, 1)) == 0, 'null-cell regression')
    findings.append({'id': 'BUG-01', 'claim': 'v0.1 crashes on null observation cells', 'observed': failures,
                     'v0.2': 'fixed, null mass skipped and null-cell conditional means chosen as zero'})
    old_risk = old.optimal_error(states, {0:Q(2), 1:Q(-1)}, lambda x:0, lambda x:x)
    require(old_risk == -1, 'invalid pmf regression witness')
    expect_error(lambda: FiniteModel.from_probabilities((0, 0), (0, 1), (Q(2), Q(-1))))
    findings.append({'id':'BUG-02', 'claim':'v0.1 accepts negative probability and returns an impossible negative error',
                     'old_error':str(old_risk), 'v0.2':'rejected with ValueError'})
    large = 2**53 + 1
    require(ceil(log2(large)) == 53 and fixed_width_bits(large) == 54, 'rounding witness')
    bit_boundaries = 0
    for exponent in range(1, 1025):
        for k in (2**exponent-1, 2**exponent, 2**exponent+1):
            b = fixed_width_bits(k)
            require(k <= 2**b and (b == 0 or k > 2**(b-1)), 'integer bit budget')
            bit_boundaries += 1
    findings.append({'id':'BUG-03', 'claim':'float ceil(log2(k)) can understate a large integer alphabet budget',
                     'alphabet':large, 'old_bits':53, 'correct_bits':54,
                     'note':'Latent arithmetic weakness, not a failure encountered in the tiny v0.1 enumerations.'})
    require(coarse.kappa() == 2 and coarse.entropy_certificate().ratio == 1 and coarse.bayes_error() == 0,
            'support vs pointwise distinction')
    findings.append({'id':'NC-01', 'false_generalization':'zero probabilistic deficit implies pointwise recovery without full support',
                     'counterexample':coarse.profile()})
    xy = tuple(product(range(2), repeat=2))
    A, B = tuple(x[0] for x in xy), tuple(x[1] for x in xy)
    r, s = FiniteModel(A, B), FiniteModel(B, B)
    require(s.mse(B)-r.mse(B) == -Q(1,4) and r.projection_distance(s,B) == Q(1,4), 'missing Markov/nesting witness')
    findings.append({'id':'NC-02', 'false_generalization':'projection loss identity without nesting or a Markov condition',
                     'loss_difference':'-1/4', 'projector_distance':'1/4'})
    parity = tuple(a ^ b for a,b in xy)
    single = FiniteModel(A, parity); joint = FiniteModel(tuple(zip(A,B)), parity)
    require(single.bayes_error() == Q(1,2) and joint.bayes_error() == 0, 'synergy witness')
    require(single.entropy_certificate().ratio == 2**4 and joint.entropy_certificate().ratio == 1, 'synergy entropy')
    findings.append({'id':'NC-03', 'false_generalization':'task information is additive or always has diminishing marginal returns',
                     'witness':'Fair A,B and F=A XOR B. Individual task mutual informations are 0; joint is 1 bit.'})
    cycle_states = tuple((edge, v) for edge in range(5) for v in (edge, (edge+1)%5))
    cr, cf = tuple(x[0] for x in cycle_states), tuple(x[1] for x in cycle_states)
    cycle = FiniteModel(cr, cf)
    chi, coloring, two_best = None, None, Q(0)
    coloring_counts = {}
    for m in (1, 2, 3):
        success_count = 0
        for code in product(range(m), repeat=5):
            score = cell_success_oracle(tuple((edge, code[v]) for edge,v in cycle_states), cf, (1,)*10)
            if m == 2:
                two_best = max(two_best, score)
            if score == 1:
                success_count += 1
                if chi is None:
                    chi, coloring = m, code
        coloring_counts[m] = success_count
    require(cycle.kappa() == 2 and cycle.optimal_success(2) == 1 and chi == 3 and two_best == Q(9,10), 'encoder access boundary')
    findings.append({'id':'NC-04', 'false_generalization':'Kappa alphabet theorem remains valid when encoder sees only F rather than the state',
                     'state_aware_min_alphabet':2, 'target_only_min_alphabet':chi,
                     'target_only_two_symbol_best_success':str(two_best), 'coloring':coloring,
                     'valid_colorings_by_alphabet':coloring_counts})
    sums = ((1,1,0,0),(0,0,1,1))
    details = ((1,-1,0,0),(0,0,1,-1))
    require(rank_mod(sums+details, 5, 4) == 4 and rank_mod(sums+details, 2, 4) == 2, 'characteristic boundary')
    findings.append({'id':'NC-05', 'false_generalization':'sum/difference signal repair works unchanged in characteristic two',
                     'GF5_combined_rank':4, 'GF2_combined_rank':2})
    assignments = tuple(product(range(2), repeat=3))
    constraints = (lambda x:x[0]^x[1] == 0, lambda x:x[1]^x[2] == 0, lambda x:x[2]^x[0] == 1)
    pair_counts = [sum(all(constraints[j](x) for j in range(3) if j != missing) for x in assignments)
                   for missing in range(3)]
    all_count = sum(all(c(x) for c in constraints) for x in assignments)
    require(pair_counts == [2,2,2] and all_count == 0, 'gluing obstruction witness')
    findings.append({'id':'NC-06', 'false_generalization':'pairwise satisfiable parity constraints necessarily glue globally',
                     'pairwise_solution_counts':pair_counts, 'global_solutions':all_count})
    rare = FiniteModel((0,0), (0,1), (999999,1))
    require(rare.bayes_error() == Q(1,1000000) and rare.repair_bits() == 1, 'rare-event exact vs mean')
    findings.append({'id':'NC-07', 'false_generalization':'very small Bayes error removes the exact obstruction',
                     'bayes_error':'1/1000000', 'exact_repair_bits':1})
    mse_small = FiniteModel((0,0), (0,1)).mse((0,1))
    mse_large = FiniteModel((0,0), (0,1)).mse((0,10))
    require(mse_large == 100*mse_small, 'metric dependence')
    findings.append({'id':'NC-08', 'false_generalization':'MSE is an intrinsic count of information independent of target coordinates',
                     'MSE_for_labels_0_1':str(mse_small), 'MSE_for_labels_0_10':str(mse_large)})
    eps = Q(1,1000)
    reconstructed_b = (eps + eps) / eps
    require(reconstructed_b - 1 == 1, 'ill-conditioning witness')
    findings.append({'id':'NC-09', 'false_generalization':'exact injectivity implies noise-robust reconstruction',
                     'observation':'R(a,b)=(a,b/1000)', 'noise_in_second_coordinate':'1/1000',
                     'reconstructed_b_error':'1', 'error_amplification':1000})
    bad_inputs = [lambda: FiniteModel((),()), lambda: FiniteModel((0,),(0,1)),
                  lambda: FiniteModel((0,),(0,),(0,)), lambda: FiniteModel((0,),(0,),(-1,)),
                  lambda: FiniteModel((0,),(0,),(1.0,)), lambda: fixed_width_bits(0),
                  lambda: fixed_width_bits(1.5), lambda: rank_mod(((1,),),4,1),
                  lambda: predictive_refinement((0,1),((0,2),)),
                  lambda: FiniteModel.from_probabilities((0,),(0,),(0.5,)),
                  lambda: FiniteModel((0,0),(0,1),(1,1)).entropy_certificate(max_total=1)]
    for bad in bad_inputs:
        expect_error(bad)
    return {'confirmed_v01_implementation_issues':3, 'false_generalizations_refuted':9,
            'large_integer_boundary_checks':bit_boundaries, 'invalid_input_cases_rejected':len(bad_inputs),
            'findings':findings,
            'interpretation':'Expected counterexamples and regressions are PASS when detected. They are not disproofs of the correctly stated theorems.'}


SUITES = {'structural':structural, 'probability':probability, 'markov':markov,
          'linear':linear, 'dynamics':dynamics, 'metamorphic':metamorphic, 'negative':negative}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=tuple(SUITES)+('all',), default='all')
    args = parser.parse_args()
    names = tuple(SUITES) if args.suite == 'all' else (args.suite,)
    (ROOT/'reports').mkdir(exist_ok=True)
    for name in names:
        started = time.perf_counter()
        print(f'RUN {name}', flush=True)
        try:
            data = SUITES[name]()
            report = {'suite':name, 'status':'PASS', 'elapsed_seconds':round(time.perf_counter()-started,3),
                      'python':sys.version, 'optimization_level':sys.flags.optimize, **data}
        except Exception as exc:
            report = {'suite':name, 'status':'FAIL', 'elapsed_seconds':round(time.perf_counter()-started,3),
                      'exception':str(exc), 'traceback':traceback.format_exc()}
            (ROOT/'reports'/f'{name}.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
            print(report['traceback'],flush=True)
            return 1
        suffix = '_optimized' if sys.flags.optimize else ''
        (ROOT/'reports'/f'{name}{suffix}.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2),flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
