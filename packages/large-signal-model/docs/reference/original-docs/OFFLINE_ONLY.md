# Offline-only execution contract

The solver runtime is local-only.

## Enforced in code

1. `Arcade` is constructed with `OperationMode.OFFLINE`.
2. The ARC API key is empty.
3. Only the bundled `environment_files` tree is scanned.
4. Socket connections, DNS lookup, `urllib`, `http.client`, and Requests calls are blocked in the solver process.
5. Proxy variables point to an unreachable loopback address.
6. The command-line interface exposes no online or competition command.
7. No game downloader is bundled in this 25-test edition.
8. The official toolkit loads local game source; the agent receives only public observations and public actions.

## Static source audit

The 25 supplied game files are parsed before execution. The audit rejects network, subprocess, browser, and filesystem imports, along with selected dynamic-execution calls. The audit is a packaging safeguard; it is not used by the agent to infer game rules.

## Optional OS-level hardening

`Run_Offline_Hardened.ps1` temporarily creates a Windows Firewall outbound-block rule for the exact Python executable in the selected Conda environment. Administrator privileges are required. The rule is removed in a `finally` block.

## One-time installation

Dependency installation may use the internet. Actual environment validation and agent execution do not. Offline runs do not create official online scorecards or leaderboard submissions.
