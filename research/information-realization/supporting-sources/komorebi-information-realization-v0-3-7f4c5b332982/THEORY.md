# Information Realization and Obstruction
## Access-aware packet repair and predictive closure · v0.3.0

**Operation Komorebi / Realization Calculus**  
**Date:** 15 October 2026  
**Scope:** finite deterministic realizations, linear maps over finite fields, a bounded adapter to the existing Haar packet implementation.  
**Proof status:** mathematical proofs below, exact finite checks in the package. No Lean compilation. No novelty or universal-information claim.

This continuation connects the v0.2 information layer to an existing packet implementation. Its main question is not merely how much information a representation lacks. It is whether the component supplying a repair can access the information it must send, and whether the repair makes a dynamical representation sufficient for future tasks.

The complete preceding development is retained, unchanged, in `prior_v0_2/`. Its uncertainty, Bayes-error, categorical residual, and probability-support conventions remain in force.

## 1. Declare the experiment before measuring it

Let the state space be the entire vector space V = F_q^n, including the zero-dimensional case. The field order q is a prime power. The implementation in this release supports prime fields only.

There are three linear maps:

\[
R:V\to O,\qquad F:V\to Y,\qquad U:V\to E.
\]

The decoder knows Rx. The task is to recover Fx. A single encoder sees only Ux and sends a noiseless message to the decoder. The encoder knows the fixed matrices defining the experiment, but does not receive Rx or x unless those are obtainable from Ux.

Zero-error recovery means correctness for **every** x in V. The communication alphabet is distinct from the cost of measuring Ux, the number of native packet objects, the number of field coordinates, latency, and numerical robustness. No distribution is needed for the exact repair theorem. A uniform prior is introduced only for the entropy and probability formulas.

Define

\[
d_R(F)=\operatorname{rank}\begin{bmatrix}R\\F\end{bmatrix}-\operatorname{rank}R
=\dim F(\ker R).
\]

The information alphabet in each observation fiber is q^{d_R(F)}. This was proved in v0.2. The present question is whether an encoder restricted to Ux can attain that bound.

## 2. The access-aware linear repair theorem

### Theorem A. Feasibility, optimality, and a constructive certificate

The following are equivalent:

1. Some encoder depending only on Ux, with an arbitrary finite alphabet, permits exact recovery of Fx together with Rx.
2. \(\ker R\cap\ker U\subseteq\ker F\).
3. \(\operatorname{row}F\subseteq\operatorname{row}R+\operatorname{row}U\).
4. There exist matrices H and G such that
   \[
   F=G\begin{bmatrix}R\\HU\end{bmatrix}.
   \]

When these conditions hold, H can have exactly d = d_R(F) rows, and the least possible message alphabet has size

\[
\boxed{q^d.}
\]

This is optimal even among nonlinear encoders. A joint fixed-width binary encoding needs \(\lceil\log_2(q^d)\rceil\) bits, computed exactly as `(q**d - 1).bit_length()`.

**Necessity.** If v lies in ker R intersect ker U but Fv is nonzero, the states 0 and v give the decoder the same observation and the encoder the same input. Every allowed message is the same for those states, while the correct answers differ. No message alphabet can resolve that pair.

**Equivalence with row spaces.** Over a finite-dimensional field, a linear map F is zero on the kernel of the stacked map [R;U] exactly when F factors linearly through [R;U]. Equivalently, every row of F lies in the row space of [R;U]. This follows by defining the induced map on the image and extending a basis, or by row reduction.

**Construction achieving d coordinates.** Select rows D of F whose classes form a basis of (row R + row F)/row R. There are d such rows, and row [R;D] = row [R;F]. By feasibility, write

\[
D=A_0R+HU.
\]

The encoder sends c = HUx. It does not need Rx. The decoder computes Dx = A_0Rx+c and hence Fx. Equivalently, it uses a matrix G satisfying the displayed factorization. The rows of HU remain independent modulo row R: a dependence among their classes would give the same dependence among the classes of D. Thus the message supplies exactly the missing d directions, rather than surplus task-irrelevant directions.

**Lower bound.** In a nonempty observation fiber x_0+ker R, the task assumes exactly q^d values. Distinct task values cannot receive the same message under zero-error decoding in that fiber. Therefore every encoder, linear or not, needs at least q^d message values. The construction attains this bound. For d=0, the message has one possible value and transmits zero bits. ∎

### What is special about this conclusion?

For a general finite domain, restricted encoder access may increase the minimum alphabet without making recovery impossible. The five-cycle example in v0.2 needs three target-only symbols instead of two state-aware symbols. Theorem A uses the full vector-space domain and linear R, F, U. Those hypotheses make a d-coordinate linear repair possible whenever any repair is possible.

It is a single-encoder, single-decoder theorem. It does not assert optimality of linear coding for arbitrary networks, multiple receivers, arbitrary support constraints, distributed encoders, or noisy channels. Prior work on coded side information and function updates studies related, often more complicated coding problems [1,2]. We supply this elementary specialization and its proof rather than claim an unqualified new coding theorem.

### The certificate interface

A successful certificate contains H, C, and G, with

\[
C=HU,\qquad G[R;C]=F,\qquad \#\mathrm{rows}(C)=d.
\]

A separate checker evaluates these identities in exact modular arithmetic. An infeasible certificate contains v with Rv=Uv=0 and Fv nonzero. Such a witness proves impossibility under the declared access rule, not merely failure of the particular repair algorithm.

## 3. Quantifying the repair

For a uniform source on V, a conditional task distribution in an observation fiber is uniform on an affine image of dimension d. Therefore

\[
\boxed{
K_R(F)=q^d,\quad H(F\mid Rx)=d\log_2q,\quad
E_R(F)=V_R(F)=1-q^{-d}.
}
\]

Here E is optimal exact-answer error, and V is the unhalved categorical quadratic residual from v0.2. The equality E=V is specific to the uniform conditional distributions in this model. For a nonuniform prior, the structural alphabet is still q^d, but the entropy and risk values must be calculated from the prior.

Theorem A identifies the endpoint of perfect recovery. It does **not** identify every smaller-budget optimum. The worked GF(3)^2 example has identical exact minimum alphabets for a state-aware encoder and a target-only encoder, but a two-symbol budget yields successes 4/5 and 11/15 respectively. Thus no exact-access penalty does not mean no probabilistic-access penalty.

## 4. Packet transfer as an information obstruction

Suppose an invertible linear analysis transform A expresses a state in packet coordinates p=Ax. Let T be a linear state transfer. Its packet-coordinate form is

\[
B=ATA^{-1}.
\]

Partition coordinates into retained observations o and hidden coordinates z. For the next retained output,

\[
\begin{bmatrix}o'\\z'\end{bmatrix}
=
\begin{bmatrix}B_{oo}&B_{oz}\\B_{zo}&B_{zz}\end{bmatrix}
\begin{bmatrix}o\\z\end{bmatrix}.
\]

### Theorem B. Leakage rank is the exact task deficit

For the task o' and current observation o,

\[
\boxed{d_o(o')=\operatorname{rank}B_{oz}.}
\]

**Proof.** Fixing o leaves z free over its full coordinate space. The possible next observations form the affine space B_oo o + image B_oz. Its dimension is the rank of B_oz. Apply the fiber theorem. ∎

Consequently, the retained coordinates evolve autonomously exactly when B_oz=0. If the encoder has enough access to resolve the hidden contribution, Theorem A produces the optimal supplement. If it sees only selected hidden packets, the kernel feasibility test decides whether that access suffices.

This is the typed connection between a transfer block and an operational information requirement. It is not a scalar score pasted onto packet terminology.

### Composition and cancellation

For two transfers with the same retained/hidden coordinate split,

\[
\boxed{(B_2B_1)_{oz}=B_{2,oo}B_{1,oz}+B_{2,oz}B_{1,zz}.}
\]

This follows by block multiplication. In particular,

\[
\operatorname{rank}(B_2B_1)_{oz}
\leq \operatorname{rank}B_{1,oz}+\operatorname{rank}B_{2,oz}.
\]

The terms can cancel. Thus endpoint task deficits need not add, even when both individual transfer blocks depend on hidden coordinates. This does not violate data processing: the task at the endpoint is different from the task of reconstructing every intermediate output, and the physical underlying state has not necessarily discarded its hidden coordinates.

The defect for an entire observed trajectory is the rank increment of the stack [R;RT;...;RT^h]. It is nondecreasing with h. The endpoint defect uses RT^h alone and can fall or oscillate. The worked shift example exhibits both behaviors explicitly.

## 5. Closing a representation under future operations

For linear actions T_1,...,T_k, start with W_0=row R and iterate

\[
W_{j+1}=W_j+\sum_i W_jT_i.
\]

### Theorem C. Minimal predictive closure

This sequence stabilizes after at most n-rank R strict enlargements. If S has a row basis of the stable space, there exist matrices D and M_i with

\[
\boxed{R=DS,\qquad ST_i=M_iS.}
\]

For every finite action word, the observation sequence is exactly predictable from Sx. Any other linear representation that contains R and evolves under every action must contain the row space of S.

**Proof.** Dimensions are nondecreasing and bounded by n. If one step leaves the dimension unchanged, equality of nested subspaces makes that space invariant under every T_i, so no later enlargement is possible. At a stable space, the displayed factorizations follow from row inclusion. Repeated substitution gives the induced evolution for every action word. Any invariant row space containing R contains every W_j by induction, so it contains the limit. ∎

A stronger observational interpretation follows directly. W_j is the span of the rows of R composed with all action words of length at most j. Two source states give identical outputs under every finite word exactly when their difference lies in ker S. Therefore S also realizes the coarsest operational equivalence classes, up to a bijection onto its image. This does not assert that S is causally recoverable from the current R alone.

A predictive model can therefore be complete for all declared future questions while still being incomplete for source reconstruction. The Haar shift example has a three-coordinate predictive state for a four-coordinate source.

## 6. Importing an existing Komorebi construction without changing its meaning

The adapter uses the unchanged `komorebi_math-1.0.0b4-4b21-py3-none-any.whl`. The Haar module's Git blob hash matches the `wavelets.py` returned by the connected GitHub read during this continuation. The package records the wheel and module hashes. This is a pinned file-level integration, not a claim that all repository modules are current or validated.

The library's unnormalized Haar split is the sum/difference transform. Its runtime arrays are floating point. `normalized=False` is **not** a claim of arbitrary-precision arithmetic. The adapter compares native impulse responses with a separate Python-integer recurrence, forms the exact integer analysis matrix, and reduces that matrix into a declared prime field. For actual data it permits only bounded integer inputs whose intermediate sums remain exactly representable, checks the native outputs before reduction, and rejects unsupported inputs. The library itself is not claimed to implement finite-field arithmetic.

The decoder in erasure experiments receives only selected coefficient tuples and the permitted encoded supplement. It never receives the whole `HaarPacketTree`, which also contains hidden coefficients and the source signal. A complete pruning is an invertible representation, not an information-erasure mechanism. An incomplete pruning is not passed off as a supported reconstruction call.

The library's `entropy_cost` concerns normalized squared coefficient magnitudes, with natural logarithms. It has no source prior or target argument. It is not the task conditional entropy used here. Tiny energy can encode noiseless distinctions, while large energy can be constant and carry no uncertainty. A physical noise model is needed before turning amplitude into an operational robustness claim.

## 7. Scope, proof levels, and remaining obligations

The general statements above have mathematical proofs. The executable exact tests corroborate them in explicitly enumerated finite families and check returned certificates independently. Native-library tests additionally validate the pinned implementation on declared bounded inputs. None of these records is a compiled Lean proof or a probability that a universal theory is correct.

A future formal port should first prove the factorization, access-feasibility, and predictive-closure identities and link certificates to their typed matrices. A broader signal extension needs numerical stability, explicit noise, and measurement costs. A multi-encoder or multi-receiver extension needs its own coding theorem, not an unchecked reuse of Theorem A.

## References and lineage

[1] Namyoon Lee, Alexandros G. Dimakis, and Robert W. Heath Jr. *Index Coding with Coded Side-Information*. arXiv:1501.00077, 2014/2015. This treats a multi-user coded-side-information problem. It is related prior art, not the source of an assertion that our simpler theorem solves that broader setting. https://arxiv.org/abs/1501.00077

[2] Suman Ghosh and Lakshmi Natarajan. *Codes for Updating Linear Functions over Small Fields*. arXiv:1901.02816v1, 2019. This treats sparse function updates with restricted transmitter knowledge and links them to functional index coding. Those support restrictions differ from the full-vector-space domain of Theorem A. https://arxiv.org/html/1901.02816v1

[3] Operation Komorebi. *Information Realization and Obstruction*, v0.2.0. Retained in `prior_v0_2/THEORY.md`, including its classical probability, coding, and observability references.

[4] Komorebi Math, `signals/wavelets.py` and `signals/filterbanks.py`. Pinned source hashes and retrieval lineage appear in `PROVENANCE.json`. The wheel is retained without source modifications.
