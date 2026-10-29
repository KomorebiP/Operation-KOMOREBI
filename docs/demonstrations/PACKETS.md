# Reconstruct an operator from its packet blocks

[All demonstrations](../DEMONSTRATIONS.md) · [Project map](../PROJECT_MAP.md#foundations) · [Glossary: transfer block](../GLOSSARY.md#transfer-block)

**Question:** Can we reproduce a matrix operation by calculating its action
between smaller pieces? You need only multiplication of two by two matrices.

## 1. Choose the object and its parts

Work over the real numbers. Take the column vector and coordinate projectors

```math
x=\begin{pmatrix}2\\3\end{pmatrix},\qquad
P_1=\begin{pmatrix}1&0\\0&0\end{pmatrix},\qquad
P_2=\begin{pmatrix}0&0\\0&1\end{pmatrix}.
```

The parts are $P_1x=(2,0)^{\mathsf T}$ and $P_2x=(0,3)^{\mathsf T}$.
They add to $x$. Each projector is idempotent, their cross products vanish,
and their sum is the identity. [Example 1](../examples/01_PACKETS.md) checks
each of these identities and also gives an oblique decomposition.

## 2. Calculate the operation by two routes

Let

```math
T=\begin{pmatrix}1&2\\3&4\end{pmatrix},\qquad
Tx=\begin{pmatrix}1\cdot2+2\cdot3\\3\cdot2+4\cdot3\end{pmatrix}
=\begin{pmatrix}8\\18\end{pmatrix}.
```

The block $P_jTP_i$ takes input from packet $i$ and places its output in
packet $j$. Rows label targets and columns label sources.

| Target $j$, source $i$ | Contribution $P_jTP_i x$ |
|---|---|
| 1, 1 | $(2,0)^{\mathsf T}$ |
| 1, 2 | $(6,0)^{\mathsf T}$ |
| 2, 1 | $(0,6)^{\mathsf T}$ |
| 2, 2 | $(0,12)^{\mathsf T}$ |

Adding the four contributions gives $(8,18)^{\mathsf T}$ again. The reason
extends to every vector in this space:

```math
\sum_{j=1}^2\sum_{i=1}^2P_jTP_i
=(P_1+P_2)T(P_1+P_2)=ITI=T.
```

[Example 4](../examples/04_TRANSFER.md) writes out the four block matrices
and continues to composition of operations.

## 3. Remove a block as a control

Omit $P_2TP_2$. The output becomes $(8,6)^{\mathsf T}$, with missing
contribution $(0,12)^{\mathsf T}$. An incomplete block calculation cannot
claim the reconstruction identity above.

## 4. Run the calculation

Follow the [download or checkout instructions](../DEMONSTRATIONS.md#run-without-installing-a-library).
From the collection root, run:

```text
python -B examples/komorebi_demonstrations.py packets
```

Expected output:

<!-- expected-output -->
```text
Input: (2, 3)
Packet parts: ((2, 0), (0, 3))
Block contributions: ((2, 0), (6, 0), (0, 6), (0, 12))
Direct result: (8, 18)
Reconstructed result: (8, 18)
Without the final block: (8, 6)
PASS: packets
```

The program checks the matrix identities themselves as well as this vector's
output. Its calculations use integers exactly.

## 5. Follow the result and its evidence

| Continue to | Route and scope |
|---|---|
| Paper | [Paper I](../works/paper-i.md#read), for packet families and operator reconstruction. |
| Exact claim | [Exact operator reconstruction](https://KomorebiP.github.io/Operation-KOMOREBI/claims.html#psc-i-t-operator-reconstruction). This record links the written statement, proof and transcribed Lean declarations. |
| Written proof | [Paper I, proof beginning at line 512](../../papers/paper-i/current/editable/traditional/03_packets_and_graphs.tex#L512). |
| Lean | [Recorded coverage and setup](../works/paper-i.md#lean). The claim record names the existing correspondence. This demonstration adds no Lean verification. |
| Program | [Read or download the complete program](https://KomorebiP.github.io/Operation-KOMOREBI/read/demonstrations.html). |
| Library use | [First packet program](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) and [installation](../FIRST_RUN.md). |
| More hand calculations | [Packets](../examples/01_PACKETS.md), [transfer blocks](../examples/04_TRANSFER.md), [coordinate changes](../examples/03_COORDINATES.md). |

This illustrates a finite algebraic reconstruction. Infinite sums, convergence,
conditioning and application-specific models require their stated hypotheses.

[Next: Refine a signal](REFINEMENT.md) · [All demonstrations](../DEMONSTRATIONS.md) · [Project overview](../START_HERE.md)
