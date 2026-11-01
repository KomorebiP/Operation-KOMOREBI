"""Reading aids keyed to the original Paper VI TikZ labels.

Integer cells name original labels. Every label appears exactly once.
"""
from paper_iv_atlas_descriptions import figure, table, text

ADDITIONAL_DESCRIPTIONS = {
    'weighted_projection': ('An observable and its weighted conditional expectation are shown as bars.', 'The left panel gives the four observable values. The right panel replaces values inside each block by its weighted average. The weights and the two resulting block values are written above the panels.'),
    'variance': ('A weighted squared norm is split into mean, between-block, and within-block parts.', 'Three adjacent segments represent the displayed orthogonal contributions. Their values appear above the bar, and the three component vectors appear below it. The source plate identifies the weighted inner product used for this decomposition.'),
    'evidence': ('A uniform prior is reweighted into a posterior.', 'The left panel gives equal prior masses at four addresses. The right panel shows the posterior after the displayed likelihood is applied and normalized. The likelihood vector and total evidence are annotated above.'),
    'insufficiency': ('Two priors with the same coarse masses produce different coarse posteriors.', 'The left panel gives their common two-packet prior. The middle and right panels give the two updated packet distributions. The note above attributes the difference to redistribution hidden inside the first packet.'),
    'loss_vector': ('Two update procedures land at different points on a two-packet simplex.', 'The line represents posterior mass in the first packet. An open point marks the declared coarse update and a filled point marks updating first in the fine model. The arrow gives their displayed difference.'),
    'odds': ('Two posterior probabilities separate along a nonlinear Bayesian flow.', 'The solid curve rises from one half while the dashed curve falls from one half. The expressions on the right give the probabilities and their differential equation. The note distinguishes conservation of total mass from preservation of mixtures.'),
    'filter_order': ('Two bar pairs compare prediction followed by update with the reverse order.', 'Both panels start from the same prior, transition, and likelihood, as stated above them. The displayed probability vectors differ. The left panel uses prediction first; the right panel applies the observation first.'),
    'beta': ('Prior and posterior beta densities are compared on the unit interval.', 'The dashed curve is the prior and the solid curve is the posterior after the stated observation. The right-hand notes distinguish the evidence for ordered data from the evidence for count data, while retaining the same posterior.'),
    'fractional': ('A changed generator graph is paired with changed mode decay.', 'The left graph distinguishes the original couplings from the added fractional couplings. The right plot compares the two displayed decay factors for the fastest mode. The source retains the same spectral modes while changing their clocks.'),
    'gap': ('Square-root perturbation curves are compared with and without a gap.', 'The horizontal axis is generator perturbation. The upper curve is the ungapped difference; the lower curve is the gapped difference. A straight certificate is shown alongside the gapped case, and the note states the limitation at zero.'),
    'random_clock': ('A subordination-clock density is plotted against diffusion time.', 'The curve rises to a marked mode and then has a long tail. The integrals at right distinguish its total mass from its first moment. The plate specifies the fixed clock parameter used for the drawing.'),
    'green': ('A piecewise-linear Green function is paired with a scaled inverse matrix.', 'The left graph samples one Green-function column at grid nodes. The matrix at right is the displayed scaled finite inverse. The equation beneath it keeps the grid-spacing factor between the nodal Green values and the inverse operator.'),
    'mesh': ('Three finite-difference error curves shrink as the mesh is refined.', 'The curves give the stated quartic test problem at three grid spacings. The table on the right pairs each spacing with its maximum error. The formula above the plot states the exact error profile for this example.'),
    'paths': ('Eight finite paths are listed with their probabilities, weights, and contributions.', 'Read each row across from the path address to its probability, departure-state weight, terminal value, and weighted contribution. The bottom note gives the total path probability and weighted terminal expectation. The selectable transcript retains every original table label.'),
    'resolvent': ('An exact retained resolvent is compared with deletion of the hidden state.', 'The solid and dashed curves show the two expressions written at right for positive spectral parameter. The source note identifies the pole retained through hidden feedback. The full system and the deleted model use different resolvent coefficients.'),
    'memory': ('Exact retained evolution is compared with naive deletion.', 'The two curves start together and then separate: the exact retained state approaches a nonzero limit, while the deletion curve decays toward zero. The formulas and memory kernel are written to the right.'),
    'jordan': ('A polynomial-exponential memory coefficient is paired with a repeated-pole formula.', 'The curve rises from zero, reaches a marked maximum, and decays. The annotations retain the nilpotent Jordan part, its exponential, and the transform with a repeated pole. The note identifies the derivative information carried by that pole.'),
    'survival': ('Survival, absorbed mass, and hazard are plotted as different curves.', 'The solid survival curve decreases, the dashed absorbed mass increases, and the dotted hazard starts at zero. Their meanings and the eventual-exit statement are written beside the plot. The plate keeps probability and rate distinct.'),
    'naturality': ('A block operator and its rational function are shown as matrices.', 'The dashed block in the function matrix corresponds to the non-diagonal repeated-eigenvalue block. The right-hand annotations give the scalar function and its derivative at that eigenvalue. The note distinguishes the whole block function from scalar substitution alone.'),
    'integrated_filter': ('Two fine posteriors and one coarse posterior complete a two-observation example.', 'Read the three bar panels from left to right. The first two use the four fine states; the third aggregates into the two declared packets. The two evidence values and their product are written above.'),
    'summability': ('Three partial sums distinguish accumulated defects from a small one-step value.', 'The solid, dashed, and dotted curves are the three sums listed at right. The source note reserves the infinite-series conclusion for the exact formulas. The horizontal axis is the refinement cutoff.'),
    'ext_paths': ('Three directed packets have only finitely many forward paths.', 'Two arrows lead from packet zero to packet one and then packet two, with their transfer weights written above. The time-dependent components are written below the packets, followed by two exact-time examples.'),
    'ext_closure': ('A rotating vector returns through a hidden direction.', 'The semicircle follows the two-step excursion from the horizontal axis through the vertical direction to the opposite horizontal point. The boxes compare the full two-step return with inserting the retained projector after each step.'),
    'ext_tails': ('A sequence of halving tail bounds is shown as bars.', 'The horizontal labels give successive refinement levels. Each bar is half the preceding one, and its exact value is written above it. The plate explains the stated scalar completion and connecting maps.'),
    'ext_obstruction': ('An aggregation diagram exposes a forgotten-direction witness.', 'The upper row applies the fine transition to a vector in the aggregation kernel. The vertical arrows aggregate before and after that transition. The dashed lower arrow and its question mark show the attempted coarse step, with the obstruction written beneath.'),
    'ext_hermite': ('Two Gaussian-degree energies decay at different rates.', 'The upper stacked bar gives the initial degree-one and degree-two energies. The smaller lower bar gives them at the displayed later time. The legend distinguishes the two degrees and the note gives their total remaining energy.'),
    'ext_profiles': ('Four states are grouped by two-coordinate likelihood profiles.', 'The first two states share their displayed profile and are joined by a brace. The remaining states have separate profiles and are labelled as separate packets. The bottom formula identifies the joint profile being compared.'),
    'ext_information': ('Relative entropy is split into coarse and conditional parts.', 'The two segments of one bar represent the terms labelled below them. The total is displayed above the bar. The source plate states the positivity assumptions for the reference masses.'),
    'ext_cumulants': ('A tilted three-score distribution is shown as a bar chart.', 'The horizontal addresses are the three score values, and each bar is labelled by its posterior probability. The annotation below gives the time, mean, and variance used by the worked example.'),
    'ext_selection': ('Three memory blocks are ranked by certified contributions.', 'Each horizontal bar is labelled by its decay rate and contribution. The longest bar is the Jordan block; the smaller bars represent the two other rates. The plate states the cost and block-count budget for this selection problem.'),
    'ext_trajectory': ('A trajectory-error curve is paired with a finite-horizon certificate.', 'The curve rises from the origin to the marked time horizon. Its exact expression is written beside and below the plot. A separate box contains the interval certificate, which the source derives under common initial data and forcing.'),
    'ext_auxiliary': ('Two auxiliary states and one retained state form a feedback realization.', 'The top arrows pass the retained input through the two auxiliary states. The lower arrow feeds the second auxiliary output back to the retained state. The input, link, feedback, and decay-rate labels are all retained.'),
    'ext_risks': ('A population is split into survivors and two absorbed causes.', 'The three adjacent segments give the surviving mass and the two cumulative absorbed masses at the displayed time. The note above states the mixture among survivors. The labels distinguish that mixture from the cumulative cause totals.'),
    'ext_substitution': ('An operator defect is transported through a rational function.', 'The arrow maps the displayed original defect to the rational-calculus defect. The notes below give the two inverse factors, the sign, and the zero-defect control. The plate compares this rectangular substitution with its core naturality result.'),
    'ext_evidence': ('Three boxes separate inherited formal scope, example checks, and edition records.', 'The boxes describe the retained source edition: saved formal logs, its rational example checks and false controls, and its PDF build and page review. The bottom note keeps these evidence categories separate and rejects a combined proof count.'),
}

FIGURES = {
    'three_views': figure(
        'Full-state bars, coarse packet masses, and retained-state curves show three different reductions.',
        'Read left to right. The first two panels use the same distribution: the middle panel sums states into two packets and loses the within-packet shape. The separate right-hand model compares the exact retained evolution with the result of omitting its coupling. The solid and dashed curves start together and then separate. The curve panel is a different model from the bars.',
        table(0, ['State', 'Probability'], [[1,2],[3,4],[5,6],[7,8]]),
        table(9, ['Packet', 'Mass'], [[10,11],[12,13]]),
        text(22,23,title='Retained and hidden states'),
        text(21,14,15,16,17,title='Horizontal axis and ticks'),
        text(18,19,20,title='Vertical ticks')),
    'clock': figure(
        'Three pairs of bars give the exact state probabilities at three elapsed times.',
        'Each panel uses the same two states and probability scale. Mass moves from state zero toward the uniform distribution. The time labels and every displayed bar value are transcribed in the three tables below.',
        table(0, ['State', 'Probability'], [[1,2],[3,4]]),
        table(5, ['State', 'Probability'], [[6,7],[8,9]]),
        table(10, ['State', 'Probability'], [[11,12],[13,14]]),
        text(15)),
    'generator_modes': figure(
        'A four-state rate graph is paired with four mode-sign rows and their decay rates.',
        'The left panel places states zero and one in the upper packet and states two and three in the lower packet. Horizontal and vertical bidirectional links have the rates listed below. The right panel gives each mode in state order, followed by its generator eigenvalue. Divide every sign entry by two, as the original caption specifies.',
        table(8, ['Position', 'State'], [['Top left',4],['Top right',5],['Bottom left',6],['Bottom right',7]]),
        table('Bidirectional graph links', ['States joined', 'Rate'],
              [['0 and 1',0],['2 and 3',1],['0 and 2',2],['1 and 3',3]]),
        text(9),
        table(10, ['Mode',31,32,33,34,39],
              [[27,11,12,13,14,35],[28,15,16,17,18,36],
               [29,19,20,21,22,37],[30,23,24,25,26,38]])),
    'lumpability': figure(
        'Fine transition columns differ, but aggregation makes columns agree within each coarse packet.',
        'The left table is eight times the fine transition matrix, with target states as rows and source states as columns. The middle table sums target rows into packets A and B. Its first two columns agree, as do its last two. The right-hand coarse matrix and the original comparison note follow the tables.',
        table(0, ['Target / source',21,22,23,24],
              [[17,1,2,3,4],[18,5,6,7,8],[19,9,10,11,12],[20,13,14,15,16]]),
        table(25, ['Coarse packet / fine source',36,37,38,39],
              [[34,26,27,28,29],[35,30,31,32,33]]),
        text(40,41,42)),
    'defect_budget': figure(
        'A solid finite-horizon defect curve lies below a dashed linear certificate.',
        'The horizontal axis counts steps and the vertical axis uses the induced one-norm. The solid values come from the exact finite model. The dashed line is the bound based on the one-step defect; it is a guarantee and need not be sharp. The axis ticks and all original legend labels follow.',
        text(10,0,1,2,3,4,title='Horizontal axis and ticks'),
        text(11,5,6,7,8,9,title='Vertical axis and ticks'),
        text(12,13,14,title='One-step defect and legend')),
}

FIGURES.update({name:figure(alt,description) for name,(alt,description) in ADDITIONAL_DESCRIPTIONS.items()})
