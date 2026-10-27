# Execution issues

- Initial request for a streaming container session failed with StreamingExecNotEnabledContainerError before a Lean process ran. Bounded subprocess execution is used instead.
- An outer invocation ended before RationalMatrixCertificates produced a completion receipt, leaving a child process. The child group was explicitly killed. The attempted broad Mathlib.Tactic import was removed; no result from that attempt is used.
