# Final delivery evidence

The core archive was extracted into a new directory. The delivered runner passed
its frozen-record checks, typed source contract, 42 verifier tests, ten integrity
tests and the complete finite replay. The extracted core manifest passed before
and after that execution. No core file changed.

A supplementary extracted-object consumer initially exceeded a 30-second limit.
That attempt was killed and remains failed under `failed_consumer_30s/`. The same
source was rerun with the existing production allowance of 300 seconds. It passed
in 54.401942 seconds, including a real projector application and two transitive
axiom queries. This was an import/consumer check, not a second 118-module source
build. No source or proof was changed for the retry.

The final complete ZIP contains the exact already-verified core tree and these
additional external delivery records. Its separate final JSON receipt supplies
the complete ZIP digest after freeze, avoiding circular self-hashing.
