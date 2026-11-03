"""Reading aids for the retained LSM diagrams; no new mathematical claims."""

FIGURES = {
 '00_architecture': (
  'Observation, archive, and predictive state connected by two commuting squares.',
  'Read from left to right: analysis stores an observation in an archive, then a summary produces a predictive state. The left square asks whether the stored transition agrees with the observation-space transition. The right square asks the additional question of whether the summary determines its own next state. Each square has its own contract.'),
 '01_consistency': (
  'A plane of realizable coefficients inside a redundant three-dimensional archive.',
  'The shaded plane consists of coefficient vectors whose third entry is the sum of their first two entries. The off-plane vector is synthesized and analyzed again, landing on that plane. This projection is oblique; the picture does not assert that it is an orthogonal nearest-point projection.'),
 '02_transport': (
  'A commuting square for the same operation in two coordinate charts.',
  'The horizontal route applies the operation in a chart. The vertical route changes charts. Commutativity says that changing charts before or after the operation gives the same realizable coefficients. Agreement between charts does not by itself establish predictive accuracy.'),
 '03_fibers': (
  'Two states on one observation fiber move to different next observations.',
  'The left panel places the two comparison states on the same vertical fiber: both have first coordinate zero. Applying the declared matrix sends them to points with different first coordinates in the right panel. A single update rule supplied only with the first coordinate cannot choose both next answers.'),
 '04_refinement': (
  'An observable row space enlarged until it is invariant under the known dynamics.',
  'The diagram adds the directions obtained by applying the known dynamics to the requested observation. In this example, the observation and its one-step image span the two-dimensional dual space. The forward observation must actually become available before it can serve as a causal delay state.'),
 '05_packets': (
  'Transfer blocks and a comparison of linear mixed terms with quadratic omitted energy.',
  'The transfer array records how every input packet contributes to every output packet. The accompanying curves distinguish the mixed contribution in a square from the square of the omitted amplitude. Retaining every block is an exact decomposition; dropping blocks needs a separate error estimate.'),
 '06_return_path': (
  'A retained-to-discarded-to-retained path missing from separately compressed operations.',
  'Follow the route from the retained coordinate into the discarded coordinate and back. Compressing each operation separately erases this intermediate route. In the displayed swap example, both individually compressed steps vanish while their full two-step composition returns the retained state.'),
 '07_memory': (
  'Geometrically decaying memory coefficients beside an exact trajectory and finite-memory predictions.',
  'The kernel plot describes the contribution of older resolved states after the discarded coordinate has been eliminated. The trajectory comparison uses the declared rational example. A tail bound evaluated on the true history and an error bound for a recursively generated prediction are different statements; the text keeps their assumptions separate.'),
 '08_defect': (
  'Analytical error envelopes for contracting, neutral, and expanding propagation.',
  'Compare how the same local defect is propagated under different amplification factors. Earlier defects receive products of subsequent factors. These curves are analytical envelopes with declared constants, rather than measured prediction errors.'),
 '09_identification': (
  'Paired consecutive outputs spanning the declared two-dimensional delay space.',
  'The two columns of the input delay matrix are independent in the running example. Their paired next columns identify a transition on that input span. Coverage of a larger unknown state space is not established by a finite observed rank.'),
 '10_domain': (
  'A probability domain, its observation branches, and normalization of a positive-mass branch.',
  'Each observation operator must preserve the cone, and their sum must preserve total mass. A normalized initial state supplies the starting probability law. Normalization is defined only for branches of positive mass; a zero-mass branch cannot be divided into a posterior.'),
 '11_psd': (
  'A finite orbit in a normalized disk, with the corresponding positive-semidefinite matrix certificate.',
  'The disk is the normalized slice of the curved Lorentz cone. The matrix representation translates cone membership into positive semidefiniteness. The finite drawn orbit illustrates the rotation; its density and the obstruction to finite generators come from the written proofs, rather than the plotted points.'),
 '12_covariance': (
  'A quadratic averaging example showing the mass lost by averaging before congruence.',
  'Averaging the quadratic action retains a covariance contribution. Applying the averaged matrix first loses that contribution even though the diagonal matrices commute. The example uses the stated uniform probability measure, so density values and mass are interpreted relative to that measure.'),
 '13_moments': (
  'A curved normalized moment domain and its homogeneous cone boundary.',
  'The normalized domain lies above the parabola and below the horizontal upper boundary. The three-dimensional wireframe shows its homogeneous geometry. Within the supplied parameter family, uncertainty changes a boundary posterior’s probability without moving its ray; arbitrary coordinate perturbations do not share that protection.'),
 '14_uncertainty': (
  'A schematic parameter rectangle inside a region with a sufficient positivity floor.',
  'One obligation is statistical: the confidence event must cover the true parameter. The other is algebraic: every parameter returned in the rectangle must satisfy the internal validity certificate. This rectangle is a schematic inclusion picture, rather than a confidence set estimated from observations.'),
 '15_horizons': (
  'Analytical bounds for complete records, one-time marginals, and rolling windows.',
  'A complete record can accumulate distinguishability as its horizon grows. Under the separate Markov and minorization assumptions, a one-time marginal can remain close. A rolling window combines the marginal discrepancy with the additional steps in the window. The plotted bounds have declared constants and are not empirical errors.'),
}

# Editorial questions help readers choose a plate; the source titles stay intact.
QUESTIONS = {
 1: 'Can every stored coefficient vector represent an observation?',
 2: 'Do two coordinate descriptions describe the same operation?',
 3: 'Can the same current summary lead to two different futures?',
 4: 'Which extra observable directions make the state close?',
 5: 'What changes when interactions cross packet boundaries?',
 6: 'Can a discarded coordinate matter after a round trip?',
 7: 'What does eliminating the discarded state leave behind?',
 8: 'Will a local defect shrink or grow as it propagates?',
 9: 'What does a finite set of observations actually identify?',
 10: 'Can future tests themselves supply predictive coordinates?',
 11: 'What makes every observation record a valid probability?',
 12: 'How can a curved domain have a finite matrix certificate?',
 13: 'What is lost by averaging before a quadratic action?',
 14: 'Which uncertainties preserve the supplied curved geometry?',
 15: 'How do statistical coverage and exact validity work together?',
 16: 'Are we bounding a whole record or one future observation?',
 17: 'Where are the full statements, proofs, and recorded scopes?',
}
