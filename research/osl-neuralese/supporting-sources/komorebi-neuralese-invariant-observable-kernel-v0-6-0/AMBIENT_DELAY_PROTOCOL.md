# ANC-4 Ambient-Delay Calibration Protocol

**Author:** Komorebi P.  
**Status:** deterministic oracle calibration, separate from the v0.5 flatness panel

## Purpose

Version 0.4 provided a genuine rank-four complement but did not make that
complement necessary. The trained system could solve its semantic task while
remaining functionally confined to the rank-eight anchor plane. ANC-4 supplies
the missing positive calibration: an online task in which an exact
eight-dimensional semantic anchor and four independent continuous lag values
must coexist in recurrent state.

This block does not train a model. It defines an exact oracle, a conditional
minimality certificate, and causal counterfactuals that a later learned system
must reproduce. It is intentionally independent of the flatness and holonomy
objectives.

## Online contract

Let the recurrent state have a semantic projection

\[
\pi:H\rightarrow\mathbb R^8.
\]

At every time step the semantic state is exactly saturated:

\[
\pi h_t=e_{s_t}.
\]

The input is an arbitrary continuous scalar stream. The delay head must answer
at every eligible time, not only at one terminal query:

\[
y_t=u_{t-4},\qquad t\ge 4.
\]

The recurrent state is the sole temporal channel. The contract excludes
attention to earlier inputs, a sequence canvas, caches, persistent
normalization buffers, an external clock, episode identifiers, parameter
updates, and uncounted side state.

The canonical oracle is

\[
H=\mathbb R^8\oplus\mathbb R^4,
\qquad
h_t=(p_t,q_t),
\]

with

\[
p_t=e_{s_t},
\qquad
q_t=(u_{t-4},u_{t-3},u_{t-2},u_{t-1}).
\]

Writing the four-stage shift as

\[
S=
\begin{bmatrix}
0&1&0&0\\
0&0&1&0\\
0&0&0&1\\
0&0&0&0
\end{bmatrix},
\quad
b=e_4,
\quad
d^\top=e_1,
\]

the update is

\[
q_{t+1}=Sq_t+bu_t,
\qquad
y_t=d^\top q_t.
\]

The memory transition is nilpotent. It is not an orthogonal recurrent
operator. Metric isometry and open input-driven memory are separate
mechanisms.

## What is coordinate independent

In canonical coordinates,

\[
P=
\begin{bmatrix}
I_8&0\\0&0
\end{bmatrix},
\qquad
Q=I-P.
\]

Mathematically, under an arbitrary invertible coordinate change \(x'=Tx\),
every object is transported:

\[
\pi'=\pi T^{-1},
\quad
P'=TPT^{-1},
\quad
Q'=TQT^{-1},
\quad
A'=TAT^{-1},
\quad
B'=TB,
\quad
C'=CT^{-1}.
\]

The invariant ambient object is the vertical fiber

\[
K=\ker\pi.
\]

The matrix \(Q\) is a choice of splitting. After a nonorthogonal coordinate
change it may be an oblique projector, and it need not select the last four
displayed coordinates. All ANC-4 counterfactuals must remain unchanged under
the transported split. The implementation derives the semantic rank from the
registered right-inverse witness \(\pi' E'=I_8\), rather than thresholding the
raw singular values of \(\pi'\). That certificate is invariant even when a
valid coordinate gauge is poorly scaled; singular values remain diagnostics,
not the algebraic rank decision. The floating-point implementation accepts only
gauges that remain numerically resolvable under the precision contract below.

## Hankel and minimality certificate

The four-step controllability and observability matrices are

\[
\mathcal R_4=[b,Sb,S^2b,S^3b],
\qquad
\mathcal O_4=
\begin{bmatrix}
d^\top\\d^\top S\\d^\top S^2\\d^\top S^3
\end{bmatrix}.
\]

Both have rank four. The registered delay Hankel matrix is

\[
\mathcal H_4=
[d^\top S^{i+j}b]_{i,j=0}^{3}
=J_4,
\]

where \(J_4\) is the four-by-four reversal matrix. Therefore

\[
\operatorname{rank}\mathcal H_4=4.
\]

This proves that the delay channel has minimal linear realization dimension
four. The registered certificate additionally verifies

\[
S^4=0,
\qquad
d^\top S^k b=\mathbf 1[k=3]\quad (0\le k<8),
\]

so a rank-four system with an extra delayed echo cannot pass merely by matching
the first four-by-four Hankel block. In registered internal memory coordinates,
\(S\), \(b\), and \(d\) are zero/one tensors and must match the canonical delay
triplet bit-for-bit. Exact \(S^4=0\) is the sufficient exclusion of every later
Markov tail; the eight displayed coefficients are an additional diagnostic.

The total lower bound is conditional. Eight semantic classes alone do not
require eight real coordinates, and a finite binary history can be encoded in
one ideal real number. The valid statement is:

> Twelve is minimal among continuous online realizations satisfying the exact
> rank-eight saturated-anchor contract and using recurrent state as the sole
> temporal channel.

For the nonlinear form, let \(H=\mathbb R^n\) be a finite-dimensional real
vector state space and let \(\pi:H\to\mathbb R^8\) be a fixed surjective linear
map. Fix the inputs before the four-lag window, the semantic trajectory, and the
future continuation. The four most recent continuous inputs range over an open
set \(U\subset\mathbb R^4\). Their state map \(F:U\to H\) then lies in one fiber
of \(\pi\). The next four outputs recover the original delay window, so a
continuous map \(Y\) satisfies

\[
Y\circ F=I_U.
\]

Thus a four-dimensional open set embeds in a fiber of dimension
\(\dim H-8\). Hence

\[
\dim H-8\ge4.
\]

For differentiable systems the same conclusion follows from
\(D(Y\circ F)=I_4\).

## Registered causal calibrations

### Q deletion

Construct a state whose semantic coordinate is exactly \(e_s\) and whose
vertical coordinate contains a continuous four-value history. Compare its next
four delay outputs with those obtained after

\[
h_t^{\setminus Q}=Ph_t.
\]

The oracle must satisfy all of the following:

- the native four-output vector equals the stored history
- Q deletion changes every nonzero-history case
- the deleted delay vector is zero under zero future input
- the semantic projection is unchanged exactly
- the result is invariant under a registered coordinate conjugation

The primary causal change rate is conditioned on histories whose infinity norm
exceeds the registered numerical bound. The evaluator reports that denominator
and the unconditional rate separately, so zero or numerically unresolved
histories cannot dilute the primary rate or silently disappear.

### Q transplant

Take donor and recipient histories with the same semantic state and form

\[
h_t^{\mathrm{swap}}=Ph_t^{\mathrm{recipient}}+Qh_t^{\mathrm{donor}}.
\]

The next four delay outputs must become the donor sequence while the semantic
projection remains the recipient anchor. The evaluator reports the donor
match rate and the change rate only on pairs with distinct history vectors.

These are causal interventions with exact predicted consequences. Nonzero
Q-energy, probe decodability, or a visible four-dimensional subspace is not a
substitute.

## Later learned-system requirements

The direct-sum shift register is an oracle ceiling, not the principal learned
architecture. A learned arm should receive the scalar through a generic input
mixer. Exact semantic canonicalization must prevent history from hiding in
logit margins or unused semantic directions.

A learned ANC-4 claim additionally requires:

- online accuracy at every eligible time and variable stream length
- independent continuous inputs and semantic trajectories
- paired histories differing only in the causally queried lag
- survival after replacing \(Ph_t\) by the exact semantic anchor
- destruction after Q deletion
- predicted four-output transfer after Q transplantation
- failure of P-only and energy-matched random controls to reproduce transfer
- rank four for the Jacobian from the four-lag window to the vertical state
- explicit accounting of every persistent variable as recurrent state

A dimension-by-delay phase diagram over ambient rank \(q\) and delay \(d\)
should test the boundary \(q\ge d\). For approximate linear systems with
\(q<4\), the reversal Hankel target gives the non-arbitrary lower bound

\[
\|\widehat{\mathcal H}_4-J_4\|_F\ge\sqrt{4-q}.
\]

## Numerical and coherence contract

The supported storage dtypes are float16, bfloat16, float32, and float64. Small
rank, inverse, and receipt calculations copy the serialized tensors to CPU
float64. They never request float64 linear algebra on the model's source device,
so certification does not fail merely because an accelerator lacks float64.
Native delay execution remains in the registered storage dtype.

For a matrix dimension \(n\), validation uses the bounded relative tolerance

\[
\tau_{\mathrm{val}}
=\min\!\left(\frac1{16},
\max(32\epsilon_{64},4n\epsilon_{\mathrm{dtype}})\right).
\]

The cap keeps every identity and right-inverse check nonvacuous even in
bfloat16: an all-zero matrix cannot pass as an identity. Numerical rank uses

\[
\tau_{\mathrm{rank}}
=\max\!\left(\tau_{\mathrm{user}},
\min\!\left(\frac1{8},
\max(32\epsilon_{64},2n\epsilon_{\mathrm{dtype}})\right)\right).
\]

A coordinate map is accepted only when
\(\kappa_2(T)\tau_{\mathrm{rank}}<1/4\). More ill-conditioned gauges are
mathematically valid but not identifiable at the registered storage precision,
so they fail closed rather than changing the reported numerical rank.

The coordinate map and its inverse, the semantic and memory split, and both
projectors are checked in both directions. The redundant runtime tensors are
not independent degrees of freedom: the stored values must agree bit-for-bit
with

\[
P=E\pi,\quad Q=M\mu,\quad
A=M S\mu,\quad B=M b,\quad C=d^\top\mu.
\]

This prevents a receipt from certifying one memory system while execution uses
another. Frozen dataclasses do not freeze tensor storage, so the complete
contract is revalidated before certification and public state execution; an
in-place tensor mutation therefore fails closed.

For causal output comparisons, the default scalar tolerance is

\[
\tau_{\mathrm{eval}}
=\min\!\left(\frac1{32},
\max(32\epsilon_{64},8\epsilon_{\mathrm{dtype}})\right),
\]

and example \(i\) receives the scale-aware bound
\(\tau_{\mathrm{eval}}\max(1,\|h_i\|_\infty)\). A transplant uses the maximum
recipient/donor scale. Thus changing packet units does not turn ordinary
roundoff into a scientific failure.

## Deterministic self-check

The implementation in `src/komorebi_neuralese/ambient_delay.py` provides:

- the exact canonical oracle
- a deterministic, well-conditioned dense nonorthogonal coordinate change
- transported P and Q projectors
- controllability, observability, and block-Hankel constructors
- a right-inverse semantic-rank witness plus Hankel, nilpotency, Markov-tail,
  controllability, and observability receipts
- Q-deletion and Q-transplant evaluators
- a JSON-safe deterministic self-check

The deterministic change populates both semantic-to-memory and
memory-to-semantic blocks. The self-check also evaluates eight consecutive
outputs from a loaded packet: the first four must equal the packet and the next
four must be zero.

Run the self-check from an installed package or with `src` on `PYTHONPATH`:

```powershell
python -m komorebi_neuralese.ambient_delay
```

The self-check is valid only if the canonical and conjugated oracles both
certify ranks \(8+4\), deletion removes the complete delayed packet without
altering semantics, transplantation transfers the complete four-output
sequence, and all coordinate-conjugacy residuals remain within the declared
floating-point tolerance.

## Claim boundary

Passing ANC-4 establishes that a four-dimensional vertical fiber can be both
necessary and causally sufficient for an independent continuous delay packet
under the exact saturated-anchor contract. It does not establish that a
learned model discovered this realization, that ambient state resolves
semantic holonomy, that four coordinates are unconditionally necessary for
all encodings, or that the mechanism bears on awareness or consciousness.
