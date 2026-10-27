# Official OEIS source records

All 30 planned anchors were freshly read on 7 October 2026 from the official OEIS export. These checks authenticate identifiers, exact entry names, both offset fields, the first eight indexed integer terms, entry revision headers, and author fields. They do not certify every formula or comment in an OEIS entry.

## Source and version

- Maintainer: OEIS Foundation and the named entry contributors.
- Official source: [oeis/oeisdata](https://github.com/oeis/oeisdata), the OEIS internal-format export.
- Pinned commit: `2ce625d68f85e35e26e15c0d9681f69280c095e7`.
- Export time recorded by `time.txt`: `2026-10-07T03:00:24-04:00`.
- Retrieval: `2026-10-07T22:22:20.917139+00:00`.
- License: Creative Commons Attribution Share Alike 4.0.
- Successful reads: **30/30**; access failures: **0**.
- The live internal pages for tribonacci, tetranacci, tangent and Bernoulli conventions were also inspected. All 30 metadata records rely on the explicitly pinned daily export. Changes to the live database after that export are outside this check.

## Exact indexing and prefix

The first offset component is the initial sequence index. The second is retained verbatim as OEIS metadata. Prefixes below start at the initial index, not automatically at zero.

| OEIS entry | Initial index | Offset field | First eight terms | Entry revision |
|---|---:|---|---|---|
| [A000045](https://oeis.org/A000045) | 0 | `0,4` | 0, 1, 1, 2, 3, 5, 8, 13 | `#2599 Oct 03 2026 09:50:31` |
| [A000032](https://oeis.org/A000032) | 0 | `0,1` | 2, 1, 3, 4, 7, 11, 18, 29 | `#871 Oct 03 2026 09:50:47` |
| [A000073](https://oeis.org/A000073) | 0 | `0,5` | 0, 0, 1, 1, 2, 4, 7, 13 | `#742 Oct 03 2026 09:50:23` |
| [A000078](https://oeis.org/A000078) | 0 | `0,6` | 0, 0, 0, 1, 1, 2, 4, 8 | `#441 Jun 15 2026 16:49:53` |
| [A001045](https://oeis.org/A001045) | 0 | `0,4` | 0, 1, 1, 3, 5, 11, 21, 43 | `#1350 Jun 30 2026 12:07:24` |
| [A001075](https://oeis.org/A001075) | 0 | `0,2` | 1, 2, 7, 26, 97, 362, 1351, 5042 | `#355 May 25 2026 18:06:39` |
| [A001353](https://oeis.org/A001353) | 0 | `0,3` | 0, 1, 4, 15, 56, 209, 780, 2911 | `#495 Oct 04 2026 09:52:07` |
| [A000984](https://oeis.org/A000984) | 0 | `0,2` | 1, 2, 6, 20, 70, 252, 924, 3432 | `#1195 Sep 17 2026 23:06:07` |
| [A000108](https://oeis.org/A000108) | 0 | `0,3` | 1, 1, 2, 5, 14, 42, 132, 429 | `#2256 Oct 03 2026 09:50:18` |
| [A000110](https://oeis.org/A000110) | 0 | `0,3` | 1, 1, 2, 5, 15, 52, 203, 877 | `#1456 Oct 05 2026 15:25:51` |
| [A000670](https://oeis.org/A000670) | 0 | `0,3` | 1, 1, 3, 13, 75, 541, 4683, 47293 | `#913 Oct 02 2026 10:10:27` |
| [A000142](https://oeis.org/A000142) | 0 | `0,3` | 1, 1, 2, 6, 24, 120, 720, 5040 | `#979 Aug 26 2026 09:41:19` |
| [A000166](https://oeis.org/A000166) | 0 | `0,4` | 1, 0, 1, 2, 9, 44, 265, 1854 | `#767 Aug 14 2026 16:07:42` |
| [A000111](https://oeis.org/A000111) | 0 | `0,4` | 1, 1, 1, 2, 5, 16, 61, 272 | `#799 Aug 31 2026 15:41:36` |
| [A000182](https://oeis.org/A000182) | 1 | `1,2` | 1, 2, 16, 272, 7936, 353792, 22368256, 1903757312 | `#565 Jul 21 2026 22:27:30` |
| [A000364](https://oeis.org/A000364) | 0 | `0,3` | 1, 1, 5, 61, 1385, 50521, 2702765, 199360981 | `#579 Aug 04 2026 17:17:15` |
| [A027641](https://oeis.org/A027641) | 0 | `0,11` | 1, -1, 1, 0, -1, 0, 1, 0 | `#317 Aug 18 2026 15:50:41` |
| [A027642](https://oeis.org/A027642) | 0 | `0,2` | 1, 2, 6, 1, 30, 1, 42, 1 | `#204 Aug 04 2026 16:21:07` |
| [A000041](https://oeis.org/A000041) | 0 | `0,3` | 1, 1, 2, 3, 5, 7, 11, 15 | `#1245 Sep 29 2026 11:35:17` |
| [A005259](https://oeis.org/A005259) | 0 | `0,2` | 1, 5, 73, 1445, 33001, 819005, 21460825, 584307365 | `#337 Sep 29 2026 11:31:54` |
| [A008683](https://oeis.org/A008683) | 1 | `1,1` | 1, -1, -1, 0, -1, 1, -1, 0 | `#413 Oct 04 2026 21:02:18` |
| [A000010](https://oeis.org/A000010) | 1 | `1,3` | 1, 1, 2, 2, 4, 2, 6, 4 | `#644 Oct 03 2026 09:51:00` |
| [A000120](https://oeis.org/A000120) | 0 | `0,4` | 0, 1, 1, 2, 1, 2, 2, 3 | `#516 Jul 27 2026 14:54:00` |
| [A010060](https://oeis.org/A010060) | 0 | `0,1` | 0, 1, 1, 0, 1, 0, 0, 1 | `#616 Jun 29 2026 00:58:43` |
| [A001316](https://oeis.org/A001316) | 0 | `0,2` | 1, 2, 2, 4, 2, 4, 4, 8 | `#378 Jul 30 2026 13:30:10` |
| [A000217](https://oeis.org/A000217) | 0 | `0,3` | 0, 1, 3, 6, 10, 15, 21, 28 | `#2067 Sep 02 2026 22:00:14` |
| [A000292](https://oeis.org/A000292) | 0 | `0,3` | 0, 1, 4, 10, 20, 35, 56, 84 | `#1102 Oct 03 2026 09:49:12` |
| [A000578](https://oeis.org/A000578) | 0 | `0,3` | 0, 1, 8, 27, 64, 125, 216, 343 | `#572 Jul 03 2026 11:32:01` |
| [A000290](https://oeis.org/A000290) | 0 | `0,3` | 0, 1, 4, 9, 16, 25, 36, 49 | `#922 Oct 06 2026 20:50:50` |
| [A000027](https://oeis.org/A000027) | 1 | `1,2` | 1, 2, 3, 4, 5, 6, 7, 8 | `#718 Jun 28 2026 15:47:49` |

## Normalization required in the guide

- **A000045**: Use F(0)=0, F(1)=1.
- **A000032**: Use L(0)=2, L(1)=1; this is not the shifted Lucas sequence beginning 1,3.
- **A000073**: Use a(0)=a(1)=0 and a(2)=1. The name tribonacci is also applied to differently seeded sequences.
- **A000078**: Use a(0)=a(1)=a(2)=0 and a(3)=1.
- **A001075**: Seeds 1,2; recurrence a(n)=4a(n−1)−a(n−2). If x_n denotes this sequence and y_n denotes A001353(n), the common-index Pell identity is x_n²−3y_n²=1.
- **A001353**: Seeds 0,1; recurrence a(n)=4a(n−1)−a(n−2). Do not confuse this with the Pell numbers 0,1,2,5,… .
- **A000111**: Full Euler up/down stream. Its even-index terms are A000364; its odd-index terms A000182(n) correspond to full index 2n−1, n≥1.
- **A000182**: OEIS starts at n=1. tan(t)=Σ_{n≥1} a(n)t^(2n−1)/(2n−1)!; if a zero-based stream is used, explicitly set b(j)=a(j+1).
- **A000364**: Nonnegative secant-number magnitudes. sec(t)=Σ_{n≥0} a(n)t^(2n)/(2n)!; signed Euler-number conventions differ.
- **A027641**: Numerators of B_n with B1=−1/2, paired with A027642 denominators. If a software library returns B1=+1/2, correct that convention before comparing.
- **A027642**: Positive reduced denominators of B_n with B1=−1/2, including denominator 1 for zero values.
- **A008683**: OEIS domain starts at n=1. Do not insert μ(0) as an OEIS term.
- **A000010**: OEIS domain starts at n=1. Do not insert φ(0) as an OEIS term.
- **A000027**: OEIS starts at n=1 with a(n)=n. A zero-based stream of its listed terms is b(j)=j+1.
- **A001316**: Gould sequence 2^popcount(n), not the popcount sequence itself.
- **A005259**: These are the ζ(3) Apéry numbers Σ binom(n,k)² binom(n+k,k)², not the distinct ζ(2) Apéry stream.

## Compact extraction and provenance

`OEIS_SOURCE_RECORDS.json` records every exact name, author field, source URL, retrieval date, entry revision header, indexed prefix and SHA-256. Each `source_data/oeis/Axxxxxx.txt` file retains only the corresponding compact metadata extraction and eight terms. Its extraction hash is recorded separately from the full fetched entry hash. Full entry pages are not retained.

No source theorem or OEIS comment is promoted to a new proof. Exact plotted transformations are to be checked in the guide’s own computation audit. No novelty search was undertaken.

## Correction boundary

An earlier atlas edge used mismatched Fibonacci and Lucas indices in a Pell-style equation. It supplies no valid dependency here. The standard common-index identity is L_m²−5F_m²=4(−1)^m. For the newly planned A001075/A001353 pair, the relevant common-index identity is x_n²−3y_n²=1. Neither statement is inferred from the bad earlier edge.
