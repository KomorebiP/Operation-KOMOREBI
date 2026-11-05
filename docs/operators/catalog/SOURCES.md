# Sources and scope

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

This catalog imports the refined operator compendium dated **4 November 2026**, by **Komorebi P.** It preserves 205 stable OP identifiers, their formulas and guards, 28 composition relations, and the associated finite fixtures.

## Source revisions

| Repository | Pinned revision |
|---|---|
| [KomorebiP/komorebi-math](https://github.com/KomorebiP/komorebi-math) | [`a3aa04ac18a523f30c50c7f5dba709f88e904eff`](https://github.com/KomorebiP/komorebi-math/tree/a3aa04ac18a523f30c50c7f5dba709f88e904eff) |
| [KomorebiP/Operation-KOMOREBI](https://github.com/KomorebiP/Operation-KOMOREBI) | [`f49e00d6088bbc8dca4f8a3a70b232db1eea085b`](https://github.com/KomorebiP/Operation-KOMOREBI/tree/f49e00d6088bbc8dca4f8a3a70b232db1eea085b) |

These immutable links identify the sources used by the compendium. They do not claim to be the latest moving branches. Recorded inspection locations describe the compendium review, not a fresh full-file inspection in this import. Some records are retained source routes, and one is a class-docstring search excerpt. A route is not a certification of every surrounding claim.

The import replayed the finite fixture suite. It did not replay Lean or the complete Komorebi Math library. Entry counts and fixture coverage do not measure novelty, independent theorems, or proof completion.

## Corrections in this edition

The imported reference has the following targeted corrections and scope clarifications. They are recorded in the registry; they do not rewrite the preserved source snapshot.

- [REL-09](RELATIONS.md#rel-09): Kernel preservation is equivalent to existence and uniqueness of an induced coarse map. It does not validate an arbitrary supplied candidate.
- [OP-057](C_COORDINATES.md#op-057), [REL-04](RELATIONS.md#rel-04): Polynomial integration requires a rational coefficient algebra or invertible integration denominators.
- [OP-173](C_COORDINATES.md#op-173), [REL-05](RELATIONS.md#rel-05): Residue packets use a positive modulus, normalized labels, and shifted labels read modulo that modulus.
- [OP-175](C_COORDINATES.md#op-175), [REL-17](RELATIONS.md#rel-17): The finite raising/lowering boundary is $(d+1)E_d$, which can vanish in characteristics dividing $d+1$.
- [OP-187](K_METRICS.md#op-187), [REL-13](RELATIONS.md#rel-13): The singular-value distortion contract requires positive dimension and compatible positive metrics.
- [OP-189](K_METRICS.md#op-189): The metric residual is linear in the metric pair for fixed map and scale, and quadratic-affine in the map.
- [REL-03](RELATIONS.md#rel-03): Coordinate composition uses three invertible charts and the same chart on the intermediate space.
- [REL-10](RELATIONS.md#rel-10): The coarse-defect composition law uses the composed coarse candidate. A separately proposed composite has an additional discrepancy term.

## Source register

<a id="source-u"></a>

### U. Unified executable language

[Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-a"></a>

### A. Komorebi Math API inventory

[Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-r"></a>

### R. Redundant frame algebra

[Redundant frame algebra](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md)

**Recorded scope:** Retained source route from the compendium.

**Source blob:** `a1c2996272e70aedbcbc589c24cc6824c2d3df25`.

<a id="source-as"></a>

### AS. Analysis and synthesis systems

[Analysis and synthesis systems](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-t"></a>

### T. Typed finite expression calculus

[Typed finite expression calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/TYPED_FINITE_EXPRESSION_CALCULUS.md)

**Recorded inspection:** Recorded line inspection 100-235.

**Source blob:** `ba5598908db74de2c08aef0b1a22671f6e9c3d30`.

<a id="source-c"></a>

### C. General coordinate atlas

[General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md)

**Recorded inspection:** Complete document.

**Source blob:** `a66a68e7d012896fc4384ee38ef4895f9816e32a`.

<a id="source-g"></a>

### G. Normalized generating functions

[Normalized generating functions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NORMALIZED_GENERATING_FUNCTIONS.md)

**Recorded scope:** Retained source route from the compendium.

**Source blob:** `2a2750b84b48e1ab6c600c1cc6938a48ba09dc96`.

<a id="source-n"></a>

### N. Finite nonlinear packet calculus

[Finite nonlinear packet calculus](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/NONLINEAR_CALCULUS.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-s"></a>

### S. Production finite signal processing

[Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md)

**Recorded inspection:** Recorded line inspection 1-140; Lines 190–275, recursive filtering and resampling.

**Source blob:** `02be2600b7469fc66d544641a14b7de393734d84`.

<a id="source-p"></a>

### P. Polyphase route packets

[Polyphase route packets](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/POLYPHASE_ROUTE_PACKETS.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-b"></a>

### B. Carrier change obstructions

[Carrier change obstructions](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/CARRIER_CHANGE_OBSTRUCTIONS.md)

**Recorded inspection:** Lines 1–115.

**Source blob:** `b8d10e160e9e350145ec54bfad1b6f6f484c1a47`.

<a id="source-q"></a>

### Q. Quantum memory contracts

[Quantum memory contracts](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/QUANTUM_MEMORY_NUMERICAL_CONTRACTS.md)

**Recorded inspection:** Recorded line inspection 1-95.

**Source blob:** `be334bec5c8f7628b520aad7f0214664126cc7b5`.

<a id="source-x"></a>

### X. Convex packets

[Convex packets](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/CONVEX_PACKETS.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-e"></a>

### E. Euler packet worked derivation

[Euler packet worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/EULER_PACKETS.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-fl"></a>

### FL. Factorial lanes worked derivation

[Factorial lanes worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/FACTORIAL_LANES.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-sb"></a>

### SB. Stirling Bell Fubini worked derivation

[Stirling Bell Fubini worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/STIRLING_BELL_FUBINI.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-ru"></a>

### RU. Roots of unity and falling-factorial coordinates

[Roots of unity and falling-factorial coordinates](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md)

**Recorded inspection:** Lines 285–510 and 690–850.

**Source blob:** `3739162fd482e2e7a22c226ed39e452014b31430`.

<a id="source-wp"></a>

### WP. Wavelet polyphase worked derivation

[Wavelet polyphase worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/WAVELET_POLYPHASE.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-sf"></a>

### SF. Special Functions reader

[Special Functions reader](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/SPECIAL_FUNCTIONS.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-f"></a>

### F. Special Functions formal scope

[Special Functions formal scope](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/SPECIAL_FUNCTIONS_FORMAL_SOURCES.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-k"></a>

### K. K-COS work and scope

[K-COS work and scope](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/monographs-cos-method.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-iv"></a>

### IV. Paper IV overview

[Paper IV overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-iv.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-ix"></a>

### IX. Paper IX overview

[Paper IX overview](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/works/paper-ix.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-li"></a>

### LI. Lean polynomial transport

[Lean polynomial transport](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/LEAN_POLYNOMIAL_TRANSPORT.md)

**Recorded scope:** Retained source route from the compendium.

<a id="source-tree"></a>

### TREE. Polynomial fixed-point source: supplied multilinear operation convention

[Polynomial fixed-point source: supplied multilinear operation convention](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/nonlinear/trees.py#L534-L650)

**Recorded inspection:** Source lines 534-650.

**Source blob:** `78f73cbb8f4d533b6e8bae8a6c29fda02eb409ec`.

<a id="source-comb"></a>

### COMB. Exact combinatorial coordinate source: matrix orientation

[Exact combinatorial coordinate source: matrix orientation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/coordinates/combinatorial.py#L69-L250)

**Recorded inspection:** Source lines 69-250.

**Source blob:** `e5d2d2aa130119bfe5f0dc693c27e698e0739542`.

<a id="source-combtest"></a>

### COMBTEST. Existing combinatorial-coordinate tests (read, not executed)

[Existing combinatorial-coordinate tests (read, not executed)](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/tests/test_coordinates_general_combinatorial.py)

**Recorded inspection:** Recorded line inspection 1-75.

**Source blob:** `a164b81cc6cfb1934e5e529d05e70f1087c60219`.

<a id="source-dc"></a>

### DC. Distortion cocycles and metric completion

[Distortion cocycles and metric completion](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/DISTORTION_COCYCLES.md)

**Recorded inspection:** Complete document, sections 1–8.

**Source blob:** `f358e51dcf49787861e9dbfa3a17242c36d52773`.

<a id="source-mp"></a>

### MP. Metric packets and coordinate covariance

[Metric packets and coordinate covariance](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md)

**Recorded inspection:** Complete document, sections 1–5.

**Source blob:** `0676b56c7658ad1cc42015d0d6ec546f9e5872d2`.

<a id="source-mi"></a>

### MI. Finite measure integration

[Finite measure integration](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_MEASURE_INTEGRATION.md)

**Recorded inspection:** Complete document.

**Source blob:** `d6075fd8c3dd67fba76b24433d3bd70ba664274c`.

<a id="source-ft"></a>

### FT. Finite trace separation

[Finite trace separation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/FINITE_CARRIER_COMPLETION.md)

**Recorded inspection:** Complete document.

**Source blob:** `4366241dfd92c45a7a0466e4f3b08bde4c28f182`.

<a id="source-cc"></a>

### CC. Companion coordinate examples

[Companion coordinate examples](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/COMPANION_COORDINATE_CALCULUS.md)

**Recorded inspection:** Complete document.

**Source blob:** `9d4fc863419301c6d660a70f73f84fc595fa368a`.

<a id="source-tc"></a>

### TC. Exact finite trace recovery implementation

[Exact finite trace recovery implementation](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/deformation/companions.py)

**Recorded inspection:** Lines 1–220, rational solver and separation result.

**Source blob:** `2ecdc52e85cde0e3826acfe704ab5d674fdd1689`.

<a id="source-ad"></a>

### AD. Atomic integrated derivative provider

[Atomic integrated derivative provider](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/integration/adapters.py)

**Recorded inspection:** Class AtomicIntegratedDerivativeProvider docstring: fixed finite weighted sum of compatible providers.

**Review scope:** Search excerpt of the class docstring only.

## Maintain the reference

The [structured registry](registry.json) is the canonical catalog. The family pages, this register, and the check and relation pages are generated from it. Worked-calculation routes are maintained and validated in the [catalog generator](../../../tools/operator_catalog.py). After an intentional edit, regenerate them with:

```text
python -B tools/operator_catalog.py
python -B tools/operator_catalog.py --check
python -B -m unittest discover -s tools -p test_operator_catalog.py
```

Keep a source revision, a precise input domain, and any hypothesis needed by a formula. Assign a finite check only when its actual fixture concerns that entry. Changes in the catalog do not change a paper’s recorded proof status.
