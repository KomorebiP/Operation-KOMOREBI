# Arithmetic Becomes Interference

A worked example accompanying *Mathematics Between Minds* by Komorebi P.
Edition: 2026-09-21.

## Read

`Arithmetic_Becomes_Interference_Worked_Example.pdf` is the seven-page, eight-step development. The editable DOCX and `Worked_Example.md` contain the same example. The complete revised philosophical essay is delivered separately.

The example derives the chain

coprime residues modulo 12 -> Ramanujan signal -> exact rational Fourier projector -> normalized quantum state and measurement.

The mathematical connection to the Komorebi corpus is the specialization of Proposition 21.11 in *Stratified Universality for Resolved Representations*, v1.16.0, Block 16. Boundary 21.12 distinguishes cyclic-character projectors from coefficient-residue selectors. The cited manuscript is not included in this bundle. Classical public sources are listed in the worked example.

## Reproduce the checks

From this folder, run:

```sh
python verify_bridge.py --output verification.json
```

The exact portion uses the Python standard library and requires Python 3.10 or later. It checks 3,003 exact assertions with integers, rational numbers, and the ring Z[z]/(z^4-z^2+1). The optional NumPy portion reports floating-point checks in a separate `numerical_checks` object. Missing NumPy skips that numerical portion rather than declaring it verified.

Expected exact result: PASS, with signal

```text
[4, 0, 2, 0, -2, 0, -4, 0, -2, 0, 2, 0]
```

The classical test signal splits into orthogonal components with squared energies 48 and 102, summing to 150. The normalized quantum signal decodes to amplitudes 1/2 on 1, 5, 7, 11. A distinct preparation with absolute-value amplitudes has the same sample-basis probabilities but zero inverse-Fourier probability on all four coprime labels.

## Reproduce the figure

With NumPy and Matplotlib installed, run:

```sh
python make_figure.py
```

The script reads `verification.json` and produces PNG, SVG, and PDF versions of one discrete-amplitude plot. Its two series use different coordinate bases. They are amplitudes, not simulated measurement outcomes. No plotting colors are prescribed; Matplotlib uses its default cycle.

## Evidence and scope

The finite exact checks are implementation evidence, not a replacement for the algebraic proofs in the text. Floating-point residuals are not exact zero certificates. This edition did not run Lean, synthesize a quantum circuit, or execute quantum hardware. The 12-dimensional Fourier operator is not the 16-dimensional four-qubit QFT. No speedup or new arithmetic identity is claimed.

`verification.json` records the checks. `build_record.json` records source lineage and recovered development errors. `QA.json` records document-layout checks. `environment.json` records the package versions used. `SHA256SUMS.txt` covers the bundle's other files.
