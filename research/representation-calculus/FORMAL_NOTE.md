# Torsion-safe optimality for certified representations

## Status and lineage

The sole representation-calculus predecessor is v0.3, archive SHA-256
`5ad2fa7216d9d940d1c0b0f31ffce998a1425765188947be4f31db7f2ef1974c`.
That archive is included verbatim under history. This is not p-adic Block 16.
The three module-generator source files imported from the separate p-adic Block 15
archive are included unchanged with their provenance. No replay of the entire
p-adic corpus is claimed.

This release closes the universal prime-power free-linear coordinate lower bound
for the actual v0.3 matrix certificate. It also proves a stronger version: the
competing target may have arbitrary deterministic operations and observations,
provided its **initial encoding is linear**, and every source state and every
future input word have the specified outputs. This initial-state interface is
load-bearing and is not the single-seed orbit problem.

The new formal core uses pinned Mathlib. To permit Lean's module system to import
both it and the predecessor's Std-only sources, the predecessor sources receive a
mechanical header conversion: `module`, `public import`, and an exposed public
section. Definition/proof bodies are unchanged. The original files remain in the
frozen predecessor. All converted sources are rebuilt, not assumed compatible.

All proof interpretation is self-review. Neither standard module theory nor the
underlying realization principle is claimed historically new. Counts and actual
execution status belong to RESULTS.md and the execution records.

## 1. The precise contract

Let p be prime, r>=1, and R=Z/(p^r). A source is the complete state module R^d,
with finite operation matrices A_a and observation matrix O. Words are read
left-to-right; a::w acts first by A_a and then by the matrices for w. Empty words
are included, with no bounded observation horizon substituted for all words.

A valid inherited certificate supplies P with t rows, target transition matrices
C_a, decoder D, and observation-word provenance G, W, satisfying

    P A_a = C_a P,       O = D P,       P = W G.

Rows of G are actual rows O_j A_w, not unconstrained vectors with word labels.
v0.3 proves

    Beh(x)=Beh(y) iff P x=P y,

and describes the actual image of P, not the whole ambient free array R^t.

A Smith-image certificate supplies an invertible change V with checked inverse,
width t<=d and nonzero elements w_i of R, satisfying

    P V = [diag(w_i) 0].

For the generated certificates w_i=p^s_i with 0<=s_i<r. The universal lower bound
needs only nonzero weights and the certified diagonal image description; sorting
or a newly computed Smith algorithm is not an assumption.

## 2. The exact theorem, including nonlinear target operations

Suppose a competitor consists of

* an arbitrary deterministic system U on R^n with the same operation alphabet,
  observation indices and observation values R;
* an R-linear initial encoding e:R^d -> R^n;
* all-state, all-word output correctness:

    Beh_source(x)(w,j) = Beh_U(e(x))(w,j) for every x,w,j.

Then

    t <= n.

Conversely the certified target matrices C_a, decoder D and encoding P realize
the source on R^t. These target operations and observations are themselves linear.
Thus for every coordinate budget b,

    exists a sufficient competitor of size n<=b with linear initial encoding
        iff t<=b.

Formal endpoints:

    prime_certificate_linear_lower
    prime_certificate_minimum_iff

The same t is therefore the exact minimum in the narrower, conventional class
where the encoding, transitions and observations are all linear. The proof uses
no local intertwining assumption on a competitor. Such equations are proved for
the constructed upper-bound machine, not demanded of every lower-bound competitor.

## 3. Proof, without a cardinality shortcut

### 3.1 The competitor's encoding kernel can lose no required distinction

If e(x)=e(y), correctness of the competitor makes their outputs agree after every
word. The inherited exact certificate theorem then gives Px=Py. This implication
uses only equality of the target starting states; it needs no linearity of U.
It is the theorem `sufficient_encoding_kernel`.

### 3.2 The competitor's actual image surjects linearly onto the principal factors

Let E=range(e)<=R^n and

    Y = product_(i:Fin t) w_i R.

For z=e(x), define F(z)=Px interpreted in Y. It is well-defined by 3.1. It is
linear because both e and P are linear: compare representatives for addition and
scalar multiplication using the same kernel implication. The Smith-image theorem
makes F surjective. The code constructs this map by choosing source preimages,
then proves well-definedness through equality and proves surjectivity separately.
It never divides by a weight in R.

Formal objects:

    encodingToPrincipal
    encodingToPrincipal_apply
    encodingToPrincipal_surjective

### 3.3 A submodule of n free residue coordinates needs at most n generators

Lift E along Z^n -> (Z/(p^r))^n. The inverse image is an integer submodule of Z^n.
A basis over the PID Z has at most n elements. Reducing those basis elements
generates E over R. This is the exact imported theorem
`KomorebiPadic.zmod_submodule_generators`.

The field/PID hypothesis is applied to Z, not falsely applied to the non-domain R.
The proof is not a claim that E is free over R.

### 3.4 The product of t nonzero principal ideals needs at least t generators

Choose the ideal generators w_i. Given q hypothetical generators of Y, express
their coordinates relative to w_i. Reduction of this coefficient matrix gives a
surjection F_p^q -> F_p^t. Why? An annihilator of nonzero w_i must reduce to zero
modulo p, since otherwise it would be a unit and force w_i=0. Hence the equations
expressing arbitrary ideal elements descend to the required field-coordinate
surjection. Field dimension forces q>=t.

Crucially this reduces coefficients **relative to the chosen ideal generators**.
It does not reduce the original ambient ideal elements and discard torsion.
The exact imported theorem is
`KomorebiPadic.primePrincipalFamily_generator_lower`.

Combining 3.2--3.4 gives t<=mu(E)<=n. The upper bound is the inherited explicit
matrix transport after proving that the predecessor's matrix-vector operation
is a genuine Mathlib linear map (`matrixLinear`).

## 4. All 202 accepted predecessor certificates receive exact minima

Thirteen generated MinimumBatch modules, imported by CertifiedMinima, reuse each frozen source certificate's
actual Valid proof and Smith identity. It adds a checked nonzero-weight proof
and instantiates the generic theorem at that source's actual prime, precision,
matrices, observations and dimensions. `FinRingCompatibility` proves agreement of the
predecessor Std modular arithmetic and the Mathlib ring operations. The modulus
wrapper checks the actual equality m=p^r once, rather than repeatedly expanding
large concrete matrix expressions during elaboration. No source states or input words are
enumerated to prove the universal conclusion.

Seventeen of the certificates have t=0. They are included: a zero-coordinate
free module has one state, the observations factor through it, and its minimum
is zero. The nonzero-weight premise is vacuous only for this empty index type.

The large 2^128-source-state example is included, but its two-coordinate optimum
was already established in v0.3 by a special cardinality argument. The present
advance is that **all** certificates now get the general algebraic optimum.
In 21 of the 202 inherited fixtures, ceil(log_(p^r)|Y|) is strictly below t, so
cardinality alone does not supply the desired lower bound.

The new `export_minimum_lean.py` invokes the unchanged independent Python checker
and emits an untrusted symbolic Lean file including its minimum theorem. Writing
such a file is not the same as Lean accepting it; compilation remains required.
The parser, discoverer, Smith implementation and exporter are not verified
executable programs. Lean proves the proposition about the literal source data.
The separately supplied intended source is still checked by the external checker.

## 5. Why the initial-encoding hypothesis cannot be dropped

Over R=Z/16, take identity dynamics on R^2 with observations

    O(x,y) = (8x,8y).

The certified image is 8R x 8R, with two nonzero order-two factors. The theorem
forces at least two coordinates for every sufficient linear initial encoding,
even with nonlinear target operations.

Nevertheless these four behaviors fit into ONE residue under the nonlinear code

    code(x,y) = (x mod 2) + 2*(y mod 2) in R.

The target has identity dynamics and decodes

    (8*(code mod 2), 8*((code div 2) mod 2)).

Lean proves all-word correctness of this nonlinear encoding and proves that it
is not additive. It therefore demonstrates the precise boundary of the general
minimum theorem, not a contradiction to it. The written and executable source
are the same explicit finite profile. The nonlinear example's local observation
identity is kernel-evaluated on its small domain; the all-word result follows
from the generic transport theorem.

Formal endpoints:

    TorsionBoundary.two_linear_coordinates_necessary
    TorsionBoundary.one_nonlinear_residue_suffices
    TorsionBoundary.packing_is_not_additive

The finite audit also checks an explicit kernel-separation witness against every
one-row linear encoding over R: 256 possible rows. This is a finite independent
audit, not the proof of the general prime-power theorem.

## 6. What has not been proved

* This is not a lower bound for arbitrary algorithms, bit memory, neural-network
  size, or a single seeded deterministic automaton.
* Allowing nonlinear initial encodings changes the optimum, as Section 5 proves.
* This does not formally verify the Python discovery loop or its termination.
* No new held-out structural discovery, trained proposer, performance comparison,
  multi-input or stochastic calculus, global arithmetic theorem or historical
  novelty claim is made.
* A kernel-checked statement about literal matrices is not automatically the
  intended informal problem; semantic translation is still a separate obligation.

## 7. Next discriminating work

The current finite-linear pipeline now has witnessed representation discovery,
all-state/all-word semantic exactness, actual-image factorization, and the generic
sharp linear-encoding minimum. Its next useful evaluation should freeze an unseen
structural family before discovery and compare equal-budget variants with and
without the representation registry and failure witnesses. A separate formal
route can verify the row-closure algorithm and its finite module-length ranking.
Neither evaluation success nor verified executable discovery follows from the
optimality theorem completed here.
