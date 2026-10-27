# v25 development diagnostics

An initial module compile could not find a project dependency because the new
Euler namespace output directory shadowed the baseline fallback. Copying the
baseline compiled artifacts into the development import root resolved it.
Subsequent development compiles caught coercion, API-name, rewrite, and linter
errors. Explicit types and local algebraic lemmas repaired those before the
clean replays. The new proof statements were not weakened to make these pass.
Raw per-module development logs were overwritten during repairs; no claim of
complete failed-log preservation is made. The final full compile logs are saved.

Both final clean replays and all retained mathematical computations passed.
A later `ps` inspection returned shell status 1 because all monitored jobs had
already exited; their terminal success reports were present. That inspection
status is not a computation failure.
