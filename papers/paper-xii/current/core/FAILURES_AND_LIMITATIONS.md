# Failures, repairs and limits

## Recovered presentation defects

The October 8 formatting migration expanded the visual guide to 33 pages and separated material that originally belonged to individual lessons. An almost empty page contained only the first lesson's concluding scope box; printed lesson locators no longer described physical pages. This release restores 27 complete lessons plus one cover, with direct source links and V-numbered headings and footers.

The main Artin-packet and companion-spine drawings had arrows passing through neighboring labels. The final architecture drawing did not use the same five gate names as Theorem 12.6. Four diagrams were regenerated with noncrossing routes and explicit input boundaries. Fourteen other main figures remain unchanged.

## Failed build and audit attempts

The first coordinated build exposed an AMS/titlesec contents-list number collision and overfull TOC boxes. The first repair used an undefined dot-separation macro and failed. The final contents configuration defines that macro and restores proper numbered leaders. The Lean contents page initially spilled its final entry onto a nearly empty page; local spacing was repaired and the final guide returned to 31 pages.

The first link pass used a closed target PDF during assembly. Target geometry is now cached before document closure. A subsequent coordinate audit showed that remote PDF XYZ destinations must retain native bottom-left coordinates; converting them as if they were local PyMuPDF coordinates was wrong. That was repaired. The route auditor also initially selected the first of two identical-target aliases and reported a missing route. It now consumes unmatched equivalent route IDs before reusing one. The final check inspects actual PDF destination arrays and target named destinations, not merely a generated route list.

The first new regression run incorrectly assumed every catalogued declaration began on a line containing its name and that a display table was byte-identical despite newly added links. One valid source record starts at a standalone attribute line. The revised checker recognizes standalone attributes and strips only documented link wrappers before comparing the complete table. An intermediate checker repair also incorrectly skipped same-line attributes and used the wrong display macro name. Both were corrected. The production source and catalog records were not changed to make these tests pass. Two failed regression reports are preserved.

The runtime's generic BibTeX launcher failed to execute. A working BibTeX binary was found and recorded. An attempted publisher full-page open returned an access error during bibliography checking; available primary publisher metadata supplied the limited bibliographic information used. No full-paper theorem audit is inferred from metadata.

## Diagnostics that remain

The final monograph has nine underfull-spacing diagnostics, the visual build has two, and the Lean build has one. The two pdfLaTeX builds warn that epstopdf shell escape is disabled; every required figure is already PDF and shell escape stays disabled. No overfull boxes, missing-character diagnostics or unresolved references were found in the final build. A blanket warning-free claim would be false.

## Distribution and verification limits

Nine standalone font files were intentionally removed from the recovered predecessor copy. Their hashes and the unchanged retained files are documented. Fonts remain local build dependencies. No standalone font file is redistributed, including inside nested archives.

No fresh Lean/Lake process was run. Both historical compiler records were authenticated by source, object and log consistency checks. The historical negative controls were not newly compiled. The fresh finite programs are bounded examples and implementation checks, not proofs of universal automorphy or companion existence. No external peer review occurred. Only selected bibliography metadata were freshly checked, not all 27 works or all their theorem applications.

The isolated three-PDF rebuild passed strict binary, extracted-text and rendered-pixel comparison in the checked environment. That result is not a cross-platform guarantee. Final archive-specific extraction, replay and build receipts are distributed separately to avoid a circular archive hash.
