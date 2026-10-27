# Third party notices for the Paper II analytic extension

## AINTLIB divided difference estimates

The file `ReleaseCycleDSlope.lean` includes material adapted from Chris Birkbeck's
`DslopeIntegral.lean` in [CBirkbeck/AINTLIB](https://github.com/CBirkbeck/AINTLIB).

Original notice:

> Copyright (c) 2026. All rights reserved.
> Released under Apache 2.0 license as described in the file LICENSE.
> Authors: Chris Birkbeck

The applicable license is reproduced in `LICENSE.AINTLIB.txt`.

The upstream source is pinned at repository commit
`2931529d8d72c086f2b5f58c33d25352dc301b16`, path
`projects/LeanModularForms/LeanModularForms/ForMathlib/DslopeIntegral.lean`,
Git blob `2b50aeb218838f86f4c8d1351e9925d73afe3dea`.
An unmodified copy is retained as `UpstreamDslopeIntegral.lean` beside the
adapted source.

The adaptation made on 2026-10-19 generalizes the scalar complex estimates to
functions valued in an arbitrary complete complex normed space. It adds
symmetry and repeated divided difference identities, then proves holomorphy
of the actual finite cycle integral with integrable velocities. A prominent
modification notice and the original copyright and license notices are
included in the adapted source.

Other AINTLIB files retained in the audit's `upstream` directory were read as
primary sources while investigating a direct import. Their original notices
remain intact. They were not imported by the production analytic extension.
The fresh winding and comparison proofs remove the extra regularity and
local winding hypotheses present in the inspected upstream theorem.

The public repository root contained the Apache 2.0 license, and no separate
upstream NOTICE file was supplied with the inspected source materials.
