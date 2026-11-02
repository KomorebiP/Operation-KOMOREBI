# Three ways into Komorebi

[Project overview](START_HERE.md) · [Project map](PROJECT_MAP.md) · [All hand-worked examples](HAND_WORKED_EXAMPLES.md)

These three demonstrations connect a concrete question to a hand calculation,
a short program and the relevant mathematical sources. Start with any one.
They use elementary finite constructions to introduce the collection's language.
The calculations are not claims of mathematical novelty.

| Question | Demonstration | What you can inspect |
|---|---|---|
| Can an operation be rebuilt from its action between parts? | [Reconstruct an operator](demonstrations/PACKETS.md) | Four blocks give the same answer as one matrix multiplication. |
| Does a finer description preserve the signal? | [Refine a signal](demonstrations/REFINEMENT.md) | Two and four address classes reconstruct the same list. Dropping a class leaves an explicit residual. |
| Does a summary contain enough information for a question? | [Test recovery from a summary](demonstrations/RECOVERY.md) | Two inputs give the same summary but different requested answers. A compatible question has an exact recovery rule. |

Each page gives the inputs, intermediate steps, expected output, a control that
exposes a limitation, and links to papers, proofs, Lean coverage and code.
The [project map](PROJECT_MAP.md) places these introductory examples in the
wider collection.

## An extended derivation with Euler numbers

[Euler numbers through packets, polynomials, and residuals](demonstrations/EULER_PACKETS.md)
follows one calculation through reciprocal series, a residue-packet matrix,
quartic sequence reconstruction, parameter polynomials, exact residual repair,
and finite-difference refinement. It includes the full hand calculations, failure
witnesses, and a standalone exact Python checker with downloadable tables.

## An extended derivation with factorial lanes

[Factorial lanes: one residue section through exact transfer](demonstrations/FACTORIAL_LANES.md)
starts with the degree-4 packet of the exponential. It reconstructs 34! from
ten step-factorial lanes, converts those lanes to a hypergeometric series,
normalizes the denominator, and inverts the packet in two equivalent
coordinate systems. It also proves a sharpened 5-adic displacement bound,
refines the residue packet into two and five children, and distinguishes the
congruential transfer row from the classical Euler numbers. A standalone
checker supplies exact rational results, downloadable code and two explicit
failure witnesses.

## An extended derivation with wavelets and polyphase transfer

[Wavelets and polyphase transfer: one signal through the whole calculus](demonstrations/WAVELET_POLYPHASE.md)
follows a sixteen-sample signal through even/odd phases, four Haar levels,
predict–update lifting, weighted coefficient selection, and exact residual
repair. It transports a three-tap FIR filter through polyphase
coordinates and all four Haar levels, derives a sharp finite stability
certificate, and proves the exact error from omitted cross-channel transfers.
The full 16×16 matrix displays inter-scale coupling, while two noncommuting
operation orders and explicit boundary repairs provide independent failure
witnesses. Reproducible tables and Python-generated figures complete the example.

## An extended derivation with Stirling, Bell and Fubini numbers

[From set partitions to exact transfer](demonstrations/STIRLING_BELL_FUBINI.md)
starts with one Stirling-number row, constructs Bell and ordered Bell numbers,
and then exposes the inverse triangular kernel. It independently derives the
exponential generating functions and their formal inverse, interprets Bell as
a Touchard evaluation and Fubini as a gamma or geometric moment, then builds
full residue transfer systems. Exact interpolation recovers a complete
parameterized polynomial, while two scalar summaries do not determine an
arbitrary coordinate profile. Every example has exact Python
checks, source-bound tables and a Python-generated diagram.

## An extended derivation with roots of unity and falling factorials

[Roots of unity, projectors, and falling-factorial coordinates](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md)
starts with the Stirling expansion of a fifth power, constructs exact
roots-of-unity residue filters, and transports the projectors through a
Newton/falling-factorial change of basis. The three packets yield
600+244+180=1024. The same page proves finite-difference and multiplication
transfer rules, tests six-way refinement, and shows why filtering ordinary
monomial degrees is the wrong operation after a coordinate change.
The independently enumerated functions from five inputs to four labels
explain exactly what those residue packets count. A rational spectral formula
for the projectors and an all-degree generating-function bridge add two
more exact routes to the same identities. Translation by one is then carried
through a complete cyclic transfer matrix, with a concrete noncommutation
witness and an integral characteristic-three spectral obstruction. The
standalone checker and source-bound CSV/SVG records support the hand
derivation. These are classical identities presented as one continuous
realization argument, not a new theorem claim.

## An extended derivation with quantum phase and measurement

[Quantum phase, measurement, and information loss](demonstrations/QUANTUM_PHASE_MEASUREMENT.md)
follows one qubit through three measurement settings, exact tomography,
partial dephasing, and a concrete recovery obstruction. A coherent two-qubit
record can be uncomputed, while a classical record loses the relative phase.
Parity packets and their singleton refinement show which coherence a
measurement removes. The page includes three browser experiments, exact
Python matrix calculations, downloadable tables, and a generated figure.
Three further collection examples develop amplitude damping, the Quantum
and Circuits book's modulus-12 Fourier phase separation, and three-qubit
syndrome recovery. The arithmetic browser experiment contrasts signed, unsigned,
and fully dephased arithmetic states.

## Run in your browser

[Open the Signal Laboratory](https://KomorebiP.github.io/Operation-KOMOREBI/signal-lab.html)
for a larger experiment. Generate or import 16–256 integer samples, add seeded
noise, and compare Haar wavelets, orthonormal cosine modes, and sample
coordinates at the same coefficient budget. Compare weighted-energy,
raw-magnitude, and prefix selections; inspect individual components; and
explore reconstruction error over every budget. Export signals or error curves
as CSV, save the experiment as JSON, or copy a link to the complete setup.

Draw your own reference directly on the signal plot, or set a selected sample
precisely with the keyboard. Edits use whole numbers from −64 to 64 and support
undo/redo. Save up to 12 runs in the browser notebook, restore or rename them,
and overlay reconstructions from identical reference and observed data. Notebook
JSON preserves the collection; a results CSV exports its comparison table.

Four starter experiments open paired runs for sharp edges, a cosine-like tone,
detail in noise, and Haar ranking rules. Saved-run comparisons offer
reconstruction, signed-error, and B-minus-A views, with a linked sample
inspector and a jump to the largest absolute difference. Download comparison
CSV for both reconstructions and their signed errors at every address.

Copy a comparison link to share both named runs, the chosen plot view, and the
selected sample. Links open a preview and recompute the results while leaving
the recipient's saved notebook unchanged. The preview can be saved as two new
notebook runs when space is available.

The quality-target finder scans every coefficient budget to find the first
that retains a requested percentage of observed energy or meets a reference
RMS-error limit. Apply a result to the active experiment or save all qualifying
representations as notebook runs. Unreachable limits are reported explicitly.

The reference signal is known in these experiments. The displayed reference
minimum uses that knowledge; it does not estimate the clean signal behind an
unknown real-world recording. Cosine calculations are numerical approximations.

[Explore the interactive diagrams](https://KomorebiP.github.io/Operation-KOMOREBI/interactive.html).
Change matrix entries, keep or omit transfer blocks, refine an eight-sample
signal, and move inputs along a shared-summary line. The controls update the
diagrams and exact whole-number results immediately, without writing code.
Each experiment links back to its hand calculation and sources.

Use **Copy experiment link** to save or share the selected experiment's exact
inputs and packet or coefficient choices. A Haar link also restores the
coefficient and sample address being inspected. Open the link to return to
those settings. If clipboard access is unavailable, select and copy the link
shown below the button.

For a deeper experiment, open the
[16-sample Haar lab](https://KomorebiP.github.io/Operation-KOMOREBI/interactive.html#haar).
Decompose a signal through four levels, choose individual coefficients or a
magnitude cutoff, and inspect the exact reconstruction error and weighted
energy balance. The [multilevel calculation](demonstrations/HAAR_LAB.md)
records the default example and its expected results.

[Open the Python playground](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html).
Choose a demonstration, press Run and compare its output with the hand calculation.
You can edit the code, stop a calculation and reset the original example.
Python loads on the first run. No account or local installation is needed.
The playground also includes a tested introductory Komorebi Math example.

For examples drawn directly from the sequence work, use
[Komorebi sequence shapes](demonstrations/SEQUENCE_SHAPES.md). These presets
plot Paper IV's reciprocal coefficients and factorial normalization, compare
the family in labelled 2D and 3D views, and explore the Special Functions atlas's factorial-weighted
Stirling sums. Each includes exact data downloads and source links.

## Run without installing a library

Use Python 3.10 or later. The program uses only the standard library and exact
integer arithmetic. It does not need internet access or write files.

[Read the complete program on the site](https://KomorebiP.github.io/Operation-KOMOREBI/read/demonstrations.html)
or [download komorebi_demonstrations.py](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/komorebi_demonstrations.py).
Open a terminal in the folder containing the downloaded file and run:

```text
python -B komorebi_demonstrations.py packets
python -B komorebi_demonstrations.py refinement
python -B komorebi_demonstrations.py recovery
```

On Windows, `py -3` can replace `python` if that is how your interpreter is
installed. No package installation or virtual environment is needed for this
program. With no argument, it runs all three demonstrations.

If you already have a collection checkout, run from its root:

```text
git rev-parse HEAD
python -B examples/komorebi_demonstrations.py all
```

Keep that revision with any saved output. The downloadable program's
[source record](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/demonstration-source.json)
gives its collection revision and SHA-256 checksum. The repository also contains
the [program source](../examples/komorebi_demonstrations.py).

## What a passing run establishes

The program checks the displayed fixed matrices, lists and witnesses. Each
demonstration explains the mathematical identity or contradiction behind its
output. Matrix identities can justify statements about every vector in the
specified finite space. Checking a list of sample vectors alone would not do so.

The website workflow runs all three programs and compares their output with the
pages below. It also runs the separate checker for the original hand-worked
examples. These runs do not replay Lean, qualify the production libraries or
prove wider research claims. All software remains beta and work in progress.

## Continue with the libraries

Use [First runs](FIRST_RUN.md) for installation, supported environments and the
introductory Python and C library programs. The demonstrations here are small
standalone teaching programs. The libraries have their own APIs and tests.

[Project overview](START_HERE.md) · [Project map](PROJECT_MAP.md) · [Evidence guide](RECORDS.md)
