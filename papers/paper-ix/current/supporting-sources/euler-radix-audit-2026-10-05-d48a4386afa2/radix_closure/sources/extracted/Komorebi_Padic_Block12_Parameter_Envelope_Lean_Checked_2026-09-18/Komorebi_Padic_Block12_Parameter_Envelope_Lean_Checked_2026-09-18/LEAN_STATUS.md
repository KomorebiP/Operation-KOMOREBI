# Lean status

```text
Lean             4.34.0-rc2
Lean commit      6a10ac8c22beadecabdbb0919c2b50214762f91d
Lake             5.0.0-src+6a10ac8
mathlib          aeb72f1e9981b6d35b426b16dca7759be3e7ba06
clean build      PASS, 1162 jobs, warning-as-error
production files 19
kernel theorems  179
compiled objects 19 .olean + 19 .ilean
```

No production source contains `sorry`, `admit`, or a project-local `axiom`.
The axiom audit reports only `propext`, `Quot.sound`, and `Classical.choice`.
