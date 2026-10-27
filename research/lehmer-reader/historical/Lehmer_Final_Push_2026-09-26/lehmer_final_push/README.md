# Lehmer final push

Start with [RESEARCH_NOTE.md](RESEARCH_NOTE.md). The conjecture remains
unresolved. This bundle contains the final route results, independent audits,
reproducible exact computations and the complete preceding checkpoint archive.

- [Current status](STATUS.json)
- [Polynomial content theorem](null_span/POLYNOMIAL_CONTENT_THEOREM.md)
- [Congruence and local Frobenius barriers](arithmetic/NOTE.md)
- [Interpolation boundary](null_span/NOTE.md)
- [Global synthetic-model theorem](prior_audit/SYNTHETIC_MODEL.md)
- [Inherited theorem audit](prior_audit/AUDIT.md)
- [New theorem audit](prior_audit/FINAL_BRANCH_AUDIT.md)
- [Source normalization](SOURCES.md)

Each computation directory has its command, exact bounds, hashes and status
in manifest.json. Scripts use only Python's standard library. The manifest
root is this folder for computations/valuations001, arithmetic/ for
arithmetic/computation001, and null_span/ for null_span/computations/run001.
No formal proof-assistant verification or historical priority is claimed.
