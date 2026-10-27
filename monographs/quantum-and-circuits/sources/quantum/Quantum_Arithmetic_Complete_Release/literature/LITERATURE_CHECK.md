# Bounded attribution check: Quantum–Arithmetic Bridge

Checked 2026-10-07 UTC (publication work begun 2026-10-06 America/Chicago).

## Question and scope

This check authenticates the classical ancestry of the Ramanujan sum, the primitive-frequency subspace, and the orthogonal decomposition indexed by divisors of a finite record length. It is an attribution and notation-translation check. It is not a novelty search, a physics validation, or a replacement for the self-contained proofs in this release.

The project uses a positive-sign, unitary Fourier synthesis matrix
\(F_{nk}=N^{-1/2}\exp(2\pi i nk/N)\), with indices \(0\le n,k<N\). Its primitive projector is \(P_{nm}=c_N(n-m)/N\). For \(d\mid N\), the divisor-shell kernel is \(P^{(d)}_{nm}=c_d(n-m)/N\). These dimensions, coefficients, and normalizations must not be inferred from a citation without the translation below.

Project-local lookup preceded external discovery. The supplied `Worked_Example.md` already cites NIST DLMF §27.10, the Caltech Ramanujan Periodicity Project, and an internal manuscript proposition. No authorized local copy of Ramanujan's original article or either 2014 Vaidyanathan journal article was found among the input files. The internal manuscript was acquired and checked separately by the release coordinator. This literature agent did not independently authenticate its proposition numbering.

The coordinator reports that the source is *Komorebi Stratified Universality Foundations v1.16.0, Block 16*: Proposition 21.11 at printed p. 189 (physical PDF p. 197), followed by Boundary 21.12 at printed p. 190 (physical PDF p. 198). Its local copy is `downloads/lineage/Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.pdf`; text extracts are in `provenance/`. This internal lineage citation must not be silently relabeled as the later final edition. The historical source and the new self-contained proof have different evidentiary roles.

## Source records

### Ramanujan1918

- **Author and title:** S. Ramanujan, *On certain trigonometrical sums and their applications in the theory of numbers*.
- **Published record:** *Transactions of the Cambridge Philosophical Society* **22**, no. 13 (1918), 259–276.
- **Original-paper scan locator:** <https://www.imsc.res.in/~rao/ramanujan/CamUnivCpapers/Cpaper21/page1.htm>.
- **Readable primary-text transcription:** <https://ramanujan.sirinudi.org/Volumes/published/ram21.pdf>. This is a hosted transcription, not an authenticated publisher facsimile. It was inspected at PDF pages 1–3, §§1–2, especially equations (2.3), (2.5), (2.6), and (2.7).
- **Checked result:** the primitive-root definition and divisor inversion giving the integer formula for \(c_s(n)\).
- **Authentication boundary:** the article identification and year agree across the transcription and Vaidyanathan's author-hosted bibliography. The IMSc index prints 269–276, apparently inconsistent with 259–276 in those two sources. We record the discrepancy rather than treat the index alone as pagination evidence. No DOI was authenticated.
- **Extraction status:** primary-text transcription inspected; scan landing page reached, scan image not extracted. No external PDF redistributed in this release.
- **Translation:** the source's \(s\) is the project's modulus \(N\). Its cosine sum equals the complex character sum because the reduced residues pair under negation. Its \(\eta_d(n)\) is \(d\) when \(d\mid n\), otherwise zero. Thus (2.7) yields \(c_N(n)=\sum_{d\mid\gcd(N,n)}d\mu(N/d)\).
- **Classification:** classical identity, known after notation translation. It is not attributed as a Komorebi discovery.

### Vaidyanathan2014FIR

- **Author and title:** P. P. Vaidyanathan, *Ramanujan-sum expansions for finite duration (FIR) sequences*.
- **Published record:** 2014 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), 4933–4937.
- **DOI:** <https://doi.org/10.1109/ICASSP.2014.6854540>.
- **Author-hosted text:** <https://systems.caltech.edu/dsp/PPVSquare.pdf>.
- **Official metadata:** <https://authors.library.caltech.edu/records/k3xw5-byr96>.
- **Checked locations:** PDF p. 1, equation (1) and the following DFT discussion; PDF p. 2, integer divisor formula and equation (5); PDF p. 3, §4 and Theorems 1–2; PDF p. 4, periodicity discussion.
- **Checked result:** primitive DFT support, orthogonal divisor subspaces, a full integer basis from shifted Ramanujan sums, and decomposition into their orthogonal projections.
- **Boundary:** the source's named \(F_N\) is a composite integer basis matrix, not this project's normalized Fourier matrix \(F\). Do not identify these symbols. The source's introductory comment about Zhang and the twin-prime conjecture is incorrect and is not used here. Its finite-dimensional Fourier proof is checked independently.
- **Classification:** the divisor-shell decomposition is known after translation. The displayed normalized circulant formula in this release follows directly from the same Fourier subspaces; it is not a new periodicity transform.

### Vaidyanathan2014I

- **Author and title:** P. P. Vaidyanathan, *Ramanujan Sums in the Context of Signal Processing—Part I: Fundamentals*.
- **Published record:** *IEEE Transactions on Signal Processing* **62**(16) (2014), 4145–4157.
- **DOI:** <https://doi.org/10.1109/TSP.2014.2331617>.
- **Official record:** <https://authors.library.caltech.edu/records/3c8eh-xc275>.
- **Checked boundary:** publication metadata and author-supplied abstract authenticated. The record is explicitly metadata-only. The full journal article was not obtained, so no journal theorem or equation number is represented as checked.
- **Attribution supported:** the established Ramanujan-subspace program, cyclic-shift integer bases, and projection methods. Detailed proof checking above uses the accessible author-hosted conference text instead.

### Vaidyanathan2014II

- **Author and title:** P. P. Vaidyanathan, *Ramanujan Sums in the Context of Signal Processing—Part II: FIR Representations and Applications*.
- **Published record:** *IEEE Transactions on Signal Processing* **62**(16) (2014), 4158–4172.
- **DOI:** <https://doi.org/10.1109/TSP.2014.2331624>.
- **Official record:** <https://authors.library.caltech.edu/records/7s1wb-ghg80>.
- **Checked boundary:** publication metadata and author-supplied abstract authenticated. The record is explicitly metadata-only. No precise journal equation number or uninspected proof is cited.
- **Attribution supported:** the published FIR decomposition into pairwise orthogonal divisor-indexed Ramanujan components and integer matrices up to an overall scale. The normalized formulas in this release are proved directly.

## Normalization and hypothesis translation

The accessible conference source uses an unnormalized DFT. Under the project's unitary convention, \(F^\dagger c_N=\sqrt N\,1_{U_N}\), where \(U_N\) is the reduced-residue frequency set. Therefore \(F\operatorname{diag}(1_{U_N})F^\dagger\) has entries \(c_N(n-m)/N\). This proves the exact normalization of the primitive projector, independently of external theorem numbering.

For a divisor \(d\mid N\), identify the source's primitive \(d\)-frequency \(a\) with the ambient frequency \(k=(N/d)a\pmod N\), where \(\gcd(a,d)=1\). The corresponding ambient Fourier character is \(\exp(2\pi i an/d)\). Summing its normalized rank-one projectors gives \(c_d(n-m)/N\), including \(d=1\). The coefficient is \(1/N\) for an \(N\times N\) ambient projector. Using \(1/d\) instead gives the wrong ambient scale when \(d<N\).

These sets partition the \(N\) Fourier frequencies by their additive order in \(\mathbb Z/N\mathbb Z\), equivalently by the multiplicative order of their phase roots \(\exp(2\pi i k/N)\). Hence the divisor projectors are mutually orthogonal and sum to the identity. The zero vector has no distinguished positive least period. For a nonzero vector in a single exact-order shell, the least period is the shell label. General mixtures have least period given by the least common multiple of their nonzero shell labels. These statements are about cyclic or periodically extended length-\(N\) records. They do not identify arbitrary hidden periods in incomplete, noisy, or noncommensurate records without further assumptions.

The conversion from a nonzero complex vector to a normalized quantum state adds a Hilbert-space interpretation. The unitary Fourier change of basis and Born probabilities do not establish a new quantum algorithm, efficient state preparation, quantum hardware realization, or computational advantage. No such claim is supported or searched here.

## Search boundary and retained evidence

- **Initial local search:** project input Markdown, LaTeX, JSON, and Python for Ramanujan, Vaidyanathan, bibliography, reference, 1918, and DOI.
- **Discovery pass:** exact original article title; the exact Part I and Part II titles; author-name/DOI queries; Caltech-domain PDF searches for fundamentals and FIR sequences.
- **Verification pass:** opened the Caltech author repository records, the official Caltech project bibliography, the author-hosted conference PDF, the IMSc original-paper landing page, and the Ramanujan primary-text transcription. Also rechecked DLMF §27.10 equations 27.10.2–27.10.5 as an official formula cross-check, not a new research-paper attribution.
- **Citation graph:** conference paper's bibliography checked for the Ramanujan original and its contemporary journal Parts I–II. No exhaustive backward or forward citation search was performed.
- **Coverage:** English-language primary papers and official institutional records; arithmetic and discrete signal processing; classical sources through the 2014 papers relevant to the attribution question. This was not a current-state-of-the-art survey through 2026.
- **Failed retrievals:** two guessed general publication-index URLs under the author's Caltech directory returned errors. Neither failure is evidence of absent literature. The known author PDF remained accessible.
- **Persistence:** only this report, a machine-readable summary, and bibliographic metadata are included. External source PDFs are not bundled. No source-cache entry or content hash is asserted.
- **Global nonclaim:** this bounded check does not establish novelty, priority of every generalization, universality of the framework, or a new physical effect. The release's contribution is its explicit worked realization, self-contained derivation, and exact computational/formal concordance.
