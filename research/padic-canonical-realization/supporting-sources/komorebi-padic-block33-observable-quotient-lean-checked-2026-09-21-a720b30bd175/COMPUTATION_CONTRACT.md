# Block 33 computation contract

## Universal theorem versus finite assertion
The Lean theorem constructs the greatest silent invariant submodule and exact
behavior quotient, with finite horizon b when the source has p^b elements. The
Python suite audits a mixed-cyclic lattice algorithm for that quotient. Finite
agreement is not substituted for the universal theorem and does not prove an
executable refinement to Lean.

## Conventions and arithmetic
R=Z/(p^r), p prime, r>=0. Source modules are products Z/(p^e_i) with 0<=e_i<=r.
Destination rows and source columns are explicit. Every input transition and
output must respect source annihilator relations. Word order is left to right;
integer indices use least-significant-first digits. The empty word is tested.
All load-bearing arithmetic is integer arithmetic or exact SymPy matrices.
A vector/matrix equality counts once. Invalid dimensions are rejected before
coordinate reduction. The quotient representative selector is not claimed linear.

## Algorithms compared
The main engine closes the observation-row lattice under precomposition by digit
maps, including modulus times the integer lattice. A Smith decomposition with
exact matrix identities, unimodularity and divisibility checks constructs its
annihilator lattice. A second checked Smith decomposition presents the quotient.
Kernel generators are checked for annihilation, source-relation inclusion, and
transition invariance.

The independent small-system oracle enumerates every source state and refines
future-behavior classes until stable, using no HNF, Smith, rank computation or
field inversion. It compares all state equivalence classes, kernel memberships,
transition/output projections and quotient representatives. Additivity and scalar
projection are checked on three deterministic sampled pairs per system.

## Exact finite domain
Seed: 33092026, random.Random (MT19937).
Prime/precision pairs: (2,0),(2,1),(2,2),(2,3),(3,1),(3,2),(5,1).
Coordinate counts: 0,1,2,3. Alphabet sizes: 0,1,2. Three sampled systems per tuple.
Exponents are sampled uniformly from 0..r. Systems with cardinality>625 are
excluded. This yields 251 generic executions. All STATES of each admitted system
are enumerated; the suite does not enumerate all possible systems in the domain.

Actual mask grid: p in {2,3,5}, r in {1,2,3}, with (A,B) respectively
(1,1-z), (1,1+p^2*z), (1+z,1), (1+z,1+z), and (1+z^2,1-z^2).
Four additional stress cases, all A=1:
(2,4,1+4z), (2,8,1-z), (2,8,1+16z), (3,6,1+81z).
There are 49 actual-mask executions. Output indices are exactly n=0..31.
Every original matrix column is compared with polynomial routing. Generator
projections and four sampled arbitrary source coordinates per mask check the
quotient transition and output. Direct Mahler recurrence and the predecessor
machine provide separate coefficient-output comparisons.

Additional explicit tests cover the nonfree Z/4 quotient, a noninvariant immediate
output kernel, an invalid mixed-modulus transition, and an invalid output relation.

## Result and limits
21,442 assertions passed; zero failures. Counts by assertion type and all mask
results appear in results/audit_observable.json. Twenty-five mask cases have a
strict observable-state reduction. No strict reduction is asserted universally.
Each authoritative subprocess had a 600-second wall-clock limit. A timeout would
be inconclusive, not evidence of a theorem or implementation failure. No tighter
memory or hardware limits were imposed by this runner. No final phase timed out.

Software: Python 3.13.5; SymPy 1.14.0. The aggregate schema1 manifest records the
exact command, software, range, seed and hashed outputs. Its inherited project-local
validator was run. Final command receipts separately pin every before/after source
hash. This is not a claim of running the installed plugin's schema2 validator.

Large-mask HNF and Smith calculations share SymPy. Their exact certificate checks
and the independent small-state partition oracle mitigate, but do not eliminate,
shared implementation risks. This is adversarial self-review, not independent
human review. All actual-mask tabulated values are finite Python evidence, not
separate reductions of the entire noncomputable Lean construction.
