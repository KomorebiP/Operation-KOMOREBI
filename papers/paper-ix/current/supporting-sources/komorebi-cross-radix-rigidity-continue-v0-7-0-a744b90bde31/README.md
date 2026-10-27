# Komorebi Cross-Radix Rigidity — certified continuation v0.7.0

v0.7.0 closes the Bell-downstream-interface and uniform common-hull block on top of certified v0.6.0.

## New internal theorem package

The new module `src/CrossRadixBellCommonHull.lean` defines an eventual bounded quasi-polynomial downstream interface and proves that one fixed linear submodule `CommonHull N T d` contains every positive affine section, hence every depth/address of every positive radix.  The hull itself is invariant under all positive affine sections and satisfies

`finrank CommonHull <= N + T*(d+1)`.

This is a field-level complex theorem downstream of an explicit interface. Bell's theorem remains external. See `BELL_EXTERNAL_INTERFACE.md`.

## Integrity

- frozen v0.6 ZIP SHA-256: `7c715d5c522079a26332e9987ce4684e985da9df6961c4add6e9cbc37f9c7e92`
- new theorem module SHA-256: `b54b69fb7629581b6aa7a0394e90fc6b3384347c5da78621db71761a1c0cf5c8`
- v0.7 axiom-audit module SHA-256: `f09790c50d24435d0a0c41035bdeffd32af0e8e7e0fee7921fd71906f140c4e9`
- all 29 v0.6 source hashes preserved
- no `sorry`, `admit`, or custom `axiom` in `src/`
- strict new-module gate: `-DwarningAsError=true`

The naive base-independent integral normal form remains rejected.
