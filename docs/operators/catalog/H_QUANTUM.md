# Quantum and finite spectral operators

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Finite checks](CHECKS.md)

Specify channels, measurements, charge sectors, leakage, and finite spectral constructions.

The 12 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-137 · Charge-sector projector](#op-137)
- [OP-138 · Quantum circuit composition](#op-138)
- [OP-139 · Kraus quantum channel](#op-139)
- [OP-140 · Dephasing channel](#op-140)
- [OP-141 · Lindblad generator](#op-141)
- [OP-142 · Born measurement functional](#op-142)
- [OP-143 · Moving packet leakage](#op-143)
- [OP-144 · Quantum Feshbach operator](#op-144)
- [OP-145 · Euclidean transfer](#op-145)
- [OP-146 · Heat semigroup](#op-146)
- [OP-147 · Heat trace functional](#op-147)
- [OP-148 · Knill–Laflamme compression](#op-148)

<a id="op-137"></a>

## OP-137. Charge-sector projector

**Kind:** linear.

```math
P_q\text{ selects fixed total charge }q
```

**Scope.** Finite declared additive symmetry and eigenspaces

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-039](B_CYCLIC.md#op-039).


<a id="op-138"></a>

## OP-138. Quantum circuit composition

**Kind:** linear.

```math
U=U_m\cdots U_1
```

**Scope.** Fixed finite dimensional gates U_1,...,U_m, applied rightmost first in the displayed product. Joint dependence on all gates is multilinear.

**Keep in view.** The product is linear on state vectors for fixed gates. Gate ordering must be retained.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-139"></a>

## OP-139. Kraus quantum channel

**Kind:** linear.

```math
\mathcal E(\rho)=\sum_jK_j\rho K_j^\dagger
```

**Scope.** Complete positivity; trace preserving if $\sum_jK_j^\dagger K_j=I$

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A48](CHECKS.md#a48).

**Related entries:** [OP-140](H_QUANTUM.md#op-140) · [OP-141](H_QUANTUM.md#op-141) · [OP-148](H_QUANTUM.md#op-148).


<a id="op-140"></a>

## OP-140. Dephasing channel

**Kind:** linear.

```math
\mathcal D(\rho)=\sum_jP_j\rho P_j
```

**Scope.** Complete orthogonal measurement sectors

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A49](CHECKS.md#a49).

**Related entries:** [OP-009](A_STRUCTURAL.md#op-009) · [OP-139](H_QUANTUM.md#op-139).


<a id="op-141"></a>

## OP-141. Lindblad generator

**Kind:** linear.

```math
\mathcal L(\rho)=-i[H,\rho]+\sum_j(L_j\rho L_j^\dagger-\tfrac12\{L_j^\dagger L_j,\rho\})
```

**Scope.** Finite matrices, Hermitian $H$, specified jumps

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [Q: Quantum memory contracts](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/QUANTUM_MEMORY_NUMERICAL_CONTRACTS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-119](G_DYNAMICS.md#op-119) · [OP-139](H_QUANTUM.md#op-139).


<a id="op-142"></a>

## OP-142. Born measurement functional

**Kind:** linear.

```math
\rho\mapsto\operatorname{tr}(M\rho)
```

**Scope.** Finite density matrix rho with trace one and a fixed effect 0<=M<=I for an outcome probability. General Hermitian M gives an observable expectation, not necessarily a probability.

**Keep in view.** A probability measurement effect must satisfy M<=I, not merely positivity.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A50](CHECKS.md#a50).


<a id="op-143"></a>

## OP-143. Moving packet leakage

**Kind:** nonlinear functional.

```math
\Vert (I-P(t))U(t)P(0)\Vert
```

**Scope.** Finite numerical operator norm and continuous packet family

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-144"></a>

## OP-144. Quantum Feshbach operator

**Kind:** linear action; rational operator family.

```math
H_{PP}+H_{PQ}(zI-H_{QQ})^{-1}H_{QP}
```

**Scope.** Fixed finite block Hamiltonian and z outside the hidden spectrum. It can depend on z and is not a single energy-independent Hamiltonian.

**Keep in view.** The effective Hamiltonian is linear on retained vectors at a fixed resolvent point, although its block construction is nonlinear.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [Q: Quantum memory contracts](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/QUANTUM_MEMORY_NUMERICAL_CONTRACTS.md).

**Finite checks linked:** [A46](CHECKS.md#a46).

**Related entries:** [OP-131](G_DYNAMICS.md#op-131) · [OP-132](G_DYNAMICS.md#op-132).


<a id="op-145"></a>

## OP-145. Euclidean transfer

**Kind:** linear.

```math
e^{-a(H-E_0I)}
```

**Scope.** Finite Hermitian Hamiltonian and declared offset/step

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-119](G_DYNAMICS.md#op-119) · [OP-146](H_QUANTUM.md#op-146).


<a id="op-146"></a>

## OP-146. Heat semigroup

**Kind:** linear.

```math
x\mapsto e^{-tH}x
```

**Scope.** Fixed finite nonnegative operator $H$

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [Q: Quantum memory contracts](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/QUANTUM_MEMORY_NUMERICAL_CONTRACTS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-119](G_DYNAMICS.md#op-119) · [OP-145](H_QUANTUM.md#op-145) · [OP-147](H_QUANTUM.md#op-147).


<a id="op-147"></a>

## OP-147. Heat trace functional

**Kind:** nonlinear.

```math
H\mapsto\operatorname{tr}(e^{-tH})
```

**Scope.** Finite nonnegative spectral operator; trace is nonlinear in $H$

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [Q: Quantum memory contracts](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/QUANTUM_MEMORY_NUMERICAL_CONTRACTS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-146](H_QUANTUM.md#op-146).


<a id="op-148"></a>

## OP-148. Knill–Laflamme compression

**Kind:** sesquilinear error-pair map; criterion.

```math
P E_i^\dagger E_j P=c_{ij}P
```

**Scope.** Fixed orthogonal code projector P and finite error family. P E_i* E_j P is conjugate-linear in E_i and linear in E_j. The criterion requires a scalar matrix c_ij for every pair.

**Keep in view.** Over complex spaces the error-pair map is sesquilinear, not bilinear. The displayed scalar-compression condition is a criterion, not itself a recovery map.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Finite checks linked:** [A08](CHECKS.md#a08).

**Related entries:** [OP-139](H_QUANTUM.md#op-139).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
