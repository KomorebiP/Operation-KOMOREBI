# Orchestration failures

The first requested interactive container session was rejected with `StreamingExecNotEnabledContainerError` before its command executed. A subsequent shell invocation assumed the directory had been created and failed with `No such file or directory`. The directory and recovery script were then explicitly created using a normal execution call, and recovery succeeded. Neither failed call is counted as a test pass.

Additional CPython interpreter downloads failed because the public download host could not be resolved. The raw download diagnostics are retained. No alternate interpreter or Windows/WSL execution is claimed.

The meaningful product defect is independently reproduced in `ascii_locale_before.log`: the exporter returned unresolved when the default ASCII encoder could not encode the Lean conjunction symbol. The corrected identical export is in `ascii_locale_after.log`.
