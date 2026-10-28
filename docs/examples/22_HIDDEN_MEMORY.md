# 22. Recover the memory hidden by a summary

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: memory kernel](../GLOSSARY.md#memory-kernel) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Sufficient Resolution studies what happens when visible coordinates omit a
hidden state. Machine Societies asks when a summary has its own transition
rule. We can see both questions in a two-coordinate linear system over the
rational numbers.

## Run the full state

Let $y_n$ be visible and $z_n$ hidden. Use

```math
\begin{pmatrix}y_{n+1}\\z_{n+1}\end{pmatrix}
=T\begin{pmatrix}y_n\\z_n\end{pmatrix},\qquad
T=\begin{pmatrix}1&1\\1&0\end{pmatrix}.
```

Thus $y_{n+1}=y_n+z_n$ and $z_{n+1}=y_n$. Start from $(y_0,z_0)=(1,0)$.

| Time $n$ | Visible $y_n$ | Hidden $z_n$ | Next visible calculation |
|---|---|---|---|
| 0 | 1 | 0 | $1+0=1$ |
| 1 | 1 | 1 | $1+1=2$ |
| 2 | 2 | 1 | $2+1=3$ |
| 3 | 3 | 2 | $3+2=5$ |
| 4 | 5 | 3 | $5+3=8$ |

The same visible value $1$ occurs at times zero and one, with different next
values. A deterministic rule receiving only the current $y_n$ cannot give
both answers. Equivalently, the full states $(1,0)$ and $(1,1)$ have the same
summary but different next summaries.

## Locate the first return from hidden state

Write the blocks of $T$ as $A=B=G=1$ and $D=0$. Here $G$ sends visible state
into the hidden coordinate, and $B$ sends hidden state back. The memory maps are

```math
M_k=BD^kG,\qquad M_0=1,\qquad M_k=0\quad(k\ge1).
```

The zeroth power $D^0$ is the identity, even though $D=0$.
Information entering the hidden coordinate at the first step returns to the
visible coordinate at the second step.

Let $Ry=(y,0)$ initialize the hidden coordinate to zero, and let $C(y,z)=y$.
The prepared visible maps $E_n=CT^nR$ are scalar multipliers:

```math
E_0=1,\qquad E_1=1,\qquad E_2=2,\qquad E_3=3.
```

In particular, $E_2\ne E_1E_1$. Restarting from the visible value and silently
resetting the hidden coordinate changes the experiment.

## Keep just enough history

For every $n\ge1$, the full recurrence gives $z_n=y_{n-1}$. Substitution yields

```math
y_{n+1}=y_n+y_{n-1}.
```

The pair $(y_n,y_{n-1})$ is therefore enough state from time one onward.
Its update is $(u,v)\mapsto(u+v,u)$. We have replaced the hidden coordinate
with a retained previous value. This is an exact statement for the declared
system and initialization.

## Try it

Replace $G=1$ by $G=0$, keeping $A=B=1$ and $D=0$. Does visible evolution
close when the hidden state is initialized to zero? Does it close for every
initial hidden state?

**Answer:** From $(y_0,0)$, the hidden coordinate stays zero and the visible
value stays $y_0$. All prepared memory maps vanish. But $(1,0)$ and $(1,1)$
still produce different first visible outputs, $1$ and $2$. A conclusion for
prepared states does not automatically hold for arbitrary hidden initialization.

These calculations illustrate exact state sufficiency. The wider monographs
state their own hypotheses for controlled, stochastic and approximate models.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Visible state](../GLOSSARY.md#visible-state) · [Hidden state](../GLOSSARY.md#hidden-state) · [Prepared hidden initialization](../GLOSSARY.md#prepared-state) · [Discrete memory maps](../GLOSSARY.md#memory-kernel) · [Autonomous dynamics of a summary](../GLOSSARY.md#autonomous-dynamics) · [State augmentation](../GLOSSARY.md#state-augmentation) · [Semigroup law for evolution maps](../GLOSSARY.md#semigroup-law)

This two-coordinate model illustrates prepared evolution and hidden-memory return in Sufficient Resolution, and the deterministic quotient criterion in Machine Societies. The works’ broader assumptions and review records remain separate.

### Sufficient Resolution

[Read](../works/sufficient-resolution.md#read) · [Written proofs](../works/sufficient-resolution.md#written-proofs) · [Lean coverage](../works/sufficient-resolution.md#lean) · [Code and setup](../works/sufficient-resolution.md#code) · [Evidence](../works/sufficient-resolution.md#evidence)

### Machine Societies

[Read](../works/monographs-machine-societies.md#read) · [Written proofs](../works/monographs-machine-societies.md#written-proofs) · [Lean coverage](../works/monographs-machine-societies.md#lean) · [Code and setup](../works/monographs-machine-societies.md#code) · [Evidence](../works/monographs-machine-societies.md#evidence)

**Source passages:**

- [Sufficient Resolution: exact hidden elimination and closure](../../monographs/sufficient-resolution/traditional/Sufficient_Resolution_Traditional.tex#L300)
- [Machine Societies: deterministic quotient criterion](../../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex#L293)


[Edition guide and reproduction instructions](../../monographs/sufficient-resolution/README.md). Use each work’s Code and setup link for its implementation. The arithmetic check below covers this tutorial separately.

[Python arithmetic check for this example: hidden_memory()](../../tools/check_hand_examples.py#L423). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Choose a certificate with shared premises](21_PROOF_CERTIFICATES.md)
- [Next: Find the reusable part of a calibration](23_CALIBRATED_CONTINUATION.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#hidden-memory)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
