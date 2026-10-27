# Runtime recovery failures

- First Library batch download of all seven parts plus start ZIP failed with HTTP 502. No Lean build was attempted or counted as successful. Retrying the authenticated helper with a smaller selection.
- Second Library download of part 01 plus start ZIP failed with HTTP 502. Retrying only the 3 KB start ZIP to distinguish bulk-transfer size from general service failure.
- Third Library download of the 3 KB start ZIP alone failed with HTTP 502. This also blocks the small starter file, so archive size alone does not explain the failure.
- Fourth download, the distinct newer 414 KB p-adic runtime-recovery archive, also failed with HTTP 502.

## Resolution

Another collaborating agent supplied an existing exact runtime path, `/workspace/scratch/3e94b90aa142/runtime/Komorebi_Portable_Lean_4.34.0-rc2`. Lean starts with the exact expected commit; all nine package pins match, and a cached mathlib import plus rational arithmetic proof pass with warnings-as-errors. No download success is claimed, and no runtime files were modified.
