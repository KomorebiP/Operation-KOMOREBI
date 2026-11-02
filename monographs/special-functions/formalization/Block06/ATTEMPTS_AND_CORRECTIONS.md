# Route and implementation notes for SF-LEAN-B06

The direct construction route succeeded. A complex-valued coefficient bridge
supplies the necessary obstruction without restricting the rescaling
witnesses to real numbers. The converse constructs the normalized scalar
solution from the equal-row coupled tuple and proves the two transformed
equations, with one surface requiring a factor interchange.

Scratch compiler feedback corrected implementation details: unfolding U and
oddSum when transforming actual HasSum values; reducing the zero-index power
before extracting AB=1; using HasDerivAt.congr_deriv instead of broad convert
steps that generated algebra-instance equality goals; reducing lambda
applications before rewriting scalar inputs; and removing tactics already
made redundant by field_simp. Warnings remain errors. No hypothesis was
weakened and no placeholder or custom axiom entered production.

The positive-root algebra and strict effective-scale bounds compiled directly.
The symmetry consequence T(x,y)=T(y,x) then upgraded the preserved finite-jet
collision to equality of both full entire functions at the two distinct
ordered tuples. Earlier records retain their historical, weaker scope.

The alternative scaled-recurrence and separate surface-symmetry proofs remain
deferred, not refuted. They are unnecessary for the completed contract and
may be useful for future coefficient estimates or explicit formulas.

The normalized candidate A=-i,B=i was selected as an adversarial complex
test: AB=1 holds, but the cubic coefficient changes sign. It is rejected
mathematically by the actual coefficient identity. Testing one such candidate
is not used as the proof of the general complex obstruction.

The fresh replay consumes hashed inputs and writes its actual outputs in a
new external directory. IO_MANIFEST.json records the sealed input/output
inventory. Scratch files remain outside the repository's formal production
and evidence directories. Any failed fresh replay, if one occurs, is retained
separately rather than overwritten.
