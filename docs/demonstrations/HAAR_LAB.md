# Decompose and reconstruct a signal through four Haar levels

[Open the interactive Haar lab](https://KomorebiP.github.io/Operation-KOMOREBI/interactive.html#haar) · [Four-sample introduction](../examples/14_HAAR_PAIRS.md) · [All demonstrations](../DEMONSTRATIONS.md)

The lab extends the neighboring-pair calculation to sixteen real samples.
It uses the **averaging normalization** throughout. Start with a shape, edit its
samples, then choose which details to retain. The diagrams show the original
signal, its reconstruction, and their difference at the original addresses.

## Analyze four levels

For each neighboring pair, compute

```math
a=(u+v)/2,\qquad d=(u-v)/2.
```

Save the details and apply the same rule to the averages. Sixteen samples give
eight first-level averages, then four, two, and one. Store the final mean,
followed by the details from coarse to fine: one at level 4, two at level 3,
four at level 2, and eight at level 1. There are sixteen coefficients in total.

The default **Steps and a spike** signal is

```math
x=(2,2,2,2,6,6,6,6,-4,-4,12,-4,4,4,4,4).
```

Its intermediate values are:

| Level | Averages | Details |
|---|---|---|
| 1 | $(2,2,6,6,-4,4,4,4)$ | $(0,0,0,0,0,8,0,0)$ |
| 2 | $(2,6,0,4)$ | $(0,0,-4,0)$ |
| 3 | $(4,2)$ | $(-2,-2)$ |
| 4 | $(3)$ | $(1)$ |

The global mean is 3. A level-$j$ detail acts on a block of $2^j$ samples:
it adds its value on the first half and subtracts it on the second half.
The coefficient tiles show these support addresses, indexed from zero.

## Select details and reconstruct

Invert each pair with $u=a+d$ and $v=a-d$, beginning with the global mean and
the level-4 detail. Continue toward the original samples. An omitted detail
is replaced by zero. The interface always retains the global mean.

Try these selections on the default signal:

| Selection | Retained coefficients | Squared reconstruction error |
|---|---:|---:|
| All coefficients | 16 | 0 |
| Magnitude cutoff 0.25 | 6 | 0 |
| Drop finest details | 8 | 128 |
| Coarse structure: mean and levels 4 and 3 | 4 | 192 |
| Magnitude cutoff 4 | 3 | 80 |
| Mean only | 1 | 272 |

Moving the cutoff selects every detail whose absolute value is at least the
cutoff. You can then override the selection with individual checkboxes.
Editing samples reapplies the current automatic selection; a manual selection
keeps the chosen support addresses. Counts describe retained coefficients,
not a measured file size or a production compression format.

Removing the finest details replaces the pair $(12,-4)$ by its average pair
$(4,4)$. All other pairs in this signal already have zero first-level detail.
The residual is 8 at address 10, $-8$ at address 11, and zero elsewhere, so
its squared norm is $8^2+(-8)^2=128$.

## Account for the normalization and energy

The averaging transform is not orthonormal. The synthesis vector for a
level-$j$ detail has $2^j$ entries equal to $+1$ or $-1$, and hence squared
norm $2^j$. The global-mean vector has sixteen entries equal to 1.
These sixteen synthesis vectors are mutually orthogonal: disjoint supports
give zero inner product; on nested supports the finer vector has zero sum
where the coarser vector is constant. Each detail also has zero sum against
the global-mean vector.

If $m$ is the final mean and $d_{j,k}$ are the details, then

```math
\|x\|_2^2
=16m^2+\sum_{j=1}^{4}2^j\sum_{k=0}^{16/2^j-1}d_{j,k}^2.
```

For the default signal, this is

```math
416=16(3^2)+16(1^2)+8((-2)^2+(-2)^2)+4((-4)^2)+2(8^2).
```

Let $\widehat{x}$ be the reconstruction from retained coefficients and set
$r=x-\widehat{x}$. Orthogonality separates the retained and omitted terms:

```math
\|x\|_2^2=\|\widehat{x}\|_2^2+\|r\|_2^2.
```

In particular, the squared error equals the sum of the **weighted** squares of
omitted coefficients. The interface's energy table displays this identity
for the current selection. Adding unweighted coefficient squares would use
the wrong normalization.

## Arithmetic and sources

The controls accept sixteen integers between $-16$ and 16. Four averaging
levels introduce only fractions with power-of-two denominators. The coefficients,
inverse calculations, and squared norms remain exactly representable in the
browser's arithmetic for these bounds. Graph coordinates are display positions;
the tables retain the exact numerical values.

The [four-sample Haar example](../examples/14_HAAR_PAIRS.md) gives the pair matrix,
its inverse, and the normalization identity. Follow its links to
[Paper V](../works/paper-v.md) and [Information Realization](../works/information-realization.md)
for the broader setting and recorded evidence. This teaching extension adds no
new formal verification or production software qualification.

[Return to the lab](https://KomorebiP.github.io/Operation-KOMOREBI/interactive.html#haar)
