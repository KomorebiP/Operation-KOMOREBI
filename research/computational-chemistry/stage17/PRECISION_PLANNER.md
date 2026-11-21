# Planning a certified response scan

An accuracy request should determine the work required for a scan. This planner uses the existing finite H10-derived response certificates to choose an action budget and a subset of saved energy nodes. It separates Hamiltonian actions, which construct a cache, from endpoint response evaluations, which reuse that cache.

At broadening 0.1 Hartree and an absolute radius budget of 0.1 per Hartree, the lowest-action qualifying stored cache uses 32 actions and 14 of its 41 saved energy nodes. Choosing the fewest endpoint evaluations instead uses 64 actions and 13 nodes. At broadening 0.5 Hartree, a 0.01-per-Hartree budget gives a similar tradeoff: three actions and six nodes, or nine actions and five nodes.

The narrow 0.01-Hartree scan still requires its 512-action cache and all 166 saved nodes to meet the 0.1-per-Hartree budget with these bounds. The planner does not hide this case. Tighter requests can be unsupported even when endpoint disks are small: the bound between available nodes must also meet the request.

These are plans over the published finite node pools and rounded cell bounds. They are not optimality statements about every solver, every possible energy grid or the true approximation error. The stored endpoints were already evaluated; choosing a subset does not undo that work or establish a measured runtime improvement.

## A sharp uniform cell bound

Stage 16 supplies a valid disk with linearly interpolated center and radius

    r(t) = (1-t)r0 + t r1 + t(1-t)C,     0 <= t <= 1.

Here r0,r1,C are nonnegative. Its exact maximum is

    M(r0,r1,C) = max(r0,r1),
        if C=0 or |r1-r0| >= C;
    M(r0,r1,C) = (r0+r1)/2 + C/4 + (r1-r0)^2/(4C),
        otherwise.                                           (1)

To prove (1), put d=r1-r0. For C>0,

    r(t) = r0 + (d+C)t - C t^2
         = r0 + (d+C)^2/(4C) - C(t-(d+C)/(2C))^2.

The vertex lies strictly inside [0,1] exactly when |d|<C. In that case the displayed vertex value expands to the second expression in (1). Otherwise the maximum occurs at an endpoint. If C=0 the radius is linear and the endpoint rule applies. Equality |d|=C is covered by either formula. This also handles zero radii and unequal endpoint radii.

The expression is nondecreasing in C because r(t) is pointwise nondecreasing in C. Therefore replacing C by a rational upper bound preserves validity. The implementation first rounds the Stage 16 coefficient upward to 18 decimal places, evaluates (1) exactly, and rounds the result upward to 18 decimal places. This final rational number is the declared edge weight. It is at most the correspondingly rounded older max(r0,r1)+C/4 bound.

## Finite optimality of the grid

Let the saved energies be E0<E1<...<E(n-1), with n>=2. For every i<j, compute the declared conservative radius w(i,j) using only the saved disks at those two endpoints. Stage 16 permits cells of any positive width; adjacent saved nodes are not required.

A plan is a strictly increasing index path from 0 to n-1. Its cells tile the entire energy interval without gaps. Its certified maximum radius is the largest edge weight on that path. Its energy cost is the number of path nodes, counting both interval endpoints.

Write D(q,j) for the smallest possible largest edge weight among paths from 0 to j using exactly q nodes. Use infinity for infeasibility. The recurrence is

    D(1,0)=0;    D(1,j)=infinity for j>0;
    D(q,j)=min over i<j of max(D(q-1,i),w(i,j)),    q>=2.       (2)

Proof is by induction on q. Every q-node path to j has a unique penultimate node i; removing its final edge leaves a (q-1)-node path to i. Its largest edge is at least max(D(q-1,i),w(i,j)). Conversely a minimizing feasible predecessor path followed by i->j realizes that value. There are finitely many candidates, so a finite minimum is attained. For q=2 the only predecessor is the initial node. No independence, monotonicity under refinement or triangle inequality for the edge weights is assumed.

For a positive requested tolerance T, the first q with D(q,n-1)<=T is therefore the minimum number of saved energy nodes meeting the request under these declared weights. A row whose radius does not improve on an earlier q is dominated and may be omitted. The remaining rows form the stored frontier. This pruning does not assume that the exact-q values are monotone.

Run this calculation separately for each stored action budget at the requested broadening. Minimizing actions chooses the smallest qualifying action budget, then the smallest qualifying node count. Minimizing energy evaluations reverses these priorities. These are count objectives, not wall-time models. The planner does not interpolate action budgets or broadenings.

## Why the optimizer does not assume greedy optimality

An abstract ordered five-node example has weight one on 0->1, 0->2, 1->4, 2->3 and 3->4, and weight two on every other forward edge. At tolerance one, choosing the farthest feasible next node gives 0,2,3,4; the optimal path is 0,1,4. This refutes a general greedy guarantee. The example is not asserted to arise from the H10 endpoint disks.

The finite study also compares greedy plans with optimal plans at three preset tolerances on each of the 22 stored curves. Those comparisons do not replace the recurrence proof or assert a physical counterexample to greedy coarsening.

## Computation and review

The study evaluates all 30,915 forward pairs across the 22 curves, producing 717 nondominated rows. For every row, an independent threshold shortest-path calculation checks its minimum node count, both at its declared radius and immediately below it on the common 18-decimal lattice: 1,434 threshold checks. These checks are over the complete saved node pools, not a sample of edges.

A separate seeded audit enumerates all 3,048 paths in 168 small weighted graphs, compares 10,584 threshold queries, checks 64 sharp-maximum cases and 6,464 rational points on their quadratics, and retains the abstract greedy counterexample. The small graphs are sampled; the paths within each chosen graph are exhaustive.

The browser verifies both downloaded data identities and rechecks the published frontier paths using exact BigInt fractions. Minimality follows from (2), the recorded full finite computation and the separate threshold checks; the browser does not rerun the complete minimax optimization on every edit.

The proof and implementation reviews are project self-review. They are not independent expert review or proof-assistant verification. The interpolation implication remains conditional on the valid endpoint disks and their named arithmetic model. The supplied neutral source/reference and finite Hamiltonian are fixed; physical approximation accuracy remains open.

## Replay

The identity verifier uses only Python's standard library:

```text
python -B research/computational-chemistry/stage17/verify_stage17.py
```

Fresh output directories reproduce the finite calculations:

```text
python -B research/computational-chemistry/stage17/budget_study.py --output fresh-budget-study
python -B research/computational-chemistry/stage17/audit_planner.py --output fresh-planner-audit
```

The recorded environment used Python 3.12.14. The study took approximately 8.0 seconds on the recorded Windows environment; this is not an optimized-solver benchmark. The provenance runner bounded each run by 180 seconds and 1 MiB of logs. The manual commands above do not impose that runner limit. No Hamiltonian action is performed by this phase.
