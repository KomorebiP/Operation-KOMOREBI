# Named finite checks

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

The catalog links to **164 named fixtures**: 93 identity checks, 59 counterexample checks, and 12 input-rejection controls. The programs use integers and `fractions.Fraction`. They require only Python’s standard library and use no network access.

All 164 fixtures passed in the import replay. A passing counterexample check means the intended failure was observed. A passing guard check means the fixture helper rejected its stated invalid input. These are finite mathematical fixtures, not whole-library execution or Lean verification.

From a repository checkout:

```text
python -B examples/operator_catalog/Komorebi_Operator_Refined_Checks.py
```

To save a fresh receipt, append `--json /path/to/local_results.json`. The command reruns both the preserved 79-check suite and the 85 additional checks. [Program and reproduction instructions](../../../examples/operator_catalog/README.md).

## What each fixture checks

<a id="l01"></a>

### L01. residue projectors complete

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-025](B_CYCLIC.md#op-025). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l02"></a>

### L02. residue projectors orthogonal

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-025](B_CYCLIC.md#op-025). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l03"></a>

### L03. transfer reconstructs operator

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-010](A_STRUCTURAL.md#op-010) · [OP-011](A_STRUCTURAL.md#op-011). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l04"></a>

### L04. transfer composes with all middle packets

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-012](A_STRUCTURAL.md#op-012). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l05"></a>

### L05. redundant analysis synthesis law

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-016](A_STRUCTURAL.md#op-016) · [OP-017](A_STRUCTURAL.md#op-017). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l06"></a>

### L06. physical components reconstruct, not all idempotent

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-021](A_STRUCTURAL.md#op-021). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l07"></a>

### L07. second presentation is exact

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-016](A_STRUCTURAL.md#op-016) · [OP-017](A_STRUCTURAL.md#op-017). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l08"></a>

### L08. bridge composes redundant coefficient lifts

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-019](A_STRUCTURAL.md#op-019) · [OP-020](A_STRUCTURAL.md#op-020). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l09"></a>

### L09. falling factorial transport is not multiplicative

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-041](C_COORDINATES.md#op-041). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l10"></a>

### L10. basepoint integral of derivative retains constant defect

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-053](C_COORDINATES.md#op-053) · [OP-054](C_COORDINATES.md#op-054) · [OP-057](C_COORDINATES.md#op-057). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l11"></a>

### L11. derivative of exact basepoint integral is identity

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-053](C_COORDINATES.md#op-053) · [OP-054](C_COORDINATES.md#op-054). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l12"></a>

### L12. three-phase FIR transfer agrees with direct convolution

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-079](E_SIGNAL.md#op-079) · [OP-080](E_SIGNAL.md#op-080) · [OP-081](E_SIGNAL.md#op-081) · [OP-082](E_SIGNAL.md#op-082). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l13"></a>

### L13. CRT idempotents and sum

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-034](B_CYCLIC.md#op-034). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l14"></a>

### L14. CRT reconstructs both residues

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-035](B_CYCLIC.md#op-035). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l15"></a>

### L15. EGF Hurwitz coefficient agrees with ordinary multiplication

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-051](C_COORDINATES.md#op-051) · [OP-067](C_COORDINATES.md#op-067). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l16"></a>

### L16. Haar reconstruction needs signed addition

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-084](E_SIGNAL.md#op-084) · [OP-085](E_SIGNAL.md#op-085). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l17"></a>

### L17. Kato generator is skew for rotating orthogonal packet pair

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-115](F_NONLINEAR.md#op-115). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="l18"></a>

### L18. Boolean support cannot preserve signed cancellation

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-162](I_COMPUTATIONAL.md#op-162). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a01"></a>

### A01. rectangular packet composition with distinct spaces

**Kind:** identity. **Cases:** 4.

**Entries:** [OP-010](A_STRUCTURAL.md#op-010) · [OP-011](A_STRUCTURAL.md#op-011) · [OP-012](A_STRUCTURAL.md#op-012). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a02"></a>

### A02. noncommuting projector product need not be a projector

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-028](B_CYCLIC.md#op-028). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a03"></a>

### A03. canonical coefficient projection and complementary gauge

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-018](A_STRUCTURAL.md#op-018) · [OP-017](A_STRUCTURAL.md#op-017). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a04"></a>

### A04. coefficient lift sandwich and recovery

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-019](A_STRUCTURAL.md#op-019) · [OP-022](A_STRUCTURAL.md#op-022). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a05"></a>

### A05. quotient metric bridge isometry

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-020](A_STRUCTURAL.md#op-020) · [OP-023](A_STRUCTURAL.md#op-023). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a06"></a>

### A06. physical-component one-index composition fails

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-021](A_STRUCTURAL.md#op-021) · [OP-012](A_STRUCTURAL.md#op-012). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a07"></a>

### A07. adjoint formation is complex conjugate-linear

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-005](A_STRUCTURAL.md#op-005). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a08"></a>

### A08. error-pair compression is sesquilinear

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-148](H_QUANTUM.md#op-148). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a09"></a>

### A09. forced companion update is not homogeneous linear

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-063](C_COORDINATES.md#op-063). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a10"></a>

### A10. operator squaring is nonlinear in the operator

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-013](A_STRUCTURAL.md#op-013). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a11"></a>

### A11. transported falling-factorial projectors reconstruct

**Kind:** identity. **Cases:** 10.

**Entries:** [OP-025](B_CYCLIC.md#op-025) · [OP-026](B_CYCLIC.md#op-026) · [OP-041](C_COORDINATES.md#op-041). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a12"></a>

### A12. derivative transports to forward difference

**Kind:** identity. **Cases:** 9.

**Entries:** [OP-041](C_COORDINATES.md#op-041) · [OP-047](C_COORDINATES.md#op-047) · [OP-053](C_COORDINATES.md#op-053). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a13"></a>

### A13. rectangular derivative coordinate naturality

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-040](C_COORDINATES.md#op-040) · [OP-053](C_COORDINATES.md#op-053). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a14"></a>

### A14. Lah rising-to-falling orientation

**Kind:** identity. **Cases:** 10.

**Entries:** [OP-046](C_COORDINATES.md#op-046). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a15"></a>

### A15. lower sequence orientation is wrong for Lah polynomial coordinates

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-046](C_COORDINATES.md#op-046). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a16"></a>

### A16. Newton differences reconstruct in binomial normalization

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-047](C_COORDINATES.md#op-047) · [OP-048](C_COORDINATES.md#op-048). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a17"></a>

### A17. falling coefficients need the Newton factorial divisor

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-048](C_COORDINATES.md#op-048). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a18"></a>

### A18. subset zeta and Mobius are inverse

**Kind:** identity. **Cases:** 4.

**Entries:** [OP-050](C_COORDINATES.md#op-050). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a19"></a>

### A19. factorial normalization fails at characteristic degree p

**Kind:** counterexample. **Cases:** 4.

**Entries:** [OP-051](C_COORDINATES.md#op-051) · [OP-052](C_COORDINATES.md#op-052). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a20"></a>

### A20. characteristic zero does not put logarithm in integer series

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-066](C_COORDINATES.md#op-066). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a21"></a>

### A21. nonzero-inner-constant formal substitution need not stabilize

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-060](C_COORDINATES.md#op-060). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a22"></a>

### A22. nonunit reciprocal is rejected

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-065](C_COORDINATES.md#op-065). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a23"></a>

### A23. formal reciprocal jet products

**Kind:** identity. **Cases:** 15.

**Entries:** [OP-065](C_COORDINATES.md#op-065). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a24"></a>

### A24. normalized Mahler masks telescope

**Kind:** identity. **Cases:** 3.

**Entries:** [OP-070](D_ARITHMETIC.md#op-070) · [OP-071](D_ARITHMETIC.md#op-071). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a25"></a>

### A25. mask recovery loses the constant scale

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-071](D_ARITHMETIC.md#op-071). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a26"></a>

### A26. unnormalized infinite-product mask is rejected

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-070](D_ARITHMETIC.md#op-070). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a27"></a>

### A27. Cartier decimation and residue projection have different indices

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-025](B_CYCLIC.md#op-025) · [OP-036](B_CYCLIC.md#op-036). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a28"></a>

### A28. commutative prime-characteristic Frobenius identity

**Kind:** identity. **Cases:** 3.

**Entries:** [OP-037](B_CYCLIC.md#op-037). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a29"></a>

### A29. noncommutative characteristic-two Frobenius fails additivity

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-037](B_CYCLIC.md#op-037). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a30"></a>

### A30. finite-field Frobenius is not extension-field linear

**Kind:** counterexample. **Cases:** 16.

**Entries:** [OP-037](B_CYCLIC.md#op-037) · [OP-167](J_REPRESENTATIONS.md#op-167). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a31"></a>

### A31. Kummer valuations match carries on the declared range

**Kind:** identity. **Cases:** 8580.

**Entries:** [OP-076](D_ARITHMETIC.md#op-076) · [OP-077](D_ARITHMETIC.md#op-077). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a32"></a>

### A32. carry transition matrices agree with direct mask product

**Kind:** identity. **Cases:** 129.

**Entries:** [OP-072](D_ARITHMETIC.md#op-072) · [OP-073](D_ARITHMETIC.md#op-073). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a33"></a>

### A33. general normalized convolution agrees with basis transport

**Kind:** identity. **Cases:** 7.

**Entries:** [OP-052](C_COORDINATES.md#op-052) · [OP-067](C_COORDINATES.md#op-067). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a34"></a>

### A34. polyphase cascade retains middle phases and lag carries

**Kind:** identity. **Cases:** 378.

**Entries:** [OP-012](A_STRUCTURAL.md#op-012) · [OP-081](E_SIGNAL.md#op-081) · [OP-082](E_SIGNAL.md#op-082) · [OP-083](E_SIGNAL.md#op-083). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a35"></a>

### A35. normalized synthesis is not a raw adjoint

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-016](A_STRUCTURAL.md#op-016) · [OP-017](A_STRUCTURAL.md#op-017) · [OP-094](E_SIGNAL.md#op-094) · [OP-095](E_SIGNAL.md#op-095). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a36"></a>

### A36. threshold retention is not a linear fixed mask

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-088](E_SIGNAL.md#op-088) · [OP-099](E_SIGNAL.md#op-099). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a37"></a>

### A37. Haar average/detail energy uses a factor of two

**Kind:** identity. **Cases:** 49.

**Entries:** [OP-084](E_SIGNAL.md#op-084) · [OP-085](E_SIGNAL.md#op-085). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a38"></a>

### A38. Kato generator has the correct commutator sign

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-115](F_NONLINEAR.md#op-115). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a39"></a>

### A39. weighted conditional expectation is an idempotent metric projection

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-125](G_DYNAMICS.md#op-125). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a40"></a>

### A40. Bayesian normalization is nonlinear in the prior

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-126](G_DYNAMICS.md#op-126). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a41"></a>

### A41. Markov column convention conserves total mass

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-122](G_DYNAMICS.md#op-122) · [OP-123](G_DYNAMICS.md#op-123). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a42"></a>

### A42. finite Markov aggregation commutes exactly when specified

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-124](G_DYNAMICS.md#op-124) · [OP-121](G_DYNAMICS.md#op-121). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a43"></a>

### A43. Schur complement inverse matches retained inverse block

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-132](G_DYNAMICS.md#op-132). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a44"></a>

### A44. nilpotent finite semigroup law is exact

**Kind:** identity. **Cases:** 3.

**Entries:** [OP-119](G_DYNAMICS.md#op-119). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a45"></a>

### A45. generator defect integrates to finite semigroup defect

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-121](G_DYNAMICS.md#op-121) · [OP-135](G_DYNAMICS.md#op-135). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a46"></a>

### A46. Schrodinger memory carries the negative kernel sign

**Kind:** identity. **Cases:** 7.

**Entries:** [OP-133](G_DYNAMICS.md#op-133) · [OP-144](H_QUANTUM.md#op-144). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a47"></a>

### A47. an algebraic resolvent point need not be a Laplace point

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-134](G_DYNAMICS.md#op-134). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a48"></a>

### A48. rational Kraus channel preserves trace

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-139](H_QUANTUM.md#op-139). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a49"></a>

### A49. dephasing is an idempotent channel

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-140](H_QUANTUM.md#op-140). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a50"></a>

### A50. positive measurement operator alone does not bound probability

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-142](H_QUANTUM.md#op-142). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a51"></a>

### A51. Boolean support composition misses signed cancellation

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-158](I_COMPUTATIONAL.md#op-158) · [OP-162](I_COMPUTATIONAL.md#op-162). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a52"></a>

### A52. signed mass product preserves the signed observation

**Kind:** identity. **Cases:** 256.

**Entries:** [OP-163](I_COMPUTATIONAL.md#op-163). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a53"></a>

### A53. fiber collisions obstruct a carrier factorization

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-162](I_COMPUTATIONAL.md#op-162). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a54"></a>

### A54. equal tropical scalar summaries lose argmax multiplicity

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-164](I_COMPUTATIONAL.md#op-164). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a55"></a>

### A55. an asymmetric convex gauge is not a norm

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-165](I_COMPUTATIONAL.md#op-165). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a56"></a>

### A56. COS constant mode requires half weighting

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-166](I_COMPUTATIONAL.md#op-166). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a57"></a>

### A57. finite cochain differential squares to zero with orientation

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-169](J_REPRESENTATIONS.md#op-169). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a58"></a>

### A58. Picard supplied-operation convention has no extra factorial

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-106](F_NONLINEAR.md#op-106). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a59"></a>

### A59. finite ordered-tree sum equals the matching Picard iterate

**Kind:** identity. **Cases:** 5.

**Entries:** [OP-105](F_NONLINEAR.md#op-105) · [OP-106](F_NONLINEAR.md#op-106). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a60"></a>

### A60. second-order composition uses the correct evaluation point

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-104](F_NONLINEAR.md#op-104). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="a61"></a>

### A61. general nonlinear maps cannot omit mixed packet terms

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-116](F_NONLINEAR.md#op-116). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Audit_Checks.py).

<a id="r01"></a>

### R01. gauge complement is idempotent and synthesizes to zero

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-170](A_STRUCTURAL.md#op-170) · [OP-018](A_STRUCTURAL.md#op-018) · [OP-016](A_STRUCTURAL.md#op-016) · [OP-017](A_STRUCTURAL.md#op-017). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r02"></a>

### R02. coefficient gauge is generally oblique

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-170](A_STRUCTURAL.md#op-170) · [OP-018](A_STRUCTURAL.md#op-018). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r03"></a>

### R03. two-endpoint transport preserves a rectangular action

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-171](A_STRUCTURAL.md#op-171) · [OP-008](A_STRUCTURAL.md#op-008) · [OP-040](C_COORDINATES.md#op-040). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r04"></a>

### R04. rectangular transports compose with the same middle chart

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-171](A_STRUCTURAL.md#op-171) · [OP-003](A_STRUCTURAL.md#op-003) · [OP-012](A_STRUCTURAL.md#op-012). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r05"></a>

### R05. covector pullback needs no invertible map

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-172](C_COORDINATES.md#op-172) · [OP-055](C_COORDINATES.md#op-055) · [OP-171](A_STRUCTURAL.md#op-171). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r06"></a>

### R06. contragredient coordinate storage preserves pairings

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-172](C_COORDINATES.md#op-172) · [OP-024](A_STRUCTURAL.md#op-024). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r07"></a>

### R07. falling-factorial transport has an exact triangular inverse

**Kind:** identity. **Cases:** 3.

**Entries:** [OP-041](C_COORDINATES.md#op-041) · [OP-042](C_COORDINATES.md#op-042) · [OP-043](C_COORDINATES.md#op-043). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r08"></a>

### R08. transported coefficient projectors are complete and orthogonal

**Kind:** identity. **Cases:** 123.

**Entries:** [OP-173](C_COORDINATES.md#op-173) · [OP-009](A_STRUCTURAL.md#op-009) · [OP-025](B_CYCLIC.md#op-025). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r09"></a>

### R09. degree labels cannot be replaced by ordinary-power labels

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-173](C_COORDINATES.md#op-173) · [OP-025](B_CYCLIC.md#op-025) · [OP-041](C_COORDINATES.md#op-041). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r10"></a>

### R10. forward differences shift the transported residue address

**Kind:** identity. **Cases:** 15.

**Entries:** [OP-173](C_COORDINATES.md#op-173) · [OP-047](C_COORDINATES.md#op-047) · [OP-031](B_CYCLIC.md#op-031). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r11"></a>

### R11. transported product is associative and unital

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-174](C_COORDINATES.md#op-174). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r12"></a>

### R12. finite differences obey Leibniz for the transported product

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-174](C_COORDINATES.md#op-174) · [OP-047](C_COORDINATES.md#op-047). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r13"></a>

### R13. ordinary multiplication has a shifted rather than differential Leibniz rule

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-174](C_COORDINATES.md#op-174) · [OP-047](C_COORDINATES.md#op-047). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r14"></a>

### R14. raising advances the falling-factorial basis

**Kind:** identity. **Cases:** 9.

**Entries:** [OP-175](C_COORDINATES.md#op-175) · [OP-059](C_COORDINATES.md#op-059). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r15"></a>

### R15. raising and difference have the polynomial Weyl commutator

**Kind:** identity. **Cases:** 3.

**Entries:** [OP-175](C_COORDINATES.md#op-175) · [OP-047](C_COORDINATES.md#op-047) · [OP-007](A_STRUCTURAL.md#op-007). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r16"></a>

### R16. a finite square Weyl representation retains a top-degree defect

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-175](C_COORDINATES.md#op-175) · [OP-047](C_COORDINATES.md#op-047). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r17"></a>

### R17. backward difference realizes the falling-factorial degree operator

**Kind:** identity. **Cases:** 9.

**Entries:** [OP-176](C_COORDINATES.md#op-176). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r18"></a>

### R18. finite characteristic preserves the integral basis but loses a spectral selector

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-041](C_COORDINATES.md#op-041) · [OP-173](C_COORDINATES.md#op-173) · [OP-176](C_COORDINATES.md#op-176) · [OP-029](B_CYCLIC.md#op-029). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r19"></a>

### R19. formal compositional inversion works in both directions

**Kind:** identity. **Cases:** 16.

**Entries:** [OP-177](C_COORDINATES.md#op-177) · [OP-060](C_COORDINATES.md#op-060). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r20"></a>

### R20. singular formal charts are rejected

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-177](C_COORDINATES.md#op-177). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r21"></a>

### R21. formal exponential and logarithm invert after truncation

**Kind:** identity. **Cases:** 2.

**Entries:** [OP-203](C_COORDINATES.md#op-203) · [OP-066](C_COORDINATES.md#op-066). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r22"></a>

### R22. formal exponential converts commuting sums into products

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-203](C_COORDINATES.md#op-203) · [OP-204](C_COORDINATES.md#op-204). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r23"></a>

### R23. formal exponential rejects an unhandled constant term

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-203](C_COORDINATES.md#op-203). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r24"></a>

### R24. normalized multiplication matches independent ordinary coefficients

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-204](C_COORDINATES.md#op-204) · [OP-052](C_COORDINATES.md#op-052) · [OP-067](C_COORDINATES.md#op-067). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r25"></a>

### R25. general normalized multiplication is associative

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-204](C_COORDINATES.md#op-204). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r26"></a>

### R26. initial state plus defects reconstructs an arbitrary finite sequence

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-178](C_COORDINATES.md#op-178) · [OP-063](C_COORDINATES.md#op-063) · [OP-064](C_COORDINATES.md#op-064). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r27"></a>

### R27. discarding recurrence defects changes a nonhomogeneous sequence

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-178](C_COORDINATES.md#op-178) · [OP-064](C_COORDINATES.md#op-064). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r28"></a>

### R28. observability recovers the initial state when full rank

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-179](G_DYNAMICS.md#op-179) · [OP-178](C_COORDINATES.md#op-178). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r29"></a>

### R29. a longer observation list need not resolve a hidden state

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-179](G_DYNAMICS.md#op-179). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r30"></a>

### R30. controllability uses chronological input powers

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-180](G_DYNAMICS.md#op-180) · [OP-063](C_COORDINATES.md#op-063). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r31"></a>

### R31. reversing input order changes the terminal state

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-180](G_DYNAMICS.md#op-180). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r32"></a>

### R32. finite trace observation and reconstruction are inverse on the image

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-181](J_REPRESENTATIONS.md#op-181) · [OP-182](J_REPRESENTATIONS.md#op-182). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r33"></a>

### R33. inconsistent overdetermined observations are rejected

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-182](J_REPRESENTATIONS.md#op-182). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r34"></a>

### R34. rank-deficient trace data cannot resolve all constituents

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-181](J_REPRESENTATIONS.md#op-181) · [OP-182](J_REPRESENTATIONS.md#op-182). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r35"></a>

### R35. unique rational recovery is not an integral multiplicity certificate

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-182](J_REPRESENTATIONS.md#op-182). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r36"></a>

### R36. joint query retains both observations but may keep a nonzero kernel

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-183](I_COMPUTATIONAL.md#op-183). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r37"></a>

### R37. kernel-preserving dynamics descends to the coarse state

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-184](I_COMPUTATIONAL.md#op-184) · [OP-015](A_STRUCTURAL.md#op-015) · [OP-124](G_DYNAMICS.md#op-124). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r38"></a>

### R38. equal present observations can have different future observations

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-184](I_COMPUTATIONAL.md#op-184) · [OP-162](I_COMPUTATIONAL.md#op-162). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r39"></a>

### R39. metric adjoint satisfies the exact pairing identity

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-185](K_METRICS.md#op-185) · [OP-005](A_STRUCTURAL.md#op-005). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r40"></a>

### R40. metric adjoints reverse composition

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-185](K_METRICS.md#op-185) · [OP-003](A_STRUCTURAL.md#op-003). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r41"></a>

### R41. a singular coefficient metric cannot be inverted as a positive metric

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-185](K_METRICS.md#op-185) · [OP-023](A_STRUCTURAL.md#op-023). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r42"></a>

### R42. whitening carries the metric quadratic form

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-186](K_METRICS.md#op-186) · [OP-185](K_METRICS.md#op-185). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r43"></a>

### R43. changing metric factors changes only unitary coordinates

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-186](K_METRICS.md#op-186) · [OP-187](K_METRICS.md#op-187). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r44"></a>

### R44. distortion is submultiplicative but not multiplicative

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-187](K_METRICS.md#op-187). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r45"></a>

### R45. individual finite-order generators can hide a mixed-word obstruction

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-187](K_METRICS.md#op-187) · [OP-189](K_METRICS.md#op-189) · [OP-191](K_METRICS.md#op-191). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r46"></a>

### R46. the source two-generator balancing metric has distortion nine

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-187](K_METRICS.md#op-187) · [OP-189](K_METRICS.md#op-189). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r47"></a>

### R47. determinant normalization fixes modulus rather than sign

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-188](K_METRICS.md#op-188). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r48"></a>

### R48. edge metric propagation gives a vanishing isometry residual

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-189](K_METRICS.md#op-189) · [OP-191](K_METRICS.md#op-191). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r49"></a>

### R49. metric propagation composes along a path

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-191](K_METRICS.md#op-191) · [OP-024](A_STRUCTURAL.md#op-024). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r50"></a>

### R50. metric holonomy residual is coordinate invariant

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-190](K_METRICS.md#op-190) · [OP-024](A_STRUCTURAL.md#op-024). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r51"></a>

### R51. keeping the metric fixed breaks full-coordinate invariance

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-190](K_METRICS.md#op-190). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r52"></a>

### R52. the unipotent metric equation exposes the positive-metric obstruction

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-189](K_METRICS.md#op-189) · [OP-191](K_METRICS.md#op-191). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r53"></a>

### R53. quadratic metric defects obey the exact pullback composition law

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-192](K_METRICS.md#op-192) · [OP-189](K_METRICS.md#op-189) · [OP-171](A_STRUCTURAL.md#op-171). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r54"></a>

### R54. plain addition is not the metric-defect composition law

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-192](K_METRICS.md#op-192). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r55"></a>

### R55. atomic integration is linear in the integrand

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-193](L_INTEGRATION.md#op-193) · [OP-197](L_INTEGRATION.md#op-197). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r56"></a>

### R56. atomic moments reproduce independent point evaluation

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-194](L_INTEGRATION.md#op-194) · [OP-193](L_INTEGRATION.md#op-193). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r57"></a>

### R57. integration covectors carry the exact polynomial basis witness

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-194](L_INTEGRATION.md#op-194) · [OP-172](C_COORDINATES.md#op-172) · [OP-040](C_COORDINATES.md#op-040). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r58"></a>

### R58. affine pushforward equals pullback of the integrand

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-195](L_INTEGRATION.md#op-195) · [OP-058](C_COORDINATES.md#op-058) · [OP-172](C_COORDINATES.md#op-172). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r59"></a>

### R59. noninjective finite pushforward preserves total mass

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-195](L_INTEGRATION.md#op-195) · [OP-193](L_INTEGRATION.md#op-193). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r60"></a>

### R60. finite product integration agrees with iterated moments

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-196](L_INTEGRATION.md#op-196) · [OP-194](L_INTEGRATION.md#op-194). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r61"></a>

### R61. product marginals cannot replace an arbitrary joint measure

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-196](L_INTEGRATION.md#op-196). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r62"></a>

### R62. Simpson moments certify every cubic polynomial on the given interval

**Kind:** identity. **Cases:** 4.

**Entries:** [OP-197](L_INTEGRATION.md#op-197) · [OP-198](L_INTEGRATION.md#op-198). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r63"></a>

### R63. exact rational quadrature is not exact integration at every degree

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-197](L_INTEGRATION.md#op-197) · [OP-198](L_INTEGRATION.md#op-198). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r64"></a>

### R64. a signed quadrature rule need not preserve positivity

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-193](L_INTEGRATION.md#op-193) · [OP-197](L_INTEGRATION.md#op-197). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r65"></a>

### R65. quadrature residual is the coefficient pairing with moment discrepancies

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-198](L_INTEGRATION.md#op-198) · [OP-194](L_INTEGRATION.md#op-194). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r66"></a>

### R66. fixed-weight differentiation commutes with a finite weighted sum

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-199](L_INTEGRATION.md#op-199) · [OP-102](F_NONLINEAR.md#op-102) · [OP-193](L_INTEGRATION.md#op-193). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r67"></a>

### R67. moving weights contribute an additional derivative term

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-199](L_INTEGRATION.md#op-199). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r68"></a>

### R68. integration by parts retains its bilinear endpoint term

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-200](L_INTEGRATION.md#op-200) · [OP-053](C_COORDINATES.md#op-053) · [OP-056](C_COORDINATES.md#op-056). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r69"></a>

### R69. negative affine slope uses absolute density scaling

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-201](L_INTEGRATION.md#op-201) · [OP-195](L_INTEGRATION.md#op-195). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r70"></a>

### R70. a constant affine map produces an atom rather than an infinite density

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-201](L_INTEGRATION.md#op-201) · [OP-195](L_INTEGRATION.md#op-195). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r71"></a>

### R71. canonical dual synthesis is a left inverse with orthogonal coefficient projection

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-202](A_STRUCTURAL.md#op-202) · [OP-017](A_STRUCTURAL.md#op-017) · [OP-018](A_STRUCTURAL.md#op-018) · [OP-094](E_SIGNAL.md#op-094). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r72"></a>

### R72. rank-deficient analysis cannot use the full-rank dual formula

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-202](A_STRUCTURAL.md#op-202). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r73"></a>

### R73. zero-state recursive filtering is linear

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-205](E_SIGNAL.md#op-205). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r74"></a>

### R74. recursive filtering composes across chunks only with continuation state

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-205](E_SIGNAL.md#op-205) · [OP-063](C_COORDINATES.md#op-063). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r75"></a>

### R75. dropping a filter continuation state changes the next chunk

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-205](E_SIGNAL.md#op-205). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r76"></a>

### R76. a nonzero fixed filter state gives an affine input map

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-205](E_SIGNAL.md#op-205) · [OP-063](C_COORDINATES.md#op-063). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r77"></a>

### R77. recursive filter rejects a zero leading denominator

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-205](E_SIGNAL.md#op-205). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r78"></a>

### R78. Bayesian nonlinearity is witnessed against both endpoint images

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-126](G_DYNAMICS.md#op-126). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r79"></a>

### R79. rational matrix fixtures reject ragged input

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-159](I_COMPUTATIONAL.md#op-159). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r80"></a>

### R80. rational matrix fixtures reject mismatched addition

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-004](A_STRUCTURAL.md#op-004) · [OP-159](I_COMPUTATIONAL.md#op-159). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r81"></a>

### R81. rational matrix fixtures reject truncated vector application

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-159](I_COMPUTATIONAL.md#op-159). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r82"></a>

### R82. exact fixture inputs reject implicit floating-point conversion

**Kind:** guard rejection. **Cases:** 1.

**Entries:** [OP-159](I_COMPUTATIONAL.md#op-159). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r83"></a>

### R83. typed coarse-map defects retain both intermediate contributions

**Kind:** identity. **Cases:** 1.

**Entries:** [OP-121](G_DYNAMICS.md#op-121) · [OP-184](I_COMPUTATIONAL.md#op-184) · [OP-171](A_STRUCTURAL.md#op-171). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r84"></a>

### R84. coarse-map defects cannot be added without their transports

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-121](G_DYNAMICS.md#op-121) · [OP-184](I_COMPUTATIONAL.md#op-184). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).

<a id="r85"></a>

### R85. finite recursive evaluation does not imply infinite-time stability

**Kind:** counterexample. **Cases:** 1.

**Entries:** [OP-205](E_SIGNAL.md#op-205). [Fixture source](../../../examples/operator_catalog/Komorebi_Operator_Refined_Checks.py).
