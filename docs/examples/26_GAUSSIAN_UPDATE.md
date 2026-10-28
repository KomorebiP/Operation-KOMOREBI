# 26. Update a Gaussian model from one observation

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: posterior](../GLOSSARY.md#posterior) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

Certified Inference and its Bayesian research companion separate the exact
posterior from an approximation built using a candidate gain. Here is a
two-coordinate example with exact rational mean and covariance calculations.

## Declare the model

Let the prior state be $X\sim\mathcal N(0,I_2)$. Observe

```math
Y=HX+V,\qquad H=\begin{pmatrix}1&1\end{pmatrix},\qquad
V\sim\mathcal N(0,1),
```

where $V$ is independent of $X$. Take the observed value to be $y=3$.
The model describes a noisy sum of the two state coordinates. In the package's
factor convention, $L=I_2$, a zero noise factor and $\sigma=1$ give the
declared prior covariance $P=I_2$ and noise covariance $R=1$.

## Calculate the gain and posterior mean

The innovation is $d=y-Hm=3$, where the prior mean $m$ is zero. The innovation
variance and exact gain are

```math
S=HPH^{\mathsf T}+R=2+1=3,\qquad
K=PH^{\mathsf T}S^{-1}=\begin{pmatrix}1/3\\1/3\end{pmatrix}.
```

Thus the posterior mean is $m+Kd=(1,1)^{\mathsf T}$. The noise means that the
posterior mean of the sum, two, need not equal the observed value, three.

## Calculate and check the covariance

For the exact gain,

```math
C_*=P-KHP
=\begin{pmatrix}2/3&-1/3\\-1/3&2/3\end{pmatrix}.
```

The normalized sum direction $(1,1)^{\mathsf T}/\sqrt2$ has posterior variance
$1/3$. The normalized difference direction $(1,-1)^{\mathsf T}/\sqrt2$ still
has variance one. This observation informs the sum and leaves the independent
difference unchanged.

We can check the posterior directly by completing the square in its density.
The prior times the likelihood is proportional to

```math
\exp\!\left[-\frac12\bigl(x_1^2+x_2^2+(3-x_1-x_2)^2\bigr)\right].
```

Write $\mu=(1,1)^{\mathsf T}$ and set

```math
J=\begin{pmatrix}2&1\\1&2\end{pmatrix}.
```

The expression inside parentheses is

```math
(x-\mu)^{\mathsf T}J(x-\mu)+3.
```

The constant affects normalization. The precision matrix is $J$, and direct
multiplication gives $JC_*=I_2$, confirming the same covariance.

## Keep a candidate gain's covariance valid

For a general gain $B$, use the Joseph covariance

```math
C_B=(I_2-BH)P(I_2-BH)^{\mathsf T}+BRB^{\mathsf T}.
```

Choose $B=(1/4,1/4)^{\mathsf T}$. Its mean is $(3/4,3/4)^{\mathsf T}$, and

```math
I_2-BH=\begin{pmatrix}3/4&-1/4\\-1/4&3/4\end{pmatrix},\qquad
C_B=\begin{pmatrix}11/16&-5/16\\-5/16&11/16\end{pmatrix}.
```

The residual $PH^{\mathsf T}-BS=(1/4,1/4)^{\mathsf T}$ is nonzero. This
candidate defines a Gaussian approximation, with a different mean and covariance
from the posterior. Substituting $B$ into $P-BHP$ would give a different matrix
and is not the general candidate covariance formula.

## Try it

Keep the original model but observe $y=-3$. Find the exact posterior mean
and covariance.

**Answer:** The mean becomes $(-1,-1)^{\mathsf T}$. The covariance stays
$C_*$ because $P,H,R$, and hence the exact gain, are unchanged.

This tutorial checks the model's matrix identities. A certified tolerance for
an approximate law and certified output intervals require the package's full
checks. No new Lean instance or sampler is claimed here.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Finite-dimensional Gaussian model](../GLOSSARY.md#gaussian-model) · [Prior distribution](../GLOSSARY.md#prior) · [Likelihood](../GLOSSARY.md#likelihood) · [Posterior distribution](../GLOSSARY.md#posterior) · [Covariance matrix](../GLOSSARY.md#covariance) · [Precision matrix](../GLOSSARY.md#precision-matrix) · [Observation innovation](../GLOSSARY.md#innovation) · [Exact Gaussian gain](../GLOSSARY.md#gaussian-gain) · [Joseph covariance](../GLOSSARY.md#joseph-covariance)

These calculations explain the exact Gaussian model and a candidate Joseph covariance. The release’s law-error tolerance, interval output and emitted Lean-instance checks require their full contracts.

### Certified Inference

[Read](../works/certified-inference.md#read) · [Written proofs](../works/certified-inference.md#written-proofs) · [Lean coverage](../works/certified-inference.md#lean) · [Code and setup](../works/certified-inference.md#code) · [Evidence](../works/certified-inference.md#evidence)

### Certified Bayesian Inference

[Read](../works/research-certified-bayesian-inference.md#read) · [Written proofs](../works/research-certified-bayesian-inference.md#written-proofs) · [Lean coverage](../works/research-certified-bayesian-inference.md#lean) · [Code and setup](../works/research-certified-bayesian-inference.md#code) · [Evidence](../works/research-certified-bayesian-inference.md#evidence)

**Source passages:**

- [Certified Bayesian Inference: Gaussian model and posterior formulas](../../research/certified-bayesian-inference/Certified_Bayesian_Publication_1.0/manuscripts/foundations.tex#L1)
- [Certified Inference: execution and evidence contract](../../packages/certified-inference/README.md#L6)


[Edition guide and reproduction instructions](../../packages/certified-inference/README.md). Use each work’s Code and setup link for its implementation. The arithmetic check below covers this tutorial separately.

[Python arithmetic check for this example: gaussian_update()](../../tools/check_hand_examples.py#L522). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Choose repair directions from a finite menu](25_REPAIR_MENUS.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#gaussian-update)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
