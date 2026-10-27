# ABC offline bounded-exhaustive search

This is a resumable offline search suite for primitive triples

\[
a+b=c,
\qquad
q(a,b,c)=\frac{\log c}{\log\operatorname{rad}(abc)}.
\]

It is designed for Windows through WSL and uses all available CPU cores. It does not claim to exhaust the infinite `abc` problem. It exhausts the finite search grammars and numerical boxes recorded in `coverage.json`.

## One PowerShell command

After extracting the folder to Downloads:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force; & "$env:USERPROFILE\Downloads\ABC_Offline_Exhaustive_Search\Run_ABC_Offline.ps1" -Profile Deep -Hours 24 -Workers 18 -FactorLimit 5000
```

Run the same command again to resume. Completed tasks are not repeated.

To inspect the size of a profile before starting:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force; & "$env:USERPROFILE\Downloads\ABC_Offline_Exhaustive_Search\Run_ABC_Offline.ps1" -Profile Deep -Plan
```

To spend a later run only on unresolved candidate factorization:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force; & "$env:USERPROFILE\Downloads\ABC_Offline_Exhaustive_Search\Run_ABC_Offline.ps1" -Profile Deep -FactorOnly -FactorLimit 10000
```


## Direct WSL fallback

The launcher now converts ordinary `C:\...` paths without calling `wslpath`. If a local policy or unusual Windows path still interferes, this command bypasses the PowerShell launcher entirely:

```powershell
$R="/mnt/c/Users/$env:USERNAME/Downloads/ABC_Offline_Exhaustive_Search"; wsl.exe -e bash "$R/run_wsl.sh" --profile deep --workdir "$R/runs/deep" --hours 24 --workers 18 --factor-limit 5000
```

## Search engines

### Complete convergent and intermediate-convergent box

For every configured power-free core pair `B,C`, exponent `d`, prime `q`, depth interval, and every root of

```text
C r^d = B mod q^e
```

the program follows every root, including singular branches, by checking every lift digit. It enumerates every continued-fraction convergent and every intermediate convergent up to the configured denominator. The exact finite box is recorded in `coverage.json`.

### Forced affine-ray box

When `ray_steps` is positive, consecutive convergents define affine rays. The program exhausts the configured ray pairs, endpoint prime powers, and `k` steps. `ray_tail=0` means all consecutive convergent rays. A positive `ray_tail` means only that many deepest rays, and the coverage file records this restriction.

### Low-support plateau box

When enabled, the program generates every low-radical endpoint in the configured prime, support, exponent, and size box, then tests every configured seed `a` and exponent `m` in

```text
x^m - a.
```

It retains candidates containing at least one configured repeated local prime packet. This engine is disabled in the supplied profiles because its Cartesian box can be very large. Enable it in a custom profile when desired.

### Low-support near-neighbor box

The program generates every integer in the configured multiplicative box and checks every pair whose numerical difference is at most `max_difference`. This is the engine that independently recovers

```text
2 + 3^10*109 = 23^5
```

when the bounds include the primes 109 and 23.

## Safe pruning and exact verification

A candidate is pruned only when the radical factors already forced by its construction are sufficient to rule out the configured quality threshold. Unknown factors are never assumed squarefree.

Every retained candidate below `factor_bits` is factored and rescored exactly. Larger candidates remain in the database with status `deferred` rather than disappearing.

## Outputs

A run directory contains:

- `search.sqlite` — checkpoint, candidate queue, and verified triples
- `coverage.json` — exact configuration and completed task counts
- `results/all_candidates.csv` — every retained candidate
- `results/verified_triples.csv` — exact factorizations and qualities
- `results/summary.json` — best result and coverage totals

## Profiles

- `Quick` is a short installation and correctness run
- `Deep` is intended for an overnight or multi-day run
- `Extreme` is a large research profile and may require days or weeks

The supplied profiles deliberately keep the plateau engine disabled. Create a custom profile to enable it.

## Custom profile

Write the built-in deep profile:

```powershell
wsl bash -lc "cd '/mnt/c/Users/$env:USERNAME/Downloads/ABC_Offline_Exhaustive_Search' && ./run_wsl.sh --write-profile deep"
```

Edit `deep_profile.json`, then run:

```powershell
wsl bash -lc "cd '/mnt/c/Users/$env:USERNAME/Downloads/ABC_Offline_Exhaustive_Search' && ./run_wsl.sh --config deep_profile.json --workdir runs/custom --hours 72 --workers 18 --factor-limit 10000"
```

## Verification

```powershell
wsl bash -lc "cd '/mnt/c/Users/$env:USERNAME/Downloads/ABC_Offline_Exhaustive_Search' && ./verify_wsl.sh"
```

The verification suite checks singular Hensel lifting, intermediate convergents, exact recovery of the current benchmark, resumability, primitive identities, radicals, and quality calculations.

## Meaning of exhaustive

The suite is exhaustive only for the declared finite grammar:

- configured core pairs
- configured exponents and prime-power depths
- configured convergent and intermediate-convergent denominator range
- configured affine-ray range
- configured low-support endpoint box
- configured near-neighbor difference window

It is not a proof that no better triple exists outside those boxes, and it is not a universal Thue–Mahler solver.
