# 24. Calculate coefficients of contracted feedback

[All examples](../HAND_WORKED_EXAMPLES.md) · [Glossary: coefficient recurrence](../GLOSSARY.md#coefficient-recurrence) · [Papers, proofs, Lean and code](#papers-proofs-lean-and-code)

The Special Functions monograph places contracted arguments inside a nonlinear
differential equation. We will calculate the first coefficients for its scales
$q=1/3$ and $r=2/3$.

## Read the defining equation

The normalized odd series satisfies

```math
T'(z)=1+T(qz)T(rz),\qquad T(0)=0.
```

The prime denotes differentiation with respect to $z$. Write

```math
T(z)=z+c_1z^3+c_2z^5+c_3z^7+\cdots.
```

The coefficient of $z$ is one because the defining equation gives $T'(0)=1$.
Substitution scales each coefficient by its degree:

```math
T(qz)=qz+c_1q^3z^3+c_2q^5z^5+\cdots.
```

## Match the first two nonconstant derivative coefficients

The coefficient of $z^2$ in $T(qz)T(rz)$ is $qr$. Since differentiation
turns $c_1z^3$ into $3c_1z^2$,

```math
3c_1=qr=\frac29,\qquad c_1=\frac2{27}.
```

The coefficient of $z^4$ has two contributions, from degrees one and three:

```math
5c_2=c_1(qr^3+q^3r)
=\frac2{27}\left(\frac8{81}+\frac2{81}\right)
=\frac{20}{2187}.
```

Thus $c_2=4/2187$, and the polynomial through degree five is

```math
T_{\le5}(z)=z+\frac2{27}z^3+\frac4{2187}z^5.
```

For instance, its value at one is exactly $2353/2187$. This is the value of
the displayed polynomial. An error bound for its difference from the full
function requires a bound on the omitted tail.

## Write the recurrence

Set $c_0=1$. Matching degree $2n$ gives

```math
c_n=\frac1{2n+1}\sum_{i=0}^{n-1}
q^{2i+1}r^{2(n-1-i)+1}c_i c_{n-1-i},\qquad n\ge1.
```

Each new coefficient depends on finitely many earlier ones. For $n=3$, the
three products give

```math
7c_3=c_2(qr^5+q^5r)+c_1^2q^3r^3
=\frac{136}{1594323}+\frac{32}{531441}
=\frac{232}{1594323}.
```

Hence $c_3=232/11160261$, agreeing with the monograph's displayed member.

## Try it

Use the same recurrence with $q=r=1/2$. Find $c_1$ and $c_2$.

**Answer:** $c_1=(1/4)/3=1/12$. Then
$5c_2=(1/12)(1/16+1/16)=1/96$, so $c_2=1/480$.

These finite coefficient identities explain the construction. The monograph's
analytic existence, growth and separation results require their full arguments.

<!-- learning-navigation -->

## Papers, proofs, Lean and code

**Terms in this example:** [Derivative in the series example](../GLOSSARY.md#derivative) · [Differential equation](../GLOSSARY.md#differential-equation) · [Initial condition](../GLOSSARY.md#initial-condition) · [Contracted argument](../GLOSSARY.md#contracted-argument) · [Coefficient recurrence](../GLOSSARY.md#coefficient-recurrence)

This example expands the defining coefficient recurrence for a member of Special Functions. Finite coefficient checks do not replace the monograph’s analytic existence, growth or separation arguments.

### Special Functions

[Read](../works/monographs-special-functions.md#read) · [Written proofs](../works/monographs-special-functions.md#written-proofs) · [Lean coverage](../works/monographs-special-functions.md#lean) · [Code and setup](../works/monographs-special-functions.md#code) · [Evidence](../works/monographs-special-functions.md#evidence)

**Source passages:**

- [Special Functions: defining equation and coefficient recurrence](../../monographs/special-functions/monograph/main.tex#L78)


[Edition guide and reproduction instructions](../../monographs/special-functions/README.md). Use each work’s Code and setup link for its implementation. The arithmetic check below covers this tutorial separately.

[Python arithmetic check for this example: contracted_feedback()](../../tools/check_hand_examples.py#L463). This checks the displayed rational, modular or finite-set calculations exactly.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

- [Previous: Find the reusable part of a calibration](23_CALIBRATED_CONTINUATION.md)
- [Next: Choose repair directions from a finite menu](25_REPAIR_MENUS.md)
- [All examples](../HAND_WORKED_EXAMPLES.md)
- [Topic map](../LEARNING_MAP.md#contracted-feedback)
- [Example coverage by work](../EXAMPLE_COVERAGE.md)
