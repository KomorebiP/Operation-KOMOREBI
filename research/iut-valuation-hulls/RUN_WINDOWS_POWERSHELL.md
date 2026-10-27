# Replay on Windows / PowerShell

Run from the package root after making Lean 4.34.0-rc2 and Lake accessible.
The portable Lean runtime recorded in the Library is a Linux build; it can be
used under WSL, not as a native Windows executable. Example with Linux/WSL:

```powershell
wsl bash -lc 'cd /mnt/c/path/to/unpacked/B05/formalization/lean && lake build -KwarningAsError=true'
wsl bash -lc 'cd /mnt/c/path/to/unpacked/B05 && LEAN_BIN=$(command -v lean) LAKE_BIN=$(command -v lake) python3 verification/verify_b05.py'
```

For native Windows, use a matching Windows Lean and Lake, then:

```powershell
Set-Location 'C:\path\to\B05\formalization\lean'
lake build -KwarningAsError=true
Set-Location '..\..'
$env:LEAN_BIN = (Get-Command lean).Source
$env:LAKE_BIN = (Get-Command lake).Source
python verification/verify_b05.py
```

The verifier must be run after the Lake build has generated `.lake/build/lib/lean`.
Actual runtime/toolchain matching is recorded in `verification/b05/verification.json`.
