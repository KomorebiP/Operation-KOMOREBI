# Notation index

[Open the notation index](https://komorebip.github.io/Operation-KOMOREBI/notation.html) · [Glossary](GLOSSARY.md) · [Browse works](BROWSE.md) · [Worked examples](HAND_WORKED_EXAMPLES.md)

The notation index gathers mathematical symbols from the selected reading sources. Search by symbol, TeX spelling, symbol name or words from a source excerpt. Choose a work when a letter has several meanings. Exact TeX matching preserves case and distinguishes spellings that look similar in plain text.

Each entry provides the original spelling, a source excerpt and links to its mathematical passages. The work navigation connects it to the paper, claims, written proofs, Lean, code and worked examples. Links to Lean or code retain the work's existing scope and status.

## How to read an entry

The index keeps meanings local to each work. A base symbol and its forms with subscripts or superscripts have separate entries. Repeated uses retain their source locations, including different contexts within the same paper.

Passages are classified from their surrounding source structure:

| Label | What it tells you |
|---|---|
| Notation table | The passage occurs in a table with a symbol and meaning header. |
| Definition passage | The passage occurs within a written definition environment. |
| Introduction passage | Nearby prose uses wording such as “denotes” or “we define”. |
| Use in source | The symbol occurs in a mathematical passage. No definition is inferred. |

A definition passage can mention several symbols while defining only one. Read the linked source before assigning a meaning. Search aliases and readable previews are aids. Exact TeX and the original passage remain available.

## Coverage

Every work in the reader catalogue has a notation page. The twelve core papers are included. Each page lists the source files scanned and the number of detected mathematical passages. A work with no detected notation is shown explicitly, with links to its reading files.

The scan covers TeX and Markdown mathematical delimiters, common equation environments and mathematical code fences. It skips ordinary program listings, comments and TeX preambles. Additional manuscript entrypoints are declared in [the source selection](../manifests/notation-sources.json). Their literal includes are followed using the existing source receipts.

This is an occurrence index of the selected reading sources. It does not claim that every symbol has a reviewed definition. Notation in PDFs, images, diagrams, unusual TeX syntax or prose outside mathematical delimiters still needs a manual pass. Historical archives and program identifiers are outside the scan. The live coverage section and each work's source list make these limits visible.

## Reproducibility

The index is rebuilt with the reader site from the same pinned collection revision. Each source is checked against its receipt before indexing. Downloadable JSON records retain source hashes, exact mathematical passages, source positions and every detected symbol occurrence. Entry links use hashes of exact spellings so that inserting another entry does not renumber existing symbols.

The site checks verify source identities, recorded positions, coverage totals, entry links and links back to the reader. Parser tests cover comments, code fences, decorated symbols, case distinctions and conservative macro display. These checks do not review proofs or change any completion, Lean or confidence assessment.
