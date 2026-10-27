# Remaining bibliography metadata review

## Scope and result

Reviewed 2026-10-18T18:28:28.825679+00:00. Source: `publication/source/traditional/Paper_XI_Traditional_Final.bib`; SHA-256 `64c6fc745198b480b7e4950d6f5daf3a0eb36ba136ae65468ed070589e23c8b8`.

The active bibliography has 29 entries. The 12 selected records in `evidence/block07/BIBLIOGRAPHY_AUDIT.md` were not re-audited here; the new `HenniartLemaire2011` record was separately checked by the parent against Numdam/publisher metadata. This pass examines the other 16 original entries.

**Result:** no remaining definite wrong author, work, original year, volume, or page range was found. Fifteen records now have primary publisher, author-archive, or publisher-deposited evidence for their core identity. `Karpilovsky1985` remains corroborated by independent institutional/archival catalogs and a contemporary published review, with original publisher front matter unavailable. Several individual fields have narrower evidence, explicitly recorded below. This is not a certification that every field of all 29 entries was independently read in a primary original edition.

This pass checks bibliography metadata only. It does not audit an external theorem, its hypotheses, or the correctness of a manuscript application. It changes no mathematical claim or proof status. No external source PDF is included in the release.

## Source-backed corrections

| Entries | Finding | Source resolution |
|---|---|---|
| `Serre1977`, `Serre1967` | Author given name was Jean Pierre; publisher and author records use Jean-Pierre. | resolved |
| `Henniart1993` | Exact publisher title uses Greek epsilon. | resolved |
| `Tate1979` | L-Functions title hyphen and Part 2 locator must appear in the rendered citation; part field was ignored by the active bibliography style. | resolved |

The parent also protected proper names, GL notation, and Roman part numbers against BibTeX case conversion. Final rendering of the corrected bibliography belongs to the parent’s final monograph build; the pre-fix `.bbl` was inspected to diagnose the missing Tate part locator.

## Record-by-record evidence

### 1. `HarrisTaylor2001`

Michael Harris and Richard Taylor; The geometry and cohomology of some simple Shimura varieties; Annals of Mathematics Studies 151; Princeton University Press; 2001.

**Evidence:** [publisher hosted book record](https://www.jstor.org/stable/j.ctt1287kfd) (opened).

The publisher record credits Vladimir G. Berkovich for an appendix; he is not an omitted coauthor. A later digital format does not change the 2001 original year. No total-page field is present in the bibliography.

### 2. `BushnellHenniart2006`

Colin J. Bushnell and Guy Henniart; The Local Langlands Conjecture for GL(2); Grundlehren der mathematischen Wissenschaften 335; Springer Berlin Heidelberg; 2006.

**Evidence:** [publisher book record](https://link.springer.com/book/10.1007/3-540-31511-X) (opened).

**DOI checked:** `10.1007/3-540-31511-X`.

The original hardback and copyright year is 2006. The later softcover date is not a replacement for that year.

### 3. `Henniart1993`

Guy Henniart; Caractérisation de la correspondance de Langlands locale par les facteurs ε de paires; Inventiones Mathematicae 113 (1993), 339–350.

**Evidence:** [publisher article record](https://link.springer.com/article/10.1007/BF01244309) (opened).

**DOI checked:** `10.1007/BF01244309`.

The publisher title uses Greek epsilon. The staging source now uses {$\varepsilon$}; resolved. The opened publisher landing record did not display issue 2. The inherited issue field was not independently certified from that page.

### 4. `BushnellKutzko1993`

Colin J. Bushnell and Philip C. Kutzko; The Admissible Dual of GL(N) via Compact Open Subgroups; Annals of Mathematics Studies 129; Princeton University Press; 1993.

**Evidence:** [publisher hosted book record](https://www.jstor.org/stable/j.ctt1b9s03n) (opened).

The publisher-hosted book identifies the original 1993 work. Digital-edition identifiers and page counts were not substituted for the original edition.

### 5. `Prasad2009`

Amritanshu Prasad; On character values and decomposition of the Weil representation associated to a finite abelian group; The Journal of Analysis 17 (2009), 73–85.

**Evidence:** [author deposited archive record](https://arxiv.org/abs/0903.1486v1) (opened; Journal reference field; v1 submitted 9 March 2009).

The journal, volume, year, and full page range are explicitly supplied in the author-deposited journal-reference field. This is not a fresh inspection of the final journal PDF. 10.48550/arXiv.0903.1486 identifies the preprint; it is not a verified journal DOI.

### 6. `Karpilovsky1985`

Independent library catalogs corroborate Gregory Karpilovsky; Projective Representations of Finite Groups; Monographs and Textbooks in Pure and Applied Mathematics 94; Marcel Dekker; New York; 1985.

**Evidence:** [institutional library catalog](https://library.imsc.res.in/bib/5552) (opened); [digitized book catalog](https://books.google.com/books?id=K-nuAAAAMAAJ) (opened; University of Michigan copy; catalog metadata, not inspected original front matter); [archival catalog api](https://archive.org/metadata/projectiverepres0000karp) (public metadata retrieved); [contemporary book review metadata](https://doi.org/10.1017/S0025557200139440) (opened; The Mathematical Gazette 70 (453), October 1986, p.248; review DOI, not book DOI).

No original publisher front matter or author-controlled record was successfully retrieved. This record is not labeled freshly primary-book-verified. The Cambridge-hosted contemporary review corroborates title, author initials, 1985, Marcel Dekker, and ISBN 0-8247-7313-6; it is secondary evidence for the book. Its stated total-page count differs from library catalogs, but no total-page field is present in the bibliography. The Internet Archive copy is access restricted. Only public catalog metadata was read; no restricted book images were requested. No book DOI was established.

### 7. `GurevichHadani2007`

Shamgar Gurevich and Ronny Hadani; The geometric Weil representation; Selecta Mathematica 13 (3) (2007), 465–481; exact full citation on author publication list.

**Evidence:** [author publication list](https://people.math.wisc.edu/~sgurevich/papers-shamgar.html) (opened; Entry 24); [author hosted publisher proof](https://people.math.wisc.edu/~sgurevich/Selecta.pdf) (search-indexed publisher header; OnlineFirst; copyright 2007 Birkhäuser; matching DOI); [publisher article record](https://link.springer.com/article/10.1007/s00029-007-0047-3) (opened).

**DOI checked:** `10.1007/s00029-007-0047-3`.

Retain 2007. The author explicitly cites Selecta Mathematica (2007), volume 13, number 3, pages 465–481; the publisher proof also bears copyright 2007. The current Springer page gives online publication 15 December 2007 but its generated citation box displays 2008. This is a recorded metadata variant, not an unnoticed inconsistency or a reason to silently replace the author-cited year.

### 8. `MilnorHusemoller1973`

John Milnor and Dale Husemoller; Symmetric Bilinear Forms; Ergebnisse der Mathematik und ihrer Grenzgebiete, volume 73; Springer Berlin Heidelberg; 1973.

**Evidence:** [publisher book record](https://link.springer.com/book/10.1007/978-3-642-88330-9) (opened).

**DOI checked:** `10.1007/978-3-642-88330-9`.

The publisher expands the series name with “2. Folge”; the shorter series form in the bibliography still identifies the same volume. The 2013 eBook and 2014 reprint dates do not replace the original 1973 copyright year.

### 9. `Serre1977`

Jean-Pierre Serre; Linear Representations of Finite Groups; Graduate Texts in Mathematics 42; Springer New York; 1977.

**Evidence:** [publisher book record](https://link.springer.com/book/10.1007/978-1-4684-9458-7) (opened).

**DOI checked:** `10.1007/978-1-4684-9458-7`.

The publisher uses Jean-Pierre. Both Serre author fields are corrected to that hyphenated form in the staging source; resolved.

### 10. `Serre1967`

Jean-Pierre Serre; Local Class Field Theory; chapter VI in Algebraic Number Theory, edited by Cassels and Fröhlich; Academic Press; 1967. The author’s institutional annual report explicitly lists this publication.

**Evidence:** [author institutional publication report](https://www.college-de-france.fr/sites/default/files/media/document/2023-03/1967-1968_serre.pdf) (opened; PDF page 4, printed page 50, Publications); [current rightsholder book record](https://www.lms.ac.uk/publications/algebraic-number-theory) (opened; Editors; first printed 1967; subsequent LMS reprint distinguished); [secondary author course bibliography](https://www.jmilne.org/math/CourseNotes/CFT.pdf) (search-indexed bibliography; Serre1967 reference corroborates 128–161).

The exact original chapter range 128–161 remains corroborated by secondary mathematical bibliographies, rather than newly checked against original chapter pages. The author report cites the Academic Press New York imprint; the bibliography retains London, a conventional citation of the same Academic Press edition. Exact original imprint front matter was not inspected. The DOI 10.1007/978-3-642-37726-6_75 is a later Collected Papers reprint at pages 421–454, not an original 1967 chapter DOI. It was not substituted.

### 11. `Tate1979`

J. Tate; Number theoretic background; Automorphic Forms, Representations and L-Functions; Proceedings of Symposia in Pure Mathematics 33, Part 2; American Mathematical Society; 1979; 3–26; editors A. Borel and W. Casselman.

**Evidence:** [publisher deposited crossref record](https://api.crossref.org/works/10.1090/pspum/033.2/546607) (public JSON retrieved); [publisher original book advertisement](https://www.ams.org/journals/notices/198202/198202FullIssue.pdf) (search-indexed publisher page; Printed page 201: editors, volume 33, parts 1/2, original publication 30 June 1979); [publisher book author index](https://www.ams.org/books/pspum/033.2/pspum033.2-endmatter.pdf) (search-indexed publisher PDF; Tate entry, Part 2, p.3).

**DOI checked:** `10.1090/pspum/033.2/546607`.

The original bibliography style ignores the separate part field. The reviewed pre-fix .bbl printed volume 33 without Part 2 and used “L Functions”. A source-backed patch to put “L-Functions, Part 2” in booktitle was sent to the parent before source edits. Its current source resolution is recorded separately below. Crossref supplies the full page range 3–26 and the publisher supplies the original edition and editors.

### 12. `DavenportHasse1935`

H. Davenport and H. Hasse, in that order; Die Nullstellen der Kongruenzzetafunktionen in gewissen zyklischen Fällen; Journal für die reine und angewandte Mathematik 172 (1935), 151–182.

**Evidence:** [publisher deposited crossref record](https://api.crossref.org/works/10.1515/crll.1935.172.151) (public JSON retrieved).

**DOI checked:** `10.1515/crll.1935.172.151`.

The historical de Gruyter deposit encodes 1935 in the volume field and 172 in the issue field; the conventional journal citation is volume 172 (1935). Do not rewrite the bibliography to reproduce that legacy schema. The online date in 2009 is digitization/publication metadata, not the original year. The deposit gives author initials; expanded first names were not separately authenticated in this pass.

### 13. `BerndtEvansWilliams1998`

Bruce C. Berndt, Ronald J. Evans, and Kenneth S. Williams; Gauss and Jacobi Sums; Wiley; June 1998; ISBN 9780471128076.

**Evidence:** [publisher book record](https://uat.store.wiley.com/en-us/gauss-and-jacobi-sums-p-9780471128076) (search-indexed metadata; direct page returned 403).

The indexed official Wiley product record supplies title, full authors, publisher, and year. Direct access to both the indexed and canonical Wiley product pages returned 403. The current product series label differs in wording from the original Canadian Mathematical Society series label retained in the bibliography. Original front matter was not inspected to re-certify the full series wording or city. 10.2307/3619097 belongs to a review, not this book; no book DOI was established or added.

### 14. `Mackey1952`

George W. Mackey; Induced Representations of Locally Compact Groups I; Annals of Mathematics 55 (1), January 1952; first page 101.

**Evidence:** [publisher deposited crossref record](https://api.crossref.org/works/10.2307/1969423) (public JSON retrieved); [secondary contemporary bibliography](https://www.numdam.org/item/SB_1951-1954__2__185_0/) (search-indexed journal archive; Reference 3 explicitly gives 101–139).

**DOI checked:** `10.2307/1969423`.

The JSTOR-deposited Crossref record supplies only first page 101. The inherited endpoint 139 is corroborated by the contemporary Numdam-hosted bibliography, not newly read from Mackey’s original final page. The public JSTOR landing and citation-export requests returned a minimal script page without usable citation data. No restricted article access was attempted.

### 15. `Isaacs1976`

I. Martin Isaacs; Character Theory of Finite Groups; originally New York: Academic Press, 1976.

**Evidence:** [publisher reprint original edition statement](https://www.ams.org/books/chel/359/chel359-endmatter.pdf) (search-indexed publisher copyright/CIP text; direct page returned 403); [publisher reprint catalog](https://doi.org/10.1090/chel/359) (search-indexed publisher metadata).

The AMS copyright/CIP statement explicitly identifies the original 1976 Academic Press edition, in Pure and Applied Mathematics 69. The existing shorter entry is consistent. 10.1090/chel/359 identifies the later AMS Chelsea reprint. It was not attached silently to the 1976 Academic Press citation.

### 16. `Brown1982`

Kenneth S. Brown; Cohomology of Groups; Graduate Texts in Mathematics 87; Springer New York; 1982.

**Evidence:** [publisher book record](https://link.springer.com/book/10.1007/978-1-4684-9327-6) (opened).

**DOI checked:** `10.1007/978-1-4684-9327-6`.

The original copyright year is 1982. The later eBook date does not replace it.

## Limits and DOI handling

The bounded search is complete for all 16 requested records. The original Karpilovsky front matter, original Serre chapter pagination, Mackey’s final-page image, Henniart’s issue number, and some original book series/imprint details were not freshly read from primary originals. These limits are retained rather than erased by secondary corroboration. Gurevich–Hadani’s 2007/2008 publisher-date variant is explicitly reconciled in favor of the author’s 2007 citation.

Nine same-work DOIs were verified as metadata identifiers in this pass. Their absence from the current bibliography is not a metadata error, and this review did not add them. The Prasad arXiv identifier, Serre Collected Papers DOI, Isaacs AMS reprint DOI, and Cambridge review DOIs must not be confused with original-journal or original-edition DOIs.

The companion JSON gives machine-readable source classes, access methods, limitations, correction states, and the exact bibliography hash. Public read-only requests were used. Direct-access failures did not authorize access-control bypass; search-indexed official records are identified as such.
