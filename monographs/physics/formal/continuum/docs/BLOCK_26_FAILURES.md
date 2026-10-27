# Block 26 failures and repairs

## 1. Spectator replication was rejected as geometry

The Block 25 cylinder map duplicates a coarse value into a child label while leaving the physical translation unchanged.  It is useful as an exact refinement architecture, but it is not a half-spacing lattice.  Block 26 therefore introduces a midpoint site and a translation that takes two fine steps per coarse edge.

## 2. Arbitrary midpoint duplication was not gauge covariant

Setting the midpoint equal to the endpoint ignores link transport.  The repaired embedding transports the spinor by the first half-link.  Independent midpoint gauge values then cancel correctly between the two sublinks.

## 3. Raw interpolation was not an isometry

Endpoint-plus-midpoint interpolation doubles the counting-measure norm.  A negative control confirms that the raw isometry claim leaves the false goal

`2 * stateIP ψ φ = stateIP ψ φ`.

The repair is the geometrically appropriate half-cell measure.

## 4. One fine step cannot equal one coarse step

The first fine step reaches the midpoint, not the next coarse endpoint.  A negative control attempts the false one-step intertwining and is rejected with the site mismatch

`inr x = coarseLift τ (inl x)`.

The correct theorem compares **two** fine shifts with one coarse shift.

## 5. Universal multi-axis path independence is false

The first design impulse was to combine the three directional midpoint embeddings as though all path choices agreed.  This silently imposes zero gauge curvature.  Block 26 instead defines the plaquette and proves path independence equivalent to unit holonomy.

A negative control claiming every plaquette is flat is rejected by the explicit goal

`-1 = 1`.

## 6. Exactness is presently one-axis

The checked `M-S-M` theorem should not be described as exact refinement of the complete `M-X-Y-Z-Y-X-M` walk.  The latter requires a three-dimensional refined cell and either flatness hypotheses or an explicit holonomy-dependent defect.

## 7. Cumulative build execution

The first full rebuild attempts exceeded the external command window while populating inherited caches.  No timeout was counted as verification.  A detached resumed build completed successfully, after which the authoritative verifier reran the now-cached cumulative build and every new proof-integrity gate successfully.

## 8. Command working-directory mistake

An early warnings-as-errors invocation supplied `lake -d` but ran `lean` from the wrong current directory, producing a file-not-found error.  This was an invocation error, not a Lean failure.  The command was rerun from the project root and passed.
