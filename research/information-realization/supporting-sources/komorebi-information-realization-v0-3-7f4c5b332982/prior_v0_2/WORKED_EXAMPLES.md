# Worked Examples
## Information Realization and Obstruction · v0.2.0

Every example below has an executable counterpart in `examples/worked_examples.py`. The script checks the stated exact values and writes `reports/worked_examples.json`. These are finite mathematical experiments with known ground truth, not tests of a trained model or a production Komorebi library.

The common setup is an underlying state, an available observation, a specified task, and a declared repair mechanism. We use four quantities:

\[
B=\lceil\log_2K\rceil,\quad H=H(F\mid R),\quad
E=\text{minimum exact-decoding error},\quad
V=\mathbb E\|e_F-P(F=\cdot\mid R)\|^2.
\]

Here \(K\) counts the most distinct task answers in any observation fiber. \(B\) is the fixed-width supplemental bit budget for a state-aware encoder. \(V\) is the unhalved multiclass Brier residual, which is invariant under task-label permutations. Scalar MSE is reported separately where a numerical target has been explicitly chosen.

## Example 1. A partially observed dynamical system

### State, observation, and task

Let \(X=(a,b,c)\) be three bits, with

\[
T(a,b,c)=(b,c,a\oplus b).
\]

Only the first coordinate is observed. The observations at times 0, 1, and 2 are therefore \(a,b,c\). The task is exact recovery of the **initial** three-bit state.

Take independent coordinates with

\[
P(a=1)=\tfrac12,\quad P(b=1)=\tfrac14,\quad P(c=1)=\tfrac18.
\]

The eight states, in binary lexicographic order, have weights

\[
(21,3,7,1,21,3,7,1)/64.
\]

This prior is fully specified. No distribution was fitted to favor the result.

### Exact structural deficits

Observing \(a\) leaves four possible initial states per observation. Observing \((a,b)\) leaves two. Observing \((a,b,c)\) leaves one:

\[
K=4,2,1,\qquad B=2,1,0.
\]

The predictive partition algorithm independently returns 2, 4, and 8 distinguishable classes, then stabilizes.

### Entropy and optimal decoding

Conditional on \(a\), the possible \((b,c)\) values have probabilities

| Missing bits \((b,c)\) | Probability |
|---|---:|
| \((0,0)\) | \(21/32\) |
| \((1,0)\) | \(7/32\) |
| \((0,1)\) | \(3/32\) |
| \((1,1)\) | \(1/32\) |

The optimal initial guess is therefore \((a,0,0)\), with success \(21/32\) and error \(11/32\). After learning \(b\), the optimal remaining guess is \(c=0\), with error \(1/8\).

Using the binary entropy function \(h_2\),

\[
H(F\mid a)=h_2(1/4)+h_2(1/8)=1.354842567658729\ldots,
\]

\[
H(F\mid a,b)=h_2(1/8)=0.543564443199596\ldots.
\]

| Available observations | Classes | Extra fixed-width bits | Conditional entropy | Optimal error | Categorical residual \(V\) |
|---|---:|---:|---:|---:|---:|
| \(a\) | 2 | 2 | 1.354843 | \(11/32\) | \(131/256\) |
| \(a,b\) | 4 | 1 | 0.543564 | \(1/8\) | \(7/32\) |
| \(a,b,c\) | 8 | 0 | 0 | 0 | 0 |

For example,

\[
V_a=1-\frac{21^2+7^2+3^2+1^2}{32^2}
=1-\frac{125}{256}=\frac{131}{256}.
\]

### The entire repair tradeoff

An encoder that can inspect the initial state may send an additional message. The optimal success probabilities for alphabets of sizes 1 through 4 are the successive sums of the largest probabilities above:

| Message alphabet size | Fixed-width bits sufficient to encode it | Best success | Best error |
|---:|---:|---:|---:|
| 1 | 0 | \(21/32\) = 65.625% | \(11/32\) |
| 2 | 1 | \(28/32\) = 87.5% | \(1/8\) |
| 3 | 2 | \(31/32\) = 96.875% | \(1/32\) |
| 4 | 2 | 1 = 100% | 0 |

One optimal one-bit message is simply \(b\). The decoder then predicts \(c=0\). The three-symbol row is an alphabet-budget statement, not a claim that three symbols use fewer than two fixed-width bits. With the full two-bit budget, all four symbols are available and exact recovery is possible.

### Scalar projector identity

Choose the numerical target \(Z=4a+2b+c\). Then

\[
\mathbb E[Z\mid a]=4a+\tfrac58,
\qquad
\mathbb E[Z\mid a,b]=4a+2b+\tfrac18.
\]

Independence gives

\[
M_a=4\operatorname{Var}(b)+\operatorname{Var}(c)
=4\cdot\frac3{16}+\frac7{64}=\frac{55}{64},
\]

\[
M_{a,b}=\frac7{64},\qquad M_{a,b,c}=0.
\]

The first refinement removes exactly

\[
\mathbb E[(2b-\tfrac12)^2]=\frac34
=\frac{55}{64}-\frac7{64}
\]

of scalar residual energy. The categorical residual drops are instead \(75/256\) and \(7/32\), also checked by their vector projection identities.

**Interpretation.** The same fixed dynamics has increasingly adequate representations. Future measurements buy information through observation delay. A hypothetical state-aware message supplies it through communication. These are different acquisition mechanisms even when their resulting representations carry the same task information.

## Example 2. Recovering missing signal packets over a finite field

### The packet transform

Work over \(\mathbb F_5\), with a four-sample signal

\[
x=(x_0,x_1,x_2,x_3).
\]

Retain only two sum packets,

\[
s_0=x_0+x_1,\qquad s_1=x_2+x_3\pmod5.
\]

The observation matrix is

\[
R=\begin{bmatrix}1&1&0&0\\0&0&1&1\end{bmatrix}.
\]

The task is to recover the complete signal. Since \(\operatorname{rank}R=2\), its kernel has dimension 2. Every observation has \(5^2=25\) possible source signals.

For a uniform source on the 625 signals,

\[
K=25,\quad B=\lceil\log_2 25\rceil=5,
\]

\[
H=\log_2 25=4.643856\ldots,
\quad E=V=\frac{24}{25}=96\%.
\]

An observation of two sum packets has therefore discarded two field coordinates, but exact binary transmission of those coordinates requires five joint fixed-width bits. It does not require six unless the two five-symbol coordinates are separately encoded into three-bit fields.

### A minimal repair

Transmit the two difference packets

\[
d_0=x_0-x_1,\qquad d_1=x_2-x_3\pmod5.
\]

Because \(2^{-1}=3\pmod5\),

\[
x_0=3(s_0+d_0),\quad x_1=3(s_0-d_0),
\]

\[
x_2=3(s_1+d_1),\quad x_3=3(s_1-d_1)\pmod5.
\]

For the concrete signal \((4,1,3,2)\), the sums are \((0,0)\) and the differences are \((3,1)\). Substitution reconstructs \((4,1,3,2)\) exactly.

| Information retained | Rank | Remaining possibilities \(K\) | Extra bits still needed | Optimal uniform error |
|---|---:|---:|---:|---:|
| Sums only | 2 | 25 | 5 | \(24/25\) |
| Sums and \(d_0\) | 3 | 5 | 3 | \(4/5\) |
| Sums and both details | 4 | 1 | 0 | 0 |

The script checks the explicit inverse on **all 625 input signals**, not a selection of favorable cases.

### A deliberate failure: characteristic two

Over \(\mathbb F_2\), subtraction equals addition. The proposed detail packets repeat the sum packets and the combined matrix still has rank 2. In particular,

\[
(1,0,0,0)\quad\text{and}\quad(0,1,0,0)
\]

have identical sums **and** identical differences. The reconstruction fails because the repair supplied no new distinctions.

**Interpretation.** Missing packet dimension has an exact information cost, and a proposed repair can be verified by rank and obstruction witnesses. The coefficient field is part of the theorem's type. This is a finite-field packet example, not an audit of an existing real-valued polyphase implementation.

## Example 3. Arithmetic reconstruction and redundant local information

### Task and first realization

Let \(X\) be uniform on \(\{0,1,\ldots,59\}\), and observe

\[
r(x)=x\bmod12.
\]

The task is exact recovery of \(x\). For observation \(r\), the five possible states are

\[
r,\ r+12,\ r+24,\ r+36,\ r+48.
\]

Therefore

\[
K=5,\quad B=3,\quad H=\log_2 5,\quad E=V=\frac45.
\]

### A useful packet

Add \(c=x\bmod5\). Write \(x=r+12t\), where \(t\in\{0,1,2,3,4\}\). Reduction modulo 5 yields

\[
c\equiv r+2t\pmod5,
\qquad t\equiv3(c-r)\pmod5.
\]

Hence the explicit decoder is

\[
\boxed{x=r+12\bigl(3(c-r)\bmod5\bigr).}
\]

For \(x=47\), we observe \(r=11\), \(c=2\). The formula gives \(t=3\), then \(x=11+36=47\). The code checks this inverse on all 60 states.

### A redundant packet

Adding \(x\bmod6\) does not help: it is already a function of \(x\bmod12\). The joint observation still has five states per fiber.

| Available residues | \(K\) | Extra bits | Optimal uniform error |
|---|---:|---:|---:|
| Modulo 12 | 5 | 3 | \(4/5\) |
| Modulo 12 and modulo 6 | 5 | 3 | \(4/5\) |
| Modulo 12 and modulo 5 | 1 | 0 | 0 |

A different failure is incompatibility rather than missing information: the requirements \(x\equiv0\pmod4\) and \(x\equiv1\pmod6\) cannot both hold, since they require opposite parity. More information cannot turn those contradictory requirements into a solution.

**Interpretation.** A packet's value is measured by the distinctions it adds relative to the existing realization. Counting packets alone cannot distinguish useful, redundant, and incompatible data.

## Example 4. Information present only in a relationship

Let \(A,B\) be independent fair bits and let the task be

\[
F=A\oplus B.
\]

Given \(A\) alone, either value of \(F\) is equally likely. The same holds for \(B\) alone. Together, the bits determine the task.

| Observation | \(K\) | Conditional entropy | Optimal error | \(V\) | Task mutual information |
|---|---:|---:|---:|---:|---:|
| None | 2 | 1 bit | \(1/2\) | \(1/2\) | 0 bits |
| \(A\) | 2 | 1 bit | \(1/2\) | \(1/2\) | 0 bits |
| \(B\) | 2 | 1 bit | \(1/2\) | \(1/2\) | 0 bits |
| \((A,B)\) | 1 | 0 | 0 | 0 | 1 bit |

All four states are enumerated. The failure of an additive packet score is exact:

\[
I(F;A)+I(F;B)=0\ne1=I(F;A,B).
\]

The marginal task information supplied by \(B\) rises from zero to one bit when \(A\) is already available. Thus task information need not have diminishing marginal returns.

**Interpretation.** A packet can be useless by itself and essential in combination. A purely one-packet-at-a-time acquisition heuristic that refuses zero immediate gain can miss such combinations. This does not mean all joint information has one uniquely defined scalar “synergy” measure. It establishes the specific failure of additive and universal diminishing-return assumptions.

## Example 5. An exact noisy-channel experiment

### Channel model

Let \(F\) be a fair bit. Observe it through a flip channel with error \(1/10\):

\[
R=F\oplus N_1,\qquad P(N_1=1)=\tfrac1{10}.
\]

Then transmit \(R\) through an independent flip channel with error \(1/5\):

\[
S=R\oplus N_2,\qquad P(N_2=1)=\tfrac15.
\]

The final bit differs from \(F\) when exactly one flip occurs:

\[
p=P(S\ne F)
=\tfrac1{10}\tfrac45+\tfrac9{10}\tfrac15
=\tfrac{13}{50}=0.26.
\]

The optimal decoder outputs the observed bit for both channels, because their crossover probabilities are below \(1/2\).

| Observation | Optimal error | Conditional entropy | Scalar MSE for \(F\in\{0,1\}\) | Categorical residual \(V\) |
|---|---:|---:|---:|---:|
| \(R\) | \(1/10\) | 0.468996 bits | \(9/100\) | \(9/50\) |
| \(S\) | \(13/50\) | 0.826746 bits | \(481/2500\) | \(481/1250\) |

### Checking the stochastic projector identity by hand

The conditional means are

\[
P_RF=0.1+0.8R,\qquad P_SF=0.26+0.48S.
\]

When \(R=S\), their difference has magnitude \(0.16\). When \(R\ne S\), it has magnitude \(0.64\). Therefore

\[
\mathbb E[(P_RF-P_SF)^2]
=\tfrac45(0.16)^2+\tfrac15(0.64)^2
=\frac{64}{625}=0.1024.
\]

Direct subtraction gives the same value:

\[
\frac{481}{2500}-\frac9{100}=\frac{64}{625}.
\]

The corresponding categorical residual increment is twice as large,

\[
\frac{481}{1250}-\frac9{50}=\frac{128}{625}=0.2048,
\]

because the unhalved binary one-hot loss sums the squared error in both complementary class probabilities.

### Why the assumption matters

The proof uses the Markov condition \(F\to R\to S\). The original target cannot affect \(S\) through an unmodeled additional route once \(R\) is known. Without that condition, comparing two arbitrary observations does not obey this loss identity.

The broader channel suite checks **all 3,125 binary Markov models** whose prior and four conditional-probability parameters lie in \(\{0,1/4,1/2,3/4,1\}\). Of these, 2,882 have zero-weight joint states. Entropy inequalities, errors, and projector residual identities are checked exactly.

**Interpretation.** The information layer is not restricted to noiseless deterministic maps. This is a finite stochastic extension with explicit conditional-independence assumptions, not a completed general measure-theoretic or quantum theory.

## Example 6. The encoder-access boundary

### Ten states around a five-cycle

There are five possible observations, numbered \(0,\ldots,4\). Observation \(i\) says the target is one of

\[
\{i,i+1\pmod5\}.
\]

Thus the structural states are the ten edge-endpoint pairs

\[
X=\{(i,i),(i,i+1\pmod5):i=0,\ldots,4\},
\]

with uniform probability. The decoder knows the edge \(i\) and must recover its endpoint. Every observation fiber contains exactly two targets, so \(K=2\).

### Encoder A sees the state

It knows the edge and the endpoint. Send 0 for the edge's first endpoint and 1 for its second endpoint. The decoder recovers the target exactly. Two symbols, or one bit, suffice.

### Encoder B sees only the target

Its message must be \(c=h(F)\), with one fixed message assigned to each target value, independent of the edge. Adjacent vertices must receive different messages.

Two messages would require alternating labels around an odd cycle, which is impossible. Three messages suffice, for example with target-label assignment

\[
(h(0),h(1),h(2),h(3),h(4))=(0,1,0,1,2).
\]

Therefore

\[
\boxed{K=2,\quad\text{minimum state-aware alphabet}=2,
\quad\text{minimum target-only alphabet}=3.}
\]

### Exhaustive coding check

The script enumerates every target-only encoder for message alphabets 1, 2, and 3:

| Alphabet | Encoders examined | Exact encoders | Best target-only success | Best state-aware success |
|---:|---:|---:|---:|---:|
| 1 | \(1^5=1\) | 0 | \(1/2\) | \(1/2\) |
| 2 | \(2^5=32\) | 0 | \(9/10\) | 1 |
| 3 | \(3^5=243\) | 30 | 1 | 1 |

The \(9/10\) upper bound is also transparent: every two-coloring has at least one monochromatic edge, and at that edge at least one of the two equally weighted states must be decoded incorrectly. The displayed alternating pattern with its final edge collision attains exactly one error among ten states.

**Interpretation.** The original minimum-repair theorem remains correct under its stated state-aware access assumption. What fails is extending it to a restricted encoder without changing the mathematical problem. A mature calculus should include who can see which variables as part of the realization's type. Confusability graphs are the established exact language for this boundary.

## Example 7. Locally satisfiable information that cannot be assembled globally

Require three bits to satisfy

\[
x_1\oplus x_2=0,\qquad
x_2\oplus x_3=0,\qquad
x_3\oplus x_1=1.
\]

Each individual relation is satisfiable. Any two of the three equations are jointly satisfiable, with exactly two assignments. Their allowed values on a shared individual variable are both \(\{0,1\}\).

But XORing all three equations cancels each variable twice and gives

\[
0=1.
\]

No global assignment exists. The script enumerates all eight assignments and verifies the pairwise counts \((2,2,2)\) and global count 0.

**Interpretation.** This is an inconsistency obstruction, not a shortage of bits. Adding a new observation cannot resolve a contradiction while leaving every contradictory requirement intact. At least one requirement or modeling assumption must change. The information calculus must distinguish refinement problems from compatibility problems.

## What these examples establish

The examples demonstrate exact reconstruction costs, optimal success curves, numerical loss identities, redundancy, nonadditivity, encoder-access constraints, and assembly failures. The shared language is productive because it states which distinctions are missing, what a permitted repair can do, and what measurable result follows.

The examples do not establish universal applicability, historical novelty, or an unrestricted equivalence among signal processing, arithmetic, and learning. They are controlled finite instances, with general proofs of their common mechanisms in `THEORY.md` and bounded executable evidence in `reports/`.
