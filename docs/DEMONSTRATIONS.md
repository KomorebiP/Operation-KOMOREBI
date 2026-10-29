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
