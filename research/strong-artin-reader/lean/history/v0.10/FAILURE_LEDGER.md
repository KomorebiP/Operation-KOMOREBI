# v0.10 failure ledger

All entries below are development or integration failures. None is reported as a proved theorem.

1. Initial portable-runtime assembly was launched from the wrong working directory and could not
   find the seven archive parts. Rerunning from the parts directory fixed the path issue.
2. An early cold full-file check hit a bounded execution timeout. It was recorded as incomplete,
   not as a Lean proof failure.
3. Several early helper proofs failed on `Representation.asModule`/subrepresentation type-synonym
   coercions. Canonical explicit group-algebra linear equivalences replaced the fragile coercions.
4. A raw Lean invocation omitted the workspace module search path and failed to import the core.
   The pinned `lake env lean` path fixed the environment error.
5. The isotypic-finrank proof initially lacked `Module.Finite K` instances for group-algebra
   submodules after scalar restriction. These were supplied through injective inclusions into the
   finite-dimensional ambient vector spaces.
6. The component-bijection proof initially attempted a direct target constituent match. It was
   simplified to injections in both directions plus finite-cardinality Schröder–Bernstein.
7. A monolithic v0.10 source merge exceeded the 300-second execution ceiling without a Lean
   theorem error. It is therefore not certified. The canonical checked v0.10 continuation is
   modular and preserves the exact v0.9 core.
8. The interrupted monolithic Lake build removed the inherited core `.olean`. The exact v0.9
   source was restored and rebuilt successfully before the final modular root was checked again.
