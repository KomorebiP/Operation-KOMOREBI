# OpenQASM witness circuits

These OpenQASM 3 files encode the exact gate words displayed in the Clifford chapters and frozen atlas result.

The census state space is the binary symplectic Clifford group **modulo global phase and Pauli translations**. Therefore a restricted and ambient pair has the same symplectic action in the declared model, but the files should not be interpreted as a claim of literal unitary equality without also resolving the ignored Pauli and phase data.

Regenerate the files from the repository root with:

```bash
cd code
PYTHONPATH=. python scripts/export_qasm_examples.py
```
