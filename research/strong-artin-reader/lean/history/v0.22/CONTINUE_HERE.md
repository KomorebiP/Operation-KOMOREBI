# Continue Strong Artin from v0.22

## Restore point

Use this directory as the canonical additive checkpoint above:

```text
Strong_Artin_Lean_v0.21.0_Completed_Formal_Presentation_Checked.zip
```

The exact base archive SHA-256 is:

```text
97d7ae4b8bf0804af7eea942cc11d0a10b7587dcea4223cd757947fba28b8d51
```

## Strongest checked endpoint

```text
relation syzygies
  → raw transpose-Jacobian kernel
  → intrinsic cotangent H1
  → 0
```

is exact, the middle map is surjective, and it is injective exactly under conormal independence of the selected relations.

With an externally supplied equivalence from cotangent H1 to the transverse Selmer obstruction space, the same exact sequence transports to Selmer.

## Critical correction

Do not identify the raw kernel of a chosen relation Jacobian with intrinsic Selmer obstruction without proving one of:

1. the relation generators are independent in the conormal module; or
2. the relation-syzygy kernel has been quotiented out.

Arithmetic Selmer functionals cannot detect nonzero relation syzygies.

## Next recommended block

Formalize a syzygy-corrected Taylor–Wiles interface:

```text
one-prime detection on intrinsic cotangent H1 / Selmer
  → finite auxiliary selection
  → induced completion of a presentation after redundant relations are removed.
```

In parallel, the decisive arithmetic theorem remains construction of

```text
cotangent H1 of the actual relative deformation/Hecke presentation
  ≃ transverse dual Selmer.
```

## Replay

```bash
python3 verify.py \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```
