# Complete reader navigation and preservation QA

Generated: 2026-10-07T17:01:09.329739+00:00. pypdf: 6.10.0.

The complete reader contains the 38-page consolidated manuscript and all eight preserved source papers, for 469 physical pages.

The source PDFs reuse hyperref destination names, including `chapter.1` and `Doc-Start`. Before merging, the script assigns a separate namespace to every input and updates its local actions and outline references. This prevents a later paper’s contents link from resolving to an earlier paper.

| Input | Pages checked | Local annotation links checked | Named destinations checked |
|---|---:|---:|---:|
| consolidated | 38 | 46 | 117 |
| paper_I | 60 | 104 | 1269 |
| paper_II | 50 | 79 | 1105 |
| paper_III | 38 | 80 | 150 |
| paper_IV | 55 | 89 | 1247 |
| paper_V | 52 | 89 | 1115 |
| paper_VI | 54 | 86 | 1199 |
| paper_VII | 60 | 96 | 1309 |
| paper_VIII | 62 | 96 | 1553 |

All 469 page decoded-content hashes, media boxes, crop boxes and rotations match their inputs. All 765 internal annotation links preserve their target page and view arguments. All 9064 names preserve their target page and view arguments.

All 289 imported outline entries preserve their title, target page, view arguments and hierarchy. The 9 added part bookmarks point to the correct starts.

Input manuscript and archive SHA256 values are unchanged before and after the build. No source files were modified. Only imported navigation names and references were changed in memory.

This is structural and navigation QA. The consolidated manuscript’s visual QA is reported separately. Full hashes and exact counts appear in `reader_navigation_validation.json`.
