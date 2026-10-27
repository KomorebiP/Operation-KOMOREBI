# Third-party notices for Paper II release 1.1.1

The original project's MIT and CC BY 4.0 grants in `../LICENSE.md` apply to
original project material. The materials below retain their supplied terms.
`THIRD_PARTY_INVENTORY.json` lists their paths and notices.

## AINTLIB divided difference estimates

The production file
`formal/current/KomorebiVerification/PaperII/ReleaseCycleDSlope.lean`
adapts Chris Birkbeck's `DslopeIntegral.lean` from CBirkbeck/AINTLIB.

Original notice:

> Copyright (c) 2026. All rights reserved.
> Released under Apache 2.0 license as described in the file LICENSE.
> Authors: Chris Birkbeck

The applicable Apache 2.0 terms are reproduced in `LICENSE.AINTLIB.txt`.
The upstream source is pinned at commit
`2931529d8d72c086f2b5f58c33d25352dc301b16`, path
`projects/LeanModularForms/LeanModularForms/ForMathlib/DslopeIntegral.lean`,
Git blob `2b50aeb218838f86f4c8d1351e9925d73afe3dea`.

The retained unmodified copy is
`verification/closeout_2026-10-19/semantic/provenance/UpstreamDslopeIntegral.lean`.
Its repository is <https://github.com/CBirkbeck/AINTLIB>.

The 19 October adaptation generalizes scalar complex estimates to functions
valued in an arbitrary complete complex normed space. It adds symmetry and
repeated divided difference identities and proves holomorphy of the actual
finite cycle integral with integrable velocities. The current adapted source
contains the original notice and a prominent modification notice.

The adaptation and all retained copies, including pre-attribution historical
snapshots and its compiled object, remain under Apache 2.0. They are listed
explicitly in `THIRD_PARTY_INVENTORY.json`. No separate upstream NOTICE file
was supplied with the inspected source materials.

## Lean and Mathlib

Exact Lean and Mathlib source snapshots were retained to review the kernel
audit and a generated upstream equation theorem. Their copyright headers
remain intact. The complete supplied terms are in `Lean-LICENSE` and
`Mathlib-LICENSE`. `SOURCE_LICENSE_PROVENANCE.json` identifies those copies.

The runtime and full upstream caches are external dependencies. The release
does not relicense them.

## URW P052 and Nimbus Sans

Standalone P052 and Nimbus Sans font files use AGPL version 3 with the
upstream PostScript/PDF embedding exception. Their exact notice and full
AGPL text remain in each edition's `fonts/URW-FONT-LICENSE.txt`.

All 24 font copies across the three editable editions match the eight
upstream font faces at commit
`3c0ba3b5687632dfc66526544a4e811fe0ec0cd9` of
<https://github.com/ArtifexSoftware/urw-base35-fonts>.

The exact upstream Type1, AFM, OTF, and TTF files for these faces, together
with the unmodified upstream COPYING, LICENSE, and README, are supplied in
`third_party/urw_base35_fonts/`. Its `UPSTREAM_PROVENANCE.json` records file
hashes and the match to the bundled OTF files.

The embedding exception permits including these font programs in the reading
PDFs regardless of the document license. The standalone fonts keep their
own terms. The CC BY stanza in the Debian notice applies to upstream
appstream metadata, not to the fonts.

## Latin Modern and DejaVu

Latin Modern Mono and Math retain the GUST Font License notice in each
edition's `fonts/LATIN-MODERN-FONT-LICENSE.txt`. The complete incorporated
LPPL version 1.3c text is additionally supplied in `LPPL-1.3c.txt`.

DejaVu Sans Mono retains the Bitstream Vera font license and its notice that
DejaVu modifications are public domain. Its complete notice is in
`editable/lean_guide/fonts/DEJAVU-FONT-LICENSE.txt`.

## Python package

The bundled `projector_seed_refinement-1.2.1-py3-none-any.whl` contains
original project code. It now has an adjacent full MIT license notice. Keep
that notice with any separate redistribution of the historical wheel.
NumPy, SymPy, Matplotlib, pytest, and other externally installed tools keep
their own terms. Their dependency binaries are not bundled here.
