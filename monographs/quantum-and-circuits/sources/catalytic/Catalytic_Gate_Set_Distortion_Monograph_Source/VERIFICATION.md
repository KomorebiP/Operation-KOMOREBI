# Release verification summary

The release was audited in the build environment with the following checks:

- Python smoke suite: 4 tests passed.
- Canonical linear words evaluated over moduli 2, 3, 5, and 8.
- Complete three-bit affine-versus-Toffoli total and entangling censuses matched the frozen result.
- Complete binary symplectic Clifford censuses matched frozen JSON for:
  - three-qubit swap-free total count;
  - three-qubit total count with unit-cost SWAP;
  - three-qubit entangling count.
- OpenQASM witness files regenerated from the frozen gate words.
- All Python-generated vector figures regenerated.
- LaTeX rebuilt successfully to a 160-page PDF.
- PDF preflight: openable, unencrypted, non-scanned, no XFA, 160 letter-size pages.
- All listed fonts are embedded and subsetted.
- Render inspection covered the front matter, theorem-dense core, quantum-gate chapters, code appendix, bibliography, and index. No blank verso page remains in the digital build.

The monograph distinguishes symbolic proofs, complete finite computations, formal research skeletons, and conjectures. Exact finite results apply only to the model conventions declared in the text and JSON metadata.
