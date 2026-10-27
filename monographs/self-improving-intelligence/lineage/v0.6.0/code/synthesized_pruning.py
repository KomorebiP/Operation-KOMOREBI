"""Costed grammar synthesis of a certified compiler pruning expression.

Only finite arithmetic ASTs are interpreted. No eval/exec, external accounts,
network, source-code execution, neural training, or access to an episode's
hidden case. The query model, prefix semantics, and certificate theorem are
supplied. The synthesized expression changes a compiler, not its verifier.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product, combinations
import hashlib
import json
from typing import Iterable

from repair_calculus import (Problem, Tree, Witness, compile_frontier, check_tree)
from compiler_improvement import (Meter, ReadBudgetExceeded, metered_problem,
                                  immutable_binary_guard)

Expr = tuple
LEAVES = ('a', 'b', 'm', 'c', '0', '1')
ARITH = ('max', 'min', '+')
COMPARE = ('>', '<', '>=', '<=', '==')


def expr_size(expr: Expr) -> int:
    return 1 + sum(expr_size(x) for x in expr[1:])


def expr_text(expr: Expr) -> str:
    if len(expr) == 1:
        return expr[0]
    op, x, y = expr
    if op in ('max', 'min'):
        return f'{op}({expr_text(x)},{expr_text(y)})'
    return f'({expr_text(x)} {op} {expr_text(y)})'


def parse_expr(raw, max_nodes: int = 7) -> Expr:
    """Reject untyped or executable payloads; only this pure syntax is accepted."""
    remaining = [max_nodes]
    def visit(x):
        remaining[0] -= 1
        if remaining[0] < 0 or not isinstance(x, (list, tuple)) or not x:
            raise ValueError('Invalid or oversized expression.')
        if len(x) == 1 and x[0] in LEAVES:
            return (x[0],), 'int'
        if len(x) != 3 or x[0] not in ARITH + COMPARE:
            raise ValueError('Unknown syntax node.')
        left, lt = visit(x[1]); right, rt = visit(x[2])
        if lt != 'int' or rt != 'int':
            raise ValueError('Arithmetic and comparisons need integer children.')
        return (x[0], left, right), 'bool' if x[0] in COMPARE else 'int'
    expr, sort = visit(raw)
    if sort != 'bool':
        raise ValueError('A pruning expression must return a Boolean.')
    return expr


def evaluate(expr: Expr, context: dict[str, int], counter: Counter | None = None):
    if counter is not None:
        counter['expression_node_visits'] += 1
    op = expr[0]
    if len(expr) == 1:
        return int(op) if op in ('0', '1') else context[op]
    a = evaluate(expr[1], context, counter)
    b = evaluate(expr[2], context, counter)
    if op == 'max': return max(a, b)
    if op == 'min': return min(a, b)
    if op == '+': return a + b
    if op == '>': return a > b
    if op == '<': return a < b
    if op == '>=': return a >= b
    if op == '<=': return a <= b
    if op == '==': return a == b
    raise ValueError('Unknown expression operator.')


def grammar(features: tuple[str, ...] = ('a', 'b', 'm', 'c')) -> tuple[Expr, ...]:
    """Generate all comparison ASTs with 3 or 5 nodes, stable syntax order.

    Arithmetic nodes are commutative and generated with ordered operand pairs.
    No target predicate is inserted as a special candidate or initial rule.
    """
    if len(set(features)) != len(features) or not set(features) <= set(LEAVES[:4]):
        raise ValueError('Unknown or duplicate feature.')
    atoms = tuple((x,) for x in (*features, '0', '1'))
    pairs = [(atoms[i], atoms[j]) for i in range(len(atoms)) for j in range(i, len(atoms))]
    compound = tuple((op, a, b) for op in ARITH for a, b in pairs)
    small = tuple((op, a, b) for op in COMPARE for a in atoms for b in atoms)
    large = tuple((op, a, b) for op in COMPARE
                  for left, right in ((compound, atoms), (atoms, compound))
                  for a in left for b in right)
    return small + large


def prefix_contexts(caps: tuple[int, ...] = (1, 2, 4)) -> tuple[dict[str, int], ...]:
    """All count prefixes of total sizes 2..2*c, independent of row labels."""
    contexts = []
    for c in caps:
        if type(c) is not int or c < 1:
            raise ValueError('Positive integer capacity required.')
        for m in range(2, 2*c+1):
            for t in range(m+1):
                for a in range(t+1):
                    contexts.append({'a':a, 'b':t-a, 'm':m, 'c':c})
    return tuple(contexts)


def impossible_by_completions(ctx: dict[str, int], counter: Counter | None = None) -> bool:
    """Finite teacher enumerates all possible remaining one-counts.

    It does not use the formula sought by the learner. Every binary completion
    has exactly one of these counts. This teacher concerns capacity feasibility,
    not completion by an actual downstream query library.
    """
    a, b, m, c = (ctx[k] for k in ('a','b','m','c'))
    if min(a,b) < 0 or a+b > m or c < 1 or not 2 <= m <= 2*c:
        raise ValueError('Prefix outside the finite teacher contract.')
    r = m-a-b
    for ones in range(r+1):
        if counter is not None:
            counter['teacher_completion_counts'] += 1
        if a+r-ones <= c and b+ones <= c:
            return False
    return True


def feature_conflict(contexts, labels, features):
    seen = {}
    for i, (ctx, label) in enumerate(zip(contexts, labels)):
        key = tuple(ctx[f] for f in features)
        if key in seen and labels[seen[key]] != label:
            j = seen[key]
            return {'features':list(features), 'left':contexts[j], 'right':ctx,
                    'left_label':labels[j], 'right_label':label,
                    'indices':[j,i]}
        seen.setdefault(key, i)
    return None


def certify_rule(raw) -> dict:
    """A narrow structural certificate checker, not general theorem proving.

    Recognizes exactly max(a,b)>c, allowing the operand swaps that preserve it.
    Universal soundness rests on the manuscript's supplied prefix-capacity proof.
    Arbitrary finite-consistent formulas are NOT automatically admitted.
    """
    expr = parse_expr(raw, max_nodes=5)
    op, left, right = expr
    if op == '<':
        left, right = right, left
        op = '>'
    if not (op == '>' and right == ('c',) and left[0] == 'max'
            and {left[1], left[2]} == {('a',), ('b',)}):
        raise ValueError('Formula has no supported universal scope certificate.')
    return {'theorem':'prefix_capacity_v1', 'expression':expr,
            'scope':['integer nonnegative prefix counts a,b with a+b<=m',
                     'positive integer child capacity c and 2<=m<=2*c',
                     'two immutable binary report branches',
                     'one successful initial case per terminal repair'],
            'proof_status':'Supplied prose argument plus project-local structural checker; not a proof assistant.'}


def synthesize(caps: tuple[int, ...] = (1,2,4)) -> tuple[Expr, dict]:
    """Counterexample-guided enumeration with an explicit feature repair."""
    ctxs = prefix_contexts(caps); counters = Counter()
    labels = []
    for ctx in ctxs:
        counters['teacher_contexts'] += 1
        labels.append(impossible_by_completions(ctx, counters))
    initial_features = ('a','b','m')
    obstruction = feature_conflict(ctxs, labels, initial_features)
    if obstruction is None:
        raise ValueError('The declared feature-refinement example lost its obstruction.')
    # One explicit, supplied extra feature is available. Its value is computed
    # from the remaining allowed diagnostic horizon, not a hidden target state.
    features = initial_features + ('c',)
    if feature_conflict(ctxs, labels, features) is not None:
        raise ValueError('The enlarged observation features remain insufficient.')
    programs = grammar(features)
    examples: list[int] = []
    trace = []
    winner = None
    for number, expr in enumerate(programs):
        counters['candidate_asts_considered'] += 1
        consistent = True
        for i in examples:
            counters['retained_example_checks'] += 1
            if bool(evaluate(expr, ctxs[i], counters)) != labels[i]:
                consistent = False
                break
        if not consistent:
            continue
        counters['candidate_teacher_queries'] += 1
        bad = None
        for i, ctx in enumerate(ctxs):
            counters['teacher_program_comparisons'] += 1
            if bool(evaluate(expr, ctx, counters)) != labels[i]:
                bad = i
                break
        if bad is None:
            winner = expr
            trace.append({'candidate_index':number, 'expression':expr_text(expr),
                          'result':'finite_domain_pass'})
            break
        if bad in examples:
            raise AssertionError('A consistent candidate repeated an old counterexample.')
        examples.append(bad)
        trace.append({'candidate_index':number, 'expression':expr_text(expr),
                      'result':'counterexample', 'context':ctxs[bad], 'label':labels[bad]})
    if winner is None:
        raise ValueError('No expression in the bounded grammar meets the finite target.')
    certificate = certify_rule(winner)
    raw = json.dumps(winner, separators=(',',':'))
    report = {'status':'PASS', 'training_capacities':list(caps), 'grammar_count':len(programs),
              'max_ast_nodes':5, 'generated_literal_ast_nodes':sum(expr_size(e) for e in programs),
              'context_count':len(ctxs),
              'initial_feature_obstruction':obstruction, 'enlarged_features':list(features),
              'learned_expression':winner, 'expression_text':expr_text(winner),
              'expression_sha256':hashlib.sha256(raw.encode()).hexdigest(),
              'ast_nodes':expr_size(winner), 'serialized_expression_bytes':len(raw.encode()),
              'counters':dict(counters), 'counterexamples':len(examples), 'trace':trace,
              'certificate':certificate,
              'training_data_sha256':hashlib.sha256(json.dumps(list(zip(ctxs,labels)),sort_keys=True).encode()).hexdigest(),
              'limitations':['Pure bounded enumerative program synthesis, not neural training.',
                'Grammar, feature registry, completion teacher, compiler skeleton, and universal proof are supplied.',
                'Training labels concern capacity obstruction, not empirical benefit on unrelated tasks.',
                'The learner does not improve its own enumerator or generate the certificate theorem.']}
    return winner, report


def compile_streaming(problem: Problem, horizon: int, raw_rule=None,
                      support: Iterable[int] | None = None,
                      read_limit: int | None = None,
                      engine: str = 'interpreted') -> tuple[tuple[Witness,...],dict]:
    """The same ordered, lower-depth tree search with/without prefix pruning.

    A recognized rule can stop reading an already impossible root's remaining
    model rows. Remaining candidate roots are still searched, with backtracking.
    Guard/checker costs are charged. Failure at the information lower depth
    falls back only when the requested horizon is greater than that depth.
    """
    states = tuple(sorted(set(range(problem.n) if support is None else support)))
    if not states or not set(states) <= set(range(problem.n)) or type(horizon) is not int or horizon < 0:
        raise ValueError('Invalid support or horizon.')
    if engine not in ('interpreted', 'lowered'):
        raise ValueError('Unknown predicate engine.')
    rule = None
    if raw_rule is not None:
        rule = certify_rule(raw_rule)['expression']
    meter = Meter(read_limit); p = metered_problem(problem, meter)
    stats = Counter(); mode = 'full_scan'; witness = None
    def dfs(possible:tuple[int,...], depth:int) -> Tree | None:
        stats['search_supports'] += 1
        if len(possible) == 1:
            return Tree('repair', leaves[possible[0]])
        if depth == 0 or len(possible) > 2**depth:
            return None
        cap = 2**(depth-1)
        for ei, e in enumerate(p.experiments):
            stats['query_roots_started'] += 1
            sides = [[],[]]; pruned = False
            for j,x in enumerate(possible):
                item = e.transitions[x]
                if item is None: raise ValueError('Immutable scope was invalidated.')
                sides[item[1]].append(x)
                if rule is not None:
                    stats['prune_rule_calls'] += 1
                    ctx={'a':len(sides[0]),'b':len(sides[1]),'m':len(possible),'c':cap}
                    if engine == 'interpreted':
                        reject = evaluate(rule,ctx,stats)
                    else:
                        # The prior prefix passed. Only this count increased,
                        # so it is the only count that can now exceed capacity.
                        stats['lowered_comparisons'] += 1
                        reject = len(sides[item[1]]) > cap
                    if reject:
                        stats['prefix_roots_rejected'] += 1
                        stats['model_rows_skipped'] += len(possible)-j-1
                        pruned = True
                        break
            if pruned:
                continue
            stats['query_roots_fully_read'] += 1
            if not all(sides) or max(map(len,sides)) > cap:
                continue
            # The size test is necessary, not sufficient for the actual library.
            a = dfs(tuple(sides[0]), depth-1)
            if a is None:
                stats['failed_feasible_roots'] += 1
                continue
            b = dfs(tuple(sides[1]), depth-1)
            if b is None:
                stats['failed_feasible_roots'] += 1
                continue
            return Tree('query',ei,((0,a),(1,b)))
        return None

    try:
        leaves=immutable_binary_guard(p,meter)
        front=None
        if leaves is not None:
            minimum_depth=(len(states)-1).bit_length()
            meter.phase='proposal'
            if horizon < minimum_depth:
                front=();mode='certified_horizon_obstruction'
            else:
                witness=dfs(states,minimum_depth)
                if witness is not None:
                    meter.phase='verification'
                    w,s=check_tree(p,states,witness,horizon)
                    if (w,s)!=(Q(minimum_depth+1),2*len(states)-1):
                        raise AssertionError('Candidate did not attain both lower bounds.')
                    front=(Witness(w,s,witness),)
                    mode='certified_streaming' if rule is not None else 'certified_full_scan'
                elif horizon == minimum_depth:
                    front=();mode='certified_lower_depth_infeasible'
        if front is None:
            mode='fallback';meter.phase='exact_search'
            extra={};front=compile_frontier(p,states,horizon,extra)
            stats.update(extra)
            meter.phase='verification'
            for w in front:
                if check_tree(p,states,w.tree,horizon)!=(w.work,w.storage):
                    raise AssertionError('Fallback witness mismatch.')
        status='complete'
    except ReadBudgetExceeded:
        front=();status='incomplete';mode='read_budget_exhausted'
    return front, {'status':status,'mode':mode,'streaming':rule is not None,
        'table_reads':meter.total,'phase_reads':dict(meter.reads),
        'shared_input_validation_reads':meter.setup_reads,'counters':dict(stats),
        'frontier':[[str(w.work),w.storage] for w in front], 'read_limit':read_limit,
        'compiler_rule_nodes':0 if rule is None else expr_size(rule),
        'engine':engine if rule is not None else 'full_scan',
        'cost_scope':'Model-record reads and interpreted AST-node visits are distinct units; not all CPU work.'}


def cover_number(problem:Problem, support:Iterable[int]) -> int | None:
    """Exact small-set repair-cover number. Not called by the compiler."""
    target=set(support)
    if not target:return 0
    for k in range(1,len(problem.repairs)+1):
        for picked in combinations(problem.repairs,k):
            covered=set().union(*(r.good for r in picked))
            if target<=covered:return k
    return None
