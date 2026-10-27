# Security policy

Do not open a public issue for a vulnerability that could expose local
environment files, credentials, arbitrary code execution, or a bypass of
the offline guard. Use GitHub's private vulnerability reporting feature for
the repository.

Include the affected version, platform, minimal reproduction, impact, and
any proposed mitigation. Remove API keys, downloaded games, recordings, and
private paths from the report.

The process-level network guard is defense in depth. It is not a substitute
for operating-system sandboxing when executing untrusted environment code.
