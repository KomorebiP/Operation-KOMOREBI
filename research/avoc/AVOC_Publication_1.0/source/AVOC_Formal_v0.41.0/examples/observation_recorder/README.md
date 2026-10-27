# Recorder examples

All examples are synthetic. No operation is executed.

- `complete.json`: two identities, four completed operations, one retained fault, one exact terminal replay, and a late begin. The snapshot is ready.
- `pending.json`: the same history followed by an unrelated pending intent. This blocks calibration export for every identity.
- `registry.json`: an injective explicit map from keys 0 and 1 to the warm and cold protected quote identities used in earlier examples.
- `scenarios.json`: twelve exact expected snapshots or rejection responses for independent tests.
- `contract.json`: the declared finite experiment bounds and limits of interpretation.

See `RECORDER_EXECUTABLE.md` for the protocol and commands. `ready` means no pending operation; calibration still enforces its own predeclared checkpoint and authority rules.
