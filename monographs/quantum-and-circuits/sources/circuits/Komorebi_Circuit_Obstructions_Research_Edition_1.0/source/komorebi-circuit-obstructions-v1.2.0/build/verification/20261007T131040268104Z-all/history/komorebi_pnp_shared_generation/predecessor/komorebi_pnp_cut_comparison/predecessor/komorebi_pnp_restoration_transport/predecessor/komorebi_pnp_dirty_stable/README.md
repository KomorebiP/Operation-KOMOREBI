# Reproduce

Run:

```bash
python checks/verify_dirty_stable.py
```

Expected result: JSON reporting 5,880 reversible clean-input checks, 65,808 exact
existential-commutation truth tables, and k-control gate counts 2k-3 for k=2..8.

No Lean verification is claimed.
