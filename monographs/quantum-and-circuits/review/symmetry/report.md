# Summary

The symmetry component now has corrected statements, explicit algorithmic hypotheses, a new adaptive error certificate, and reproducible exact and numerical checks. The reviewed core comprises invariant and moving packets, leakage, bounded excitation, Schur compression, charge scaling, orbit quotients, and branch merging. External stabilizer, Gaussian, and Schur theory was not independently reproved. This is a delegated review followed by self-review of the changes; model settings are inherited and not exposed.

# Main mathematical concerns

The density-limit entropy formula was too strong. Under only k(n)/n→p, its remainder need not be logarithmic. The corrected form uses the varying density inside the entropy: log2 binom(n,k)=n H2(k/n)+O(log n)=n H2(p)+o(n). The conclusion that finite-density sectors are exponential is unchanged. The parent independently checked the sqrt(n) counterexample.

# Other mathematical concerns

The revised source removes a false uniqueness assertion for zero-weight normalized Schur blocks and corrects the bounded-excitation proof to use the actual confined trajectory rather than assume whole-sector invariance. Initialization, successor enumeration, canonical keys, measurement access, and a sufficient continuous-time bound are now explicit. The finite-unitary relation between invariance and commutation and the occupation-raising convention are stated correctly.

The new adaptive discarded-state theorem proves that an unnormalized projected trajectory has total state error at most the sum of its actual discarded norms. Effect expectation error is at most twice that sum. Its exact two-step rational example has squared state error 832/625, below the squared certificate 1024/625. This is a written proof, not Lean.

# Exposition and organization

Numerical reconstruction is now identified as numerical. The historical runtime tables remain historical. Recorded computation panels no longer imply exact arithmetic. All changed LaTeX environments and cross references passed static checks. Visual rendering is delegated to the combined-volume build.

# Claim and scope assessment

The result remains a collection of sufficient classical simulation theorems under declared representation and access conditions. It proves no universal quantum complexity collapse. Guaranteed polynomial adaptive growth remains open despite the completed error-accounting theorem. No symmetry Lean formalization is supplied. The contextual order-six product-cell nonexistence implication was checked against arXiv:2603.02334v1, Definitions 2–3, Theorem 6 and its final proof. The entangled existence result remains a cited external theorem, not a new result of this volume.

# Questions for the authors

None needed for the repaired release scope. Research questions are retained explicitly in the monograph.

# Suggested revisions

The coordinator should publish the rebuilt combined volume and mark the original standalone symmetry PDF and its original hashes as historical. The source changes are recorded in source_changes.patch and source_changes.json.

# Overall assessment

All three current validation commands passed. The original numerical suite has maximum reconstruction residual 2.532e-16 against tolerance 2e-12. The new exact suite passes 308 rational/integer assertions, including 27 fixed-weight circuit instances on one through six qubits and dimension checks through twelve qubits. Twenty-one API boundary controls pass. The packet compiler now rejects any represented nonzero leakage, preserves complex outputs for real inputs, and rejects invalid basis or qubit data.

During editing, disk exhaustion truncated a Python source file. The file was restored from the preserved original and the patch reapplied, then parsed and tested successfully. The first provenance validation rejected absolute paths; those were converted to workspace-relative paths and all three manifests then validated. No timing benchmark was rerun, and no separate symmetry PDF was rebuilt.
