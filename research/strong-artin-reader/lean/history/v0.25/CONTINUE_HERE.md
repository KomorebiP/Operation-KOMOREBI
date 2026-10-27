# Continue from Strong Artin v0.25

Read README.md, RESEARCH_BOUNDARY.md, MANIFEST.json and the source capstones.
Preserve the exact v0.24 and v0.20 base archives.

The nonlinear compatibility gap is now resolved under an exact moving-relation
hypothesis and residue exactness. Do NOT revisit the false fixed residual-target
shortcut. No integral retraction is needed for the new principal-Artin theorem.

The strongest polynomial theorem is:

    PolynomialMovingSyzygyHensel.
      exists_exact_root_over_principal_nilpotent_residue

It requires B(x)F(x)=0 on the residual fibre and image(Jbar)=kernel(Bbar).
The alternative input is ker(Jbar*)=range(Bbar*), via
IntrinsicGradedLiftingCapstone.

The actual representation-equation module supplies a concrete next route:

    D_r(g,h) = r(g)r(h)-r(gh)
    r(g)D_r(h,l)-D_r(gh,l)+D_r(g,hl)-D_r(g,h)r(l)=0.

Across a square-zero extension, kernel-valued corrections change D_r by
C_r(b), with no higher remainder. A lift exists exactly if that correction can
cancel D_r. The remaining issue is compatible defect versus correction image.

Highest-value next target: normalize this exact representation-defect complex,
construct its genuine cohomology class with the correct coefficient action,
prove independence of the chosen lifts, and identify vanishing with lift
existence. Keep continuity and local conditions explicit. Then compare this
complex to the actual Selmer/auxiliary-prime construction rather than silently
assuming a cotangent-H1/Selmer equivalence.

A second route is to build a full finite represented-algebra example whose
actual moving relation matrix supplies the dual exactness after allowed
auxiliaries. Prove that any augmented point descends before claiming a point of
the unaugmented arithmetic problem.

Do not count the new 42 theorem declarations as 42 new Strong Artin results.
They include standard structural lemmas, exact examples and conditional
composition theorems. No historical novelty claim has been established.

Replay in three bounded batches as documented in README.md. No background work
is left running by this handoff.
