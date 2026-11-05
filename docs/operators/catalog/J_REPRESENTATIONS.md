# Finite arithmetic and representation models

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

Keep the representation, scalar field, observation map, and finite recovery conditions explicit.

The 5 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-167 · Finite Frobenius action](#op-167)
- [OP-168 · Finite monodromy operator](#op-168)
- [OP-169 · Finite cochain coboundary](#op-169)
- [OP-181 · Finite trace observation](#op-181)
- [OP-182 · Trace-table reconstruction](#op-182)

<a id="op-167"></a>

## OP-167. Finite Frobenius action

**Kind:** linear.

```math
v\mapsto Fv
```

**Scope.** A declared finite linear model over a specified fixed field. If Frobenius acts on extension-field scalars, record F(av)=sigma(a)F(v) instead of asserting full-field linearity.

**Keep in view.** A chosen Frobenius element acts linearly through the declared representation. This is not automatically the scalar power map $x\mapsto x^p$ in OP-037.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A30](CHECKS.md#a30).

**Related entries:** [OP-037](B_CYCLIC.md#op-037) · [OP-181](J_REPRESENTATIONS.md#op-181) · [OP-182](J_REPRESENTATIONS.md#op-182).


<a id="op-168"></a>

## OP-168. Finite monodromy operator

**Kind:** linear.

```math
N:V\to V
```

**Scope.** Specified finite dimensional representation with nilpotent N. Any relation to Frobenius and its normalization must be stated separately.

**Keep in view.** Monodromy data require nilpotence and any Frobenius compatibility convention from the actual representation.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-169"></a>

## OP-169. Finite cochain coboundary

**Kind:** linear.

```math
d^n:C^n\to C^{n+1},\qquad d^{n+1}d^n=0
```

**Scope.** Explicit finite cochain complex over a declared ring or field. The displayed condition is not automatic for arbitrary linear maps.

**Keep in view.** A cochain differential has degree +1 and compatible adjacent types. Squaring to zero is a family condition.

**Sources:** [N: Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A57](CHECKS.md#a57).

**Related entries:** [OP-114](F_NONLINEAR.md#op-114).


<a id="op-181"></a>

## OP-181. Finite trace observation

**Kind:** linear.

```math
\mathcal T_A(m)=Am
```

**Scope.** Supplied finite matrix whose columns are declared constituent trace lists. The scalar field and selected rows are fixed.

**Keep in view.** This measures finite linear combinations. It does not establish an arithmetic identification outside the supplied places.

**Source relationship.** Explicit source construction.

**Sources:** [FT: Finite trace separation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_CARRIER_COMPLETION.md) · [TC: Exact finite trace recovery implementation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/deformation/companions.py).

**Finite checks linked:** [R32](CHECKS.md#r32), [R34](CHECKS.md#r34).

**Related entries:** [OP-015](A_STRUCTURAL.md#op-015) · [OP-167](J_REPRESENTATIONS.md#op-167) · [OP-179](G_DYNAMICS.md#op-179) · [OP-182](J_REPRESENTATIONS.md#op-182).

**Composition laws:** [Finite trace recovery](RELATIONS.md#rel-22).


<a id="op-182"></a>

## OP-182. Trace-table reconstruction

**Kind:** linear on the image; guarded recovery.

```math
R_A(Am)=m,\qquad \operatorname{rank}A=r
```

**Scope.** A has r columns and full column rank. Observations must belong to its image. Recovery is for the selected trace rows.

**Keep in view.** The source selects independent rows. Unused observations need a separate consistency check. A rational solution is not automatically an integral nonnegative multiplicity vector.

**Source relationship.** Explicit source construction.

**Sources:** [FT: Finite trace separation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_CARRIER_COMPLETION.md) · [TC: Exact finite trace recovery implementation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/deformation/companions.py).

**Finite checks linked:** [R32](CHECKS.md#r32), [R33](CHECKS.md#r33), [R34](CHECKS.md#r34), [R35](CHECKS.md#r35).

**Related entries:** [OP-078](D_ARITHMETIC.md#op-078) · [OP-167](J_REPRESENTATIONS.md#op-167) · [OP-179](G_DYNAMICS.md#op-179) · [OP-181](J_REPRESENTATIONS.md#op-181).

**Composition laws:** [Finite trace recovery](RELATIONS.md#rel-22).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
