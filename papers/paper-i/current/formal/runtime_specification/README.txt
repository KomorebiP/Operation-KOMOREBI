Pinned runtime reconstruction specification

These five small files are copied byte-for-byte from the exact portable kit
used for this release. They identify its Lake workspace, dependency revisions,
Lean toolchain selection, launcher and host compatibility adapter source.

The Linux x86_64 Lean toolchain, compiled compatibility adapter and dependency
cache are external prerequisites; this directory is not a runnable binary kit.
The accepted audit authenticates the precise runtime file hashes and dependency
revisions in ../runtime_bindings.json. It reuses the pinned upstream cache.

The copied launcher is included to specify the release's Lake invocation.
Its optional kit-specific verify/attach actions require other kit scripts and
are not needed by the release's formal/verify.sh command. Supply a complete
pinned portable runtime when following formal/README.txt.

The launcher license is preserved in LICENSE. SOURCE_HASHES.json records
the five source/configuration files and that license notice.
