# Greedy packet-selective posterior solver — proof note

Author: Komorebi P. Status: proved as written in the pinned Lean environment.
Base: v12 output-enclosure checkpoint. New namespace: Komorebi.AdaptivePosterior.

## Contract

Let M be the finite exact-rational factor-coded model

    P = L L^T, R = N N^T + sigma I, sigma > 0,
    S = H P H^T + R, v = y - H m, F(B) = P H^T - B S.

Let Q_a be complete self-adjoint mutually orthogonal rational output projectors,
and D_b complete self-adjoint rational input projectors. The dimensions may be
rectangular and the prior may be singular. A supplied seed inhabits the finite
output-label type, and a finite scan covers every output label. Duplicate scan
labels and arbitrary scan order are allowed.

For all positive rational epsilon and delta and every initial rational gain,
`runAdaptive` returns r with `PosteriorOutput.ResultValid M Q D epsilon delta r`:

- the returned candidate passes the model/packet/residual checker;
- its actual rounded score passes the requested tolerance;
- W2(actual Bayesian posterior, Joseph Gaussian of r.candidate.gain) <= epsilon;
- the returned mean/covariance arrays enclose the parameters of that same Gaussian;
- every array radius is at most delta;
- the reported parameter precision and arrays equal the actual output evaluator.

Successful-return soundness requires no caller-supplied validity hypotheses.
The program itself checks valid setup, positive epsilon, positive delta, and scan
coverage. Completeness uses those hypotheses to prove the guards and final check
succeed. The returned gain is an actual selective iterate within computed fuel,
by the separate `adaptive_solver_gain_origin` theorem.

The mean and covariance being enclosed are

    mu_B = m + B v,
    C_B = (I-BH) P (I-BH)^T + B R B^T.

Delta controls numerical representation of these approximation parameters, not
their coordinatewise distance from exact posterior parameters. The interval centers
do not independently define a certified Gaussian. The v12 PSD boundary remains.

## Local update and packet effects

Set tau = 1/(sigma + trace S) and q = (1-sigma/(sigma+trace S))^2.
The inherited innovation estimate gives 0 <= q < 1 and

    E(G (I-tau S)) <= q E(G),  E(G) = sum_ij G_ij^2.

For a selected output packet a, execute the exact-rational update

    B' = B + tau Q_a F(B).

Substitution proves

    F(B') = F(B) - tau Q_a F(B) S.

Orthogonality and idempotence give, for b != a,

    Q_b F(B') = Q_b F(B),   Q_b B' = Q_b B,
    Q_a F(B') = (Q_a F(B)) (I-tau S).

Thus complete output accounting yields the quantitative descent

    E(F(B')) <= E(F(B)) - (1-q) E(Q_a F(B)).

No assumption that innovation S preserves input packets is used. For any D,

    F(B') D = F(B) D - tau Q_a F(B) S D.

A zero output packet stays zero throughout the entire greedy trajectory, proved
by induction using the selected and unselected identities. This does not imply
that a zero input packet stays zero.

## Executable selection and global progress

`winner` scans the supplied list and replaces its incumbent only on a strict
energy increase. The initial label and every list member have energy no larger
than the returned label. The coverage hypothesis makes this a true maximum over
all output labels, even with repetitions or an unsorted list.

Write A = card(output labels), which is positive because a seed is supplied.
For the actually selected label a(B), completeness and the maximum property give

    E(Q_a(B) F(B)) >= E(F(B))/A.

Define r = 1-(1-q)/A. Then 0 <= r < 1 and every executed greedy step satisfies

    E(F(B_next)) <= r E(F(B)).

Iteration gives E(F(B_n)) <= r^n E(F(B_0)). The exact certificate score

    a(B) = E(F(B)) (sigma + ||v||^2)/sigma^2

has the same geometric bound. Selection is recomputed from the current gain on
every step, rather than supplied as a hypothetical favorable sequence.

The computable sufficient fuel is

    N = ceil_nat( a(B_0) / ((epsilon/2)^2 (1-r)) ).

The inherited quantitative geometric-fuel lemma establishes

    n >= N  ==>  a(B_n) <= epsilon^2/4.

This coarse rational bound avoids an approximate logarithm. It is sufficient,
not optimal. In the coordinate example it gives 410,093 although execution stops
after five updates; in the rotated example it gives 4,267 and stops after three.

## Rounded certification, stopping, and output

At each current gain B, `certifyGain` tries the supplied verification precisions,
then the inherited computed sufficient precision for inflation epsilon^2/4.
If any check passes, return immediately. Otherwise, update the selected output
packet and decrement the finite fuel. At the final permitted iterate the exact
score is at most epsilon^2/4, so the sufficient-precision fallback must pass.

`solveAdaptiveFuel_complete` connects a passing last permitted iterate to the
actual recursive early-stopping program. `solveAdaptive_terminates` supplies that
passing final iterate using the geometric bound. The probability theorem applies
the inherited checked posterior certificate to the returned candidate. The output
wrapper applies v12's `represent_spec` to that same gain and requested delta.

Main declarations:

- PacketSelectiveAlgebra: sum_left_energy, packetStep_residual,
  unselected_residual, selected_residual, unselected_gain, input_packet_effect,
  packetStep_energy_descent.
- GreedyPacketSelection: winner_ge_initial, winner_ge_member,
  selected_energy_share, adaptiveRate_bounds, greedy_energy_contract.
- GreedyPacketConvergence: greedy_energy_geometric, greedy_score_geometric,
  greedy_score_at_fuel.
- AdaptivePacketSolver: solveAdaptiveFuel_sound/complete,
  solveAdaptive_sound/terminates.
- AdaptivePacketOrigin: adaptive_solver_gain_origin.
- AdaptivePacketPosterior: adaptive_solver_reaches_posterior_tolerance.
- AdaptivePacketOutput: runAdaptive_terminates, runAdaptive_sound.
- AdaptivePacketInvariants: zero_packet_invariant,
  solveAdaptive_rejects_incomplete_scan.

## Checked concrete instances and boundary

Coordinate example: P=diag(4,1), H=[1,1], R=[1], y=[1], m=0, B0=0.
The selections are 0,1,0,1,0, returning B=(228/343,8/49)^T. The actual 12-bit
rounded score is 1525/1048576 <= (1/20)^2. Output precision is 32 bits for
delta=1/1000. Lean checks every selected label, actual program return, gain,
score, output precision, every center/radius, and the resulting ResultValid.

Rotated example: P=ones(2,2), H=R=I, y=(1,-1), m=0, B0=0, with the two rank-one
plus/minus projectors. Selections are 0,0,0, returning B=(39/125)ones(2,2).
The second output packet has zero exact residual throughout this run. The 12-bit
score is 215859/4194304 <= (1/4)^2. Output precision is 32 for delta=1/1000.
Small positive rounded upper bounds on exact-zero subpackets are allowed.

Boundary model: one state, two observations, H=(1,1)^T, P=[1], R=I, B=(-1/3,2/3).
It has S=[[2,1],[1,2]], tau=1/5, and F(B)=[1,0]. After the single-output-packet
step, F(B')=[3/5,-1/5]. The second input-packet energy grows 0 -> 1/25 while
total energy decreases 1 -> 2/5. These are kernel-checked equalities, together
with valid setup, rejection of an empty scan, and stable tie-breaking.

## Arithmetic and scope

Packet updates, model preprocessing, selection energies, fuel/budgets and final
comparisons are exact rational. Only the certificate graph and parameter-output
graph use the declared outward-rounded dyadic arithmetic. The separate v11 full
Richardson solver has a rounded-update theorem; this selective branch does not.

This closes one precise adaptive computation policy: change the updated output
packet according to its current residual and retain a guaranteed final posterior
certificate. The model and packet family remain fixed. It does not prove
hierarchy refinement, rounded selective-update convergence, scalable scanning,
performance superiority, posterior sampling, sequential filtering, uncertain-input
semantics, hardware arithmetic, or literature novelty.

## Evidence

All 12 new modules, including the complete declaration audit, compiled successfully.
The final seal validates all 90 active modules, using unchanged v12 receipts and
compiled hashes for 78 inherited modules. It is not a claim of 90 fresh compilations
in this block. There are 455 active theorem/lemma declarations, 69 new including
support lemmas and instances. All audited axioms are contained in propext,
Classical.choice and Quot.sound. No forbidden proof tokens occur in active sources.

The deterministic independent scalar-sum diagnostics cover six matrix shapes,
eight updates each, the two complete example outputs, eight expected rejections,
and 911 assertions. These computations are bounded diagnostics, not substitutes
for the universal Lean proofs. The final Mathbox computation manifest validates.
Three deliberately invalid Lean controls were separately rejected. Five current
block draft compiler failures were corrected; inherited history includes six more.
No incomplete compilation source snapshot remains. See FAILURE_LOG.md and the
source/log/output/dependency hashes in FINAL_VERIFICATION_RECEIPT.json.
