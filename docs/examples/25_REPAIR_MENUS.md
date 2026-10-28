# 25. Choose repair directions from a finite menu

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: repair menu](../GLOSSARY.md#repair-menu) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Constructive Repair asks how to make a target reachable while keeping the
original equations and admissible choices fixed. Work in $\mathbb Q^3$.
The original image is the span of $d=(1,0,0)^{\mathsf T}$, and the required
target is $r=(0,1,0)^{\mathsf T}$.

## Identify the missing direction

No multiple of $d$ equals $r$. Modulo the original image, the residual class
of $r$ is nonzero. If we may freely choose a rational added direction, one
direction suffices: add $r$ itself. Zero added directions do not suffice, so
the minimum free repair dimension is one.

## Respect a supplied menu

Now restrict the available added directions:

| Choice | Direction | Selection cost |
|---|---|---|
| 1 | $e_1=(0,1,1)^{\mathsf T}$ | 1 |
| 2 | $e_2=(0,0,1)^{\mathsf T}$ | 1 |
| 3 | $e_3=(0,1,0)^{\mathsf T}$ | 3 |

The symbols $e_i$ label menu choices here, rather than the standard basis.
A cost is paid once for each selected direction. Rational coefficients may
have either sign. We seek

```math
xd+\sum_{i\text{ selected}}a_i e_i=r.
```

## Check feasible choices and their costs

Choice 1 alone would require both $a_1=1$ from the second coordinate and
$a_1=0$ from the third. Choice 2 alone cannot change the second coordinate.
Together they work:

```math
0d+1e_1-1e_2=(0,1,0)^{\mathsf T}=r.
```

The total cost is two. Choice 3 alone also works, at cost three. The empty
selection and the two cost-one selections fail, so two is the minimum menu
cost. The freely chosen repair dimension and the cheapest menu selection
answer different questions.

## Reject a wrong certificate without rejecting the problem

The proposed coefficients $a_1=a_2=1$ give $(0,1,2)^{\mathsf T}$, so that
proposal fails the original target equation. The coefficients $(1,-1)$ above
provide a valid repair using the same two directions.

If the allowed menu instead contains only choice 2, the row vector
$\lambda=(0,1,0)$ gives a direct obstruction:

```math
\lambda d=0,\qquad \lambda e_2=0,\qquad \lambda r=1.
```

Every allowed combination has zero image under $\lambda$, while the target
does not. This proves infeasibility for that restricted menu. Adding choice 1
changes the admissible problem and removes this obstruction.

## Try it

Lower the cost of choice 3 from three to one. What is the new optimum? Does
the earlier identity $e_1-e_2=r$ stop being valid?

**Answer:** Choice 3 alone gives the new minimum cost one. The earlier repair
remains valid but is no longer cheapest.

This is exact rational linear repair with a finite, unconstrained selection
menu. Integer coefficients, nonlinear constraints and other admissibility rules
require their own problem statements. The linked package distinguishes Python
certificate validity from acceptance of an emitted Lean certificate.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Repair direction](../GLOSSARY.md#repair-direction) · [Free linear repair](../GLOSSARY.md#free-repair) · [Finite repair menu](../GLOSSARY.md#repair-menu) · [Repair selection cost](../GLOSSARY.md#repair-cost) · [Feasibility](../GLOSSARY.md#feasibility) · [Linear obstruction witness](../GLOSSARY.md#dual-witness)

The example uses rational linear repair with supplied menu costs. It distinguishes feasibility, optimal selection and rejection of a proposed certificate. Python checks and Lean acceptance retain their separate recorded meanings.

### Constructive Repair

[Read](../works/constructive-repair.md#read) · [Written proofs](../works/constructive-repair.md#written-proofs) · [Lean coverage](../works/constructive-repair.md#lean) · [Code and setup](../works/constructive-repair.md#code) · [Evidence](../works/constructive-repair.md#evidence)

**Source passages:**

- [Constructive Repair: the original menu example](../../packages/constructive-repair/README.md#L24)
- [Constructive Repair: mathematical scope](../../packages/constructive-repair/README.md#L56)


[Edition guide and reproduction instructions](../components/CONSTRUCTIVE_REPAIR.md). Use each work’s Code and setup link for its implementation. The arithmetic check below covers this tutorial separately.

[Python arithmetic check for this example: repair_menus()](../../tools/check_hand_examples.py#L488). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Calculate coefficients of contracted feedback](24_CONTRACTED_FEEDBACK.md)
- [Next: Update a Gaussian model from one observation](26_GAUSSIAN_UPDATE.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#repair-menus)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
