# 21. Choose a certificate with shared premises

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: minimum-cost certificate](../GLOSSARY.md#minimum-cost-certificate) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Proof Path Theory distinguishes a valid certificate, an inclusion-minimal
certificate and a cheapest certificate. This small recorded rule system shows
why those distinctions matter.

## Declare the leaves and rules

There are four obligations, $a,b,c,d$. The final rule requires all four:

```math
\{a,b,c,d\}\Longrightarrow t.
```

Choose from four admissible leaves. Each selected leaf costs one unit and can
be used more than once. Obligation nodes, the target and all rules cost zero.
There are no mandatory starting leaves.

| Leaf | Certified consequences | Cost |
|---|---|---|
| $s_1$ | $a$ and $b$ | 1 |
| $s_2$ | $b$ and $c$ | 1 |
| $s_3$ | $c$ and $d$ | 1 |
| $s_4$ | $a$ and $d$ | 1 |

For example, the first row represents two separate rules
$\{s_1\}\Longrightarrow a$ and $\{s_1\}\Longrightarrow b$.
The table declares the available certified rules for this exercise. It does
not assert that arbitrary implications are mathematically valid.

## Build and check one certificate

Select the node set $K=\{s_1,s_3,a,b,c,d,t\}$. Retain the five rules

```math
s_1\Longrightarrow a,\quad s_1\Longrightarrow b,\quad
s_3\Longrightarrow c,\quad s_3\Longrightarrow d,\quad
\{a,b,c,d\}\Longrightarrow t.
```

A forward check proceeds as follows:

1. Admit the selected leaves $s_1,s_3$.
2. Apply the first four rules to obtain $a,b,c,d$.
3. Apply the final rule to obtain $t$.

The selected nodes and rules form a certificate. Its cost is $1+1=2$.
The use of $s_1$ twice does not charge for that leaf twice.

## Establish the minimum and its limits

One leaf supplies only two of the four obligations. No certificate of cost
zero or one can reach $t$. The displayed cost-two certificate is therefore
optimal in this finite rule system.

There is another optimum: select $s_2,s_4$. The other four pairs all miss an
obligation:

| Selected leaves | Missing obligation |
|---|---|
| $s_1,s_2$ | $d$ |
| $s_1,s_4$ | $c$ |
| $s_2,s_3$ | $a$ |
| $s_3,s_4$ | $b$ |

Each optimum is inclusion-minimal. Removing one of its selected leaves or
used rules breaks the derivation. There is no least certificate contained in
both optima: their common nodes include no admissible leaf, so they cannot
start a derivation. A minimum cost therefore need not identify a unique
certificate or a least certificate under inclusion.

## Recognize a failed proposal

A record selecting only $s_1$ reaches $a,b$ but cannot fire the final rule.
Its rejection concerns that record. We have already exhibited valid records
for the same target. Exhausting a search budget would also leave the search
unresolved, rather than establish that no certificate exists.

## Try it

Add a leaf $s_5$ with four rules supplying $a,b,c,d$. What happens if its
cost is three? What if its cost is one?

**Answer:** At cost three, the original cost-two pairs remain optimal. At
cost one, selecting $s_5$ gives the new minimum. The permitted rules and costs
determine the optimization problem.

This example checks one supplied finite proof field. It does not establish
that a selected certificate is the shortest possible proof in every system.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Finite proof field](../GLOSSARY.md#proof-field) · [Admissible leaf](../GLOSSARY.md#admissible-leaf) · [Recorded inference rule](../GLOSSARY.md#inference-rule) · [Verification closure](../GLOSSARY.md#verification-closure) · [Inclusion-minimal certificate](../GLOSSARY.md#inclusion-minimal) · [Least certificate](../GLOSSARY.md#least-certificate) · [Minimum-cost certificate](../GLOSSARY.md#minimum-cost-certificate)

This example compares certificates in a supplied finite rule system. It illustrates verification closure and cost selection in Proof Path Theory. It does not certify arbitrary inference rules or Python implementations.

### Proof Path Theory

[Read](../works/proof-path-theory.md#read) · [Written proofs](../works/proof-path-theory.md#written-proofs) · [Lean coverage](../works/proof-path-theory.md#lean) · [Code and setup](../works/proof-path-theory.md#code) · [Evidence](../works/proof-path-theory.md#evidence)

**Source passages:**

- [Proof Path Theory: certificates and verification closure](../../monographs/proof-path-theory/docs/Proof_Path_Theory.tex#L408)
- [Proof Path Theory: alternative derivations and costs](../../monographs/proof-path-theory/docs/Proof_Path_Theory.tex#L479)


[Edition guide and reproduction instructions](../../monographs/proof-path-theory/README.md). Use each work’s Code and setup link for its implementation. The arithmetic check below covers this tutorial separately.

[Python arithmetic check for this example: proof_certificates()](../../tools/check_hand_examples.py#L396). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Separate support from multiplicity](20_SUPPORT_AND_MULTIPLICITY.md)
- [Next: Recover the memory hidden by a summary](22_HIDDEN_MEMORY.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#proof-certificates)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
