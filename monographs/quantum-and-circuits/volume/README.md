# Quantum and Circuits: book sources

The current reading edition is `output/Realization_Calculus_Quantum_and_Circuits.pdf`.

To compile the self-contained reading source, run from this directory:

    xelatex -interaction=nonstopmode -halt-on-error -output-directory=output volume.tex
    xelatex -interaction=nonstopmode -halt-on-error -output-directory=output volume.tex

The build uses XeLaTeX, bundled P052 serif and Nimbus Sans text fonts, DejaVu Sans Mono, the existing Latin Modern mathematical fonts, and standard TeX Live packages. The URW font license and font exception are included in `fonts/COPYRIGHT.txt`. All scientific figure PDFs are in `assets/`. The generated chapter sources are in `generated/`. No remote content is fetched during compilation.

To regenerate those chapters from the four component source trees included as the sibling `sources/` directory, run `python3 build_volume.py`. This reads the latest component files, copies figures, separates the mathematical treatments from the technical companions, namespaces references, assembles the collected bibliography, and updates the verification statements from the supplied sibling `verification/` receipts. `source_manifest.json` records the exact source hashes.

`check_content.py` verifies preservation of all explicitly delimited LaTeX statement and proof blocks, plus the twenty arithmetic proofs. It normalizes only reference namespaces, whitespace, and copied asset paths. It does not verify mathematical validity or cover prose outside those explicit blocks. `qa/content_preservation.json` contains the result.

`qa_volume.py` renders every final PDF page and checks text bounds and critical compilation diagnostics. Visual review and mathematical review remain distinct checks.

The mathematical scope and open obligations are stated within the volume. Successful Lean replays cover the indexed arithmetic and circuit modules, not every theorem in the book. Original historical failures remain preserved with the source components and are not described as fresh passes.

The nested-model figure is redrawn by `make_reading_figures.py` as a precise generic restricted/ambient comparison. It replaces an inherited figure with overlapping labels and an ambiguous family-inclusion chain. The caption explicitly requires each concrete gate family to supply its own inclusion and cost model.

The professional monograph presentation is centralized in `monograph_style.tex` and the cover/part calls in `volume.tex`. It follows the Komorebi Physics publication style: navy cover, serif typography, teal labels, gold rules, and part reading maps. The mathematical source and verification text remain unchanged. The first explicit page break in each visual chapter is suppressed locally so the chapter title and first section share a page.
