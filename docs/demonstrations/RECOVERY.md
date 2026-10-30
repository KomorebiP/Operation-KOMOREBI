# Test whether a summary can answer a question

[All demonstrations](../DEMONSTRATIONS.md) · [Project map](../PROJECT_MAP.md#limits-and-repair) · [Glossary: obstruction](../GLOSSARY.md#obstruction)

[Run and edit this example in your browser](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#recovery)

[Explore the interactive diagram](https://KomorebiP.github.io/Operation-KOMOREBI/interactive.html#recovery)
to move inputs with the same summary and change the question you want to recover.

**Question:** If a summary keeps only the sum of two coordinates, can it recover
the first coordinate? This example needs only addition and the idea of a function.

## 1. Specify the summary and the requested answer

Work over the real numbers. Let

```math
R(x_1,x_2)=x_1+x_2,\qquad F(x_1,x_2)=x_1.
```

Exact recovery for every input would require a function $G$ with $F=G\circ R$.
The [factorization glossary entry](../GLOSSARY.md#factorization) explains this
notation. [Example 7](../examples/07_OBSTRUCTIONS.md) develops the calculation.

## 2. Find a witness that recovery is impossible

Take $u=(1,0)$ and $v=(0,1)$. Their summaries agree, but their requested
answers differ:

```math
R(u)=R(v)=1,\qquad F(u)=1,\qquad F(v)=0.
```

Any recovery function would need both $G(1)=1$ and $G(1)=0$.
This contradiction rules out every function of the sum alone, including
nonlinear ones. The computation displays the witness. The contradiction
explains why the witness settles this recovery question.

For the linear maps above, the difference $w=u-v=(1,-1)$ gives the same
issue in kernel notation:

```math
Rw=0,\qquad Fw=1.
```

The summary erases a direction that still changes the desired answer.

## 3. Check a question the summary can answer

Ask instead for $H(x_1,x_2)=2x_1+2x_2$. Then $G_H(s)=2s$ works because
$G_H(R(x))=2(x_1+x_2)=H(x)$ for every input. The program checks the exact
coefficient identity $[2][1\ \ 1]=[2\ \ 2]$.

The same summary can therefore be sufficient for one observation and
insufficient for another. This example concerns exact recovery for all inputs.
It does not measure prediction accuracy for a specified probability distribution.

## 4. Run the calculation

Follow the [download or checkout instructions](../DEMONSTRATIONS.md#run-without-installing-a-library).
From the collection root, run:

```text
python -B examples/komorebi_demonstrations.py recovery
```

Expected output:

<!-- expected-output -->
```text
Inputs: (1, 0) and (0, 1)
Same summary: 1
Requested first coordinates: (1, 0)
Kernel witness: (1, -1)
R(w): 0
F(w): 1
Compatible observation coefficients: (2, 2)
PASS: recovery
```

## 5. Follow the argument and the wider subject

| Continue to | Route and scope |
|---|---|
| Written argument | [The collision argument](../examples/07_OBSTRUCTIONS.md#find-a-collision) and the library's [factorization criterion](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion). |
| Papers and books | [Realization Boundaries](../works/realization-boundaries.md#read) and [Paper III](../works/paper-iii.md#read) develop related questions about compatibility and obstructions. |
| A further claim | [Paper III's nonlinear refinement defect](https://KomorebiP.github.io/Operation-KOMOREBI/claims.html#paper-iii-def-nonlinear_defect) and [defect under composition](https://KomorebiP.github.io/Operation-KOMOREBI/claims.html#paper-iii-thm-defect_composition_identity) introduce a different, explicitly defined setting. |
| Written proof of that further claim | [Readable composition theorem and proof](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-iii/nonlinear-coordinates.html#L748). Keep its hypotheses when moving beyond this example. |
| Lean | [Paper III coverage](../works/paper-iii.md#lean) and [Realization Boundaries coverage](../works/realization-boundaries.md#lean). No theorem-to-Lean correspondence is asserted for this standalone demonstration. |
| Program | [Read or download the complete program](https://KomorebiP.github.io/Operation-KOMOREBI/read/demonstrations.html), then explore the [library code and instructions](../works/realization-boundaries.md#code). |
| More hand calculations | [Kernels and fibers](../examples/10_KERNELS.md), [hidden memory](../examples/22_HIDDEN_MEMORY.md) and [repair directions](../examples/25_REPAIR_MENUS.md). |

[Previous: Refine a signal](REFINEMENT.md) · [All demonstrations](../DEMONSTRATIONS.md) · [Project overview](../START_HERE.md)
