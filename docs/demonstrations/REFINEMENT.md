# Refine a signal and account for a missing packet

[All demonstrations](../DEMONSTRATIONS.md) · [Project map](../PROJECT_MAP.md#foundations) · [Glossary: refinement](../GLOSSARY.md#refinement)

[Run and edit this example in your browser](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#refinement)

[Explore the interactive diagram](https://KomorebiP.github.io/Operation-KOMOREBI/interactive.html#refinement)
to reshape the signal, refine its address packets, and inspect what is lost when a packet is discarded.

**Question:** What changes when a signal is described by finer address classes?
This example uses list indexing and integer arithmetic.

## 1. Keep the original addresses

Take $x=(1,2,3,4,5,6,7,8)$, indexed from zero. Separating addresses by
their remainder modulo two gives the compact lists

```math
x^{(2)}_0=(1,3,5,7),\qquad x^{(2)}_1=(2,4,6,8).
```

These lists retain all eight entries. Interleaving them recovers the original
signal. [Example 5](../examples/05_REFINEMENT.md) also expresses each list as
a projector acting in the original eight-dimensional space.

## 2. Refine from two classes to four

| Remainder modulo four | Original addresses | Values |
|---|---|---|
| 0 | 0, 4 | $(1,5)$ |
| 1 | 1, 5 | $(2,6)$ |
| 2 | 2, 6 | $(3,7)$ |
| 3 | 3, 7 | $(4,8)$ |

Let $P_0,P_1$ be the even and odd selectors, and let $F_r$ select remainder
$r$ modulo four, all acting on the original eight coordinates. Then

```math
P_0=F_0+F_2,\qquad P_1=F_1+F_3.
```

Each coarse packet is exactly the sum of its fine children. To reconstruct
from the compact lists, put their entries back at the recorded addresses.
Python's `fine[i % 4][i // 4]` implements this for address `i` in this example.

## 3. Discard one class as a control

Dropping remainder 2 produces

```math
\widehat x=(1,2,0,4,5,6,0,8),\qquad
r=x-\widehat x=(0,0,3,0,0,0,7,0).
```

The residual is original minus reconstructed. Its squared Euclidean norm is
$3^2+7^2=58$. Refinement with every packet retained is an exact coordinate
description. Deleting a packet is an additional operation with a measurable
loss in this example.

## 4. Run the calculation

Follow the [download or checkout instructions](../DEMONSTRATIONS.md#run-without-installing-a-library).
From the collection root, run:

```text
python -B examples/komorebi_demonstrations.py refinement
```

Expected output:

<!-- expected-output -->
```text
Input: (1, 2, 3, 4, 5, 6, 7, 8)
Two packets: ((1, 3, 5, 7), (2, 4, 6, 8))
Four packets: ((1, 5), (2, 6), (3, 7), (4, 8))
Interleaved: (1, 2, 3, 4, 5, 6, 7, 8)
Without remainder 2: (1, 2, 0, 4, 5, 6, 0, 8)
Residual: (0, 0, 3, 0, 0, 0, 7, 0)
Squared residual norm: 58
PASS: refinement
```

The checks compare fine children with both coarse packets, reconstruct the
list and test the discarded-packet residual. There is no convolution, padding,
boundary extension or approximation in this run.

## 5. Follow the result and its evidence

| Continue to | Route and scope |
|---|---|
| Paper | [Paper II's readable chapters](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-ii/index.html). |
| Exact claim | [Nested residue refinement](https://KomorebiP.github.io/Operation-KOMOREBI/claims.html#paper-ii-thm-residue_refinement). |
| Written proof | [Readable statement](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-ii/refinement-and-residue-coordinates.html#L476) and [proof](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-ii/refinement-and-residue-coordinates.html#L486). |
| Lean | [Paper II's recorded coverage and setup](../works/paper-ii.md#lean). Individual claim mappings are not transcribed in this claim index. Consult the formal guide for the exact scope. |
| Program | [Read or download the complete program](https://KomorebiP.github.io/Operation-KOMOREBI/read/demonstrations.html). |
| Signal applications | [Paper V](../works/paper-v.md) and the library's [signal realization guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization). |
| More hand calculations | [Residue refinement](../examples/05_REFINEMENT.md) and [Haar averages and differences](../examples/14_HAAR_PAIRS.md). |

This is a finite address decomposition. It does not establish stability or
accuracy for a filter bank, an infinite signal or a numerical implementation.

[Previous: Reconstruct an operator](PACKETS.md) · [Next: Test recovery](RECOVERY.md) · [All demonstrations](../DEMONSTRATIONS.md)
