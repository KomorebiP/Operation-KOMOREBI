# Continue from v0.38

Read README.md, PROOF.md, RESEARCH_BOUNDARY.md, SELF_REVIEW.md, and verification/fresh/RESULT.json. The unchanged v0.37 archive is in base/, including its exact v0.36 parent.

The noncommutative power-map local image is now exact with an explicit inverse certificate: Q=p^(-s)B, BD_A=D_AB=p^sI, B integral, and m>s. One congruence B vec(U-A^d)=0 modulo p^(m+s) gives a unique actual p-adic root in the prescribed ball. The inverse certificate is checked on all matrix units; it is not merely invertibility modulo p.

Do not redo the scalar/diagonal theorem, assume all-depth solvability, or replace the ordered derivative by d A^(d-1) X. Do not conflate s with v_p(d).

The next substantive local boundary is a derivative genuinely singular over Q_p, or a proved finite covering/classification of a specified shallow resonant matrix prefix. A useful explicit singular test center is diag(1,-1) for the square map: off-diagonal tangent directions vanish over Q_p, so the inverse certificate cannot exist. Another distinct target is effective simultaneous prescriptions beyond a nonresonant reference, which is not settled by the present single-power theorem.

The derivative-inversion implementation is also an engineering boundary: generalize the exact-rational certificate generator and formally connect a computable determinant/inverse calculation to InverseCertificate. This should not be reported as a solution of the singular derivative problem.

Replay:
`python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2`

Continuation prompt: Restore the v0.38 Effective Matrix Hensel checkpoint, read its proof boundary, and attempt the next genuinely singular or shallow resonant matrix block. Preserve exact hypotheses and verification evidence, and distinguish a solved sector from Strong Artin.
