# Projector-Resolved Prime-Contact Coherence Calculus

## Verified final source

**Subtitle:** Sparse Additive Relations, Prime-Power Contact, and Adelic Coherence  
**Author:** Komorebi P.

This directory contains the standalone LaTeX source and the complete internal verification record for the final paper.

The paper distinguishes exact theorems, exact finite computations, structural limitations, conjectural constructions, and conditional implications. It does **not** claim a proof of the `abc` conjecture.

## Rebuild

### PowerShell

```powershell
.\Rebuild.ps1
```

### POSIX shell

```bash
./rebuild.sh
```

The expected result is a 142-page PDF with no LaTeX layout warnings.

## Verification directory

The `verification` directory contains:

- exact theorem-audit scripts and result ledgers
- exact implementation tests
- the complete 361-row coherence rerun summary
- source-language, claim-language, and PDF-layout audits
- PDF preflight, font, and rendering records
- the exact reference implementations and corpus used for the audit

These checks are an extensive internal audit. They are not a substitute for independent peer review.
