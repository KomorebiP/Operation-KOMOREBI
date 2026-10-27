# Development incidents

The failed compilation logs in this directory are intermediate attempts, not accepted results. The accepted fresh run is in ../accepted.

Direct network download of the compiler failed at DNS/URL retrieval. The offline Library kit was recovered instead. Earlier runtime work had reset before proof compilation.

The compiler rejected first-pass uses of changed/deprecated API names, some implicit scalar interpretations, missing prerequisite group instances, and linter violations. These were corrected before the clean accepted build. No production axiom or admitted proof was used to bridge an obligation.

The first whole-environment audit attempts were interrupted/time-limited before a complete result. They did not yield accepted audit receipts. The module-name array was being recomputed inside the declaration loop. The final audit caches it outside the loop, and both preflight and post-clean-build audits passed. The accepted process retains standard warning and axiom rejection policies.

The ten deliberately failing files under tests/negative are a separate diagnostic suite. Their required failures are recorded as successful rejection controls, not as successful theorem elaborations.
