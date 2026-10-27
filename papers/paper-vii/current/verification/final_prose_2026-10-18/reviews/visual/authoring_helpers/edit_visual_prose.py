from pathlib import Path
import difflib, hashlib, json, re

ROOT = Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Final_2026-10-18')
BASE = Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Complete_Proofread_2026-10-18')
OUT = Path('/workspace/scratch/be33f0b6c391/tmp/p7_final_visual_prose')
OUT.mkdir(parents=True, exist_ok=True)
ledger = []
changed = {}

def math_spans(text):
    def escaped(pos):
        backslashes=0
        while pos>0 and text[pos-1]=='\\':
            backslashes+=1
            pos-=1
        return backslashes%2==1
    spans=[]
    i=0
    while i<len(text):
        opening=None
        if text[i]=='$' and not escaped(i):
            opening='$$' if text.startswith('$$',i) else '$'
            closing=opening
        elif text[i:i+2] in [r'\[',r'\('] and not escaped(i):
            opening=text[i:i+2]
            closing=r'\]' if opening==r'\[' else r'\)'
        if opening:
            end=i+len(opening)
            while end<len(text):
                if text.startswith(closing,end) and not escaped(end):
                    spans.append(text[i:end+len(closing)])
                    i=end+len(closing)
                    break
                end+=1
            else:
                raise ValueError(('Unclosed math delimiter',opening,i))
        else:
            i+=1
    return spans

def replace(text, old, new, location, reason='Natural prose and punctuation'):
    assert text.count(old) == 1, (location, old, text.count(old))
    assert math_spans(old) == math_spans(new), ('Math changed', location, old, new)
    ledger.append({'location':location, 'before':old, 'after':new, 'reason':reason})
    return text.replace(old, new, 1)

def save(rel, new):
    old = (ROOT / rel).read_text()
    assert math_spans(old) == math_spans(new), ('File math changed',rel)
    if old != new:
        changed[rel] = {'before':old, 'after':new}
        (ROOT / rel).write_text(new)

# The page keys make each replacement local. No punctuation is replaced inside
# formulae, TikZ commands, or code syntax.
edits = {
1:[
(r'\head{Amplitudes, not just occupied addresses}', r'\head{Amplitudes retain relative phase}'),
(r'\head{Elimination, not disappearance}', r'\head{How hidden dynamics returns}'),
('The density matrix $\\rho=\\psi\\psi^*$ contains additional off-diagonal entries. Those entries matter to measurements that compare the two addresses. Deleting them is a physical channel, not simply rewriting coordinates.', 'The density matrix $\\rho=\\psi\\psi^*$ also records coherence in its off-diagonal entries. Measurements that compare the two addresses can detect this coherence. Deleting those entries applies a physical channel and changes the state.'),
('This guide reads alongside the traditional volume. Its first 28 worked pages preserve the original appendix, with source lines revised to the final edition.', "Read this guide alongside the traditional volume. The first 28 worked pages retain the original appendix's examples and mathematical content, with source references updated to this edition."),
('Exact example checks are not new Lean certificates.', 'The example checks and the inherited Lean certificates have separately recorded scopes.')],
2:[
('Addresses and coherent amplitudes.', 'They specify the space of addresses and its coherent amplitudes.'),
('Which linear operations are available.', 'It specifies the available linear operations.'),
('The whole selected subspace, not one basis vector.', 'It selects an entire subspace.'),
('Populations and coherences.', 'It records populations and coherences.'),
(r'An outcome probability $\Tr(E_k\rho)$.', r'It gives the outcome probability $\Tr(E_k\rho)$.'),
('One branch of a channel; generally not a projector.', 'It describes one channel branch and need not be a projector.'),
(r'Unitary real-time evolution $e^{-\ii tH}$.', r'It generates evolution in real time through $e^{-\ii tH}$.'),
('Packet transport generator; connection', 'Packet transport generator and connection'),
('Motion of subspaces and differentiation within their ranges.', 'They describe moving subspaces and differentiation within their ranges.'),
(r'A decomposition with $Q=I-P$.', r'They define a decomposition with $Q=I-P$.'),
('Spectral influence of the hidden sector.', 'It records the spectral influence of the hidden sector.'),
('Nonnegative operator; Euclidean transfer', 'Nonnegative operator and Euclidean transfer'),
('Decay factors and finite heat-trace diagnostics.', 'They determine decay factors and finite heat trace diagnostics.'),
(r'The bit order is the displayed left-to-right tensor order: $X_1=X\otimes I\otimes I$. A normalized pure state gives $\rho=\psi\psi^*$; a general coefficient matrix used to count a seed orbit need not be normalized.', r'The tensor factors are ordered from left to right, so $X_1=X\otimes I\otimes I$. A normalized pure state gives $\rho=\psi\psi^*$. A coefficient matrix used to count a seed orbit need not be normalized.')],
3:[
('allow the three single-bit flip operators', 'allow the three bit flip operators'),
('Dashed edges change the first bit between the two displayed squares; the other edges change one of the remaining bits.', 'Dashed edges connect the two squares by changing the first bit. The other edges change one of the remaining bits.'),
('This is exactly the cyclicity statement for the algebra generated by the flips. It is not a statement that a product of flips alone prepares every normalized vector.', 'This proves cyclicity for the algebra generated by the flips. Preparing every normalized vector requires more than products of these flips alone.')],
4:[
('Its local orbit span contains arbitrary first-subsystem vectors but only the second-subsystem direction', 'Its local orbit span allows arbitrary vectors in the first subsystem but only the second subsystem direction'),
('Local unitary operations preserve Schmidt coefficients; they do not turn the Bell vector into an arbitrary product vector as a deterministic pure-state transformation.', 'Local unitary operations preserve Schmidt coefficients. They therefore cannot turn the Bell vector into an arbitrary product vector by a deterministic transformation between pure states.'),
('This directly exhibits the rows counted by the theorem rather than inferring them from a drawing of entangled particles.', 'The calculation directly exhibits the independent rows counted by the theorem.')],
5:[
('not of the Hilbert-space dimension alone.', 'and depends on more than the dimension of the Hilbert space alone.'),
('The argument explains why the construction meets the lower bound; a successful example alone would not prove minimality.', 'The argument explains why the construction meets the lower bound and therefore proves minimality.'),
('Additional seeds or a larger operator algebra are genuinely different resources.', 'Adding seeds and enlarging the operator algebra provide different ways to supply those directions.')],
6:[
(r'The four-site shift will return on \pagerefV{27}. There it diagonalizes the Hamiltonian', r'The same shift on four sites returns on \pagerefV{27}, where it diagonalizes the Hamiltonian'),
('Its norm is only one scalar summary of that component, not a substitute for it.', 'Its norm summarizes the size of that component while leaving its phase and direction unspecified.')],
7:[
('Grouping addresses by Hamming-weight parity gives', 'Grouping addresses according to the parity of their Hamming weight gives'),
('That operation removes cross-child coherence and need not agree with dephasing only between even and odd sectors.', 'That operation removes coherence between the fine packets and can differ from dephasing only between the even and odd sectors.'),
('computational-basis measurement', 'measurement in the computational basis'),
('Internal coherence survives until an operation actually discards it; changing the address description alone does not do so.', 'Internal coherence survives a change of address description. It is lost only when an operation discards it.')],
8:[
('all eight parity-indexed matrix terms', 'all eight matrix terms indexed by parity'),
('A coordinate resolution in a derivation should not be mistaken for an experimental intervention.', 'The derivation resolves intermediate coordinates without physically measuring them.')],
9:[
('A COMPLETE DESTRUCTIVE-INTERFERENCE LEDGER', 'HOW TWO PATH AMPLITUDES CANCEL'),
('the two opposite-output path products.', 'the two path products leading to the opposite output.'),
('Thus the false calculation accidentally describes a different experiment.', 'Adding the two path probabilities would therefore describe the experiment with an intermediate measurement.')],
10:[
('Exponentiating either block gives the corresponding part of the exact evolution; the off-packet transfer stays zero for every real time.', 'Exponentiating either block gives the corresponding part of the exact evolution. Transfer between the packets remains zero for every real time.'),
('There the cross-packet entries no longer vanish, and their effect must be controlled rather than hidden by reordering.', 'There the entries coupling the packets no longer vanish, so their effect needs an explicit bound.')],
11:[
('The figure samples closed-form functions for display.', 'The figure displays samples of the explicit functions above.'),
('The bound itself is supplied by the paper\'s theorem, not established by sampling the curve.', 'The paper\'s theorem supplies the bound for all times within its stated scope.'),
('Thus the commutator bound is a worst-case guarantee, not a prediction that leakage rises monotonically forever.', 'The commutator bound therefore limits the largest possible leakage without predicting that it must rise monotonically.'),
('Square it for a normalized-state probability bound,', 'For a normalized state, square it to obtain a probability bound,')],
12:[
('A finite-difference test is unnecessary for this model.', 'The explicit derivatives make a numerical difference approximation unnecessary.'),
('The connection term accounts for that change; it is not an optional force added to the laboratory system.', 'The connection term accounts for that change without adding a force to the laboratory system.')],
13:[
('At $t=0$, the matrices in the plate let the reader verify these identities by multiplying the displayed small arrays.', 'At $t=0$, the displayed small matrices allow these identities to be checked by direct multiplication.'),
('It transports every packet derivative simultaneously.', 'This single connection reproduces the motion of every packet in the family.')],
14:[
('Range-atlas details:', 'Details of the range atlas:'),
('The geometric illustration here is finite-dimensional and orthogonal for transparency; that convenience is not promoted to an extra premise of the recorded theorem.', 'The illustration uses a finite-dimensional orthogonal projector to make the construction visible. Those simplifying choices do not restrict the recorded theorem.')],
15:[
('AN EXACT BLOCH-PROJECTOR CALCULATION', 'AN EXACT BLOCH PROJECTOR CALCULATION'),
('The plate\'s latitude is an illustration of this cap; the formula, not its apparent area on the page, supplies the value.', 'The latitude drawn in the plate illustrates this cap. The exact flux comes from the formula above.'),
('A phase assigned to parallel transport additionally requires an orientation and a connection-sign convention; flux and phase should not be interchanged without those choices.', 'Assigning a phase to parallel transport also requires an orientation and a sign convention for the connection. These choices determine how flux relates to phase.')],
16:[
('Computational-basis dephasing instead removes', 'Dephasing in the computational basis removes'),
('Every computational-basis effect', 'Every effect in the computational basis'),
('It compares their coherent combination, so the paper\'s block-diagonal invariance hypothesis does not apply.', 'It compares their coherent combination, so it falls outside the paper\'s invariance result for block-diagonal effects.')],
17:[
('Keeping only population-transfer arrows would not specify its off-diagonal entries.', 'Arrows that show population transfer alone would leave its off-diagonal entries unspecified.'),
('The complete-positivity certificate', 'How complete positivity is certified'),
('under the unnormalized maximally entangled convention used by the check.', 'under the convention used by the check, which leaves the maximally entangled vector unnormalized.')],
18:[
('a positive single-system matrix', 'a positive matrix on one system'),
('This single exact quadratic-form value certifies failure of positivity on the composite system.', 'This exact negative value of the quadratic form certifies failure of positivity on the composite system.'),
('This argument explains the word \\emph{completely}; checking one input density matrix in the original dimension is not an equivalent test.', 'This argument explains the word \\emph{completely}. The conclusion holds for every auxiliary dimension, which a test of one input density matrix on the original system cannot establish.')],
19:[
('This code corrects the specified single-bit flips. It is not claimed to correct arbitrary errors on three qubits, or even arbitrary single-qubit errors.', 'This code corrects the specified flips of individual bits. That result does not cover arbitrary errors on three qubits or arbitrary errors on a single qubit.')],
20:[
('A harmless-looking syndrome can hide a logical error', 'An unchanged syndrome can hide a logical error'),
('single recovery valid for the whole declared unknown-error family', 'single recovery valid for every unknown error in the declared family'),
('Its trace is zero, but its action on the code is certainly nonzero.', 'Its trace is zero even though its action on the code is nonzero.')],
21:[
('genuine full-resolvent poles.', 'poles of the full resolvent.'),
('The full-invertibility hypothesis is independently necessary.', 'Invertibility of the full matrix is an independent requirement.'),
('The original prose omitted this condition; the preserved amendments restore it.', 'The original prose omitted this condition. The preserved amendments restore it.')],
22:[
('A nonzero hidden initial state would add its own forcing term; it cannot be silently ignored.', 'A nonzero hidden initial state would add a forcing term that must also be retained.'),
('The plotted curves are merely a visualization of these closed-form identities.', 'The curves visualize the explicit solution and its periodic return of amplitude.'),
('Exact elimination trades a hidden coordinate for memory and initial-data forcing.', 'Exact elimination replaces a hidden coordinate with memory and forcing from the initial data.')],
23:[
('The spectrum and positive-definite quadratic form are preserved,', 'The spectrum and positivity of the quadratic form are preserved,'),
('None follows just from two positive eigenvalues.', 'Each of these assumptions requires its own justification beyond the two positive eigenvalues.')],
24:[
('A FOUR-SITE HEAT TRACE IN CLOSED FORM', 'THE EXACT HEAT TRACE ON FOUR SITES'),
('For the four-cycle Laplacian', 'For the Laplacian on a cycle with four sites'),
('its spectral-dimension diagnostic', 'its diagnostic of spectral dimension'),
('Both ends are finite-size regimes', 'Both ends reflect the finite size of the system'),
('two identical four-cycles', 'two identical cycles with four sites'),
('The second curve is not fitted to the first; the product identity determines it.', 'The product identity determines the second curve exactly from the first.'),
('This noninteger value is a scale-dependent spectral quantity,', 'This noninteger value is a spectral quantity that depends on scale,'),
('Larger-grid experiments remain finite diagnostics; convergence requires the analytic hypotheses developed on', 'Experiments on larger grids remain finite diagnostics. Convergence requires the analytic hypotheses developed on')],
25:[
('not by trusting floating-point sine values or fitting a line on a logarithmic plot.', 'without relying on approximate sine values or a fitted logarithmic slope.'),
('Why the low-mode qualification matters', 'Why the mode regime matters'),
('The displayed rational test uses the analytic symbol; it does not assert an integer periodic grid for every chosen spacing.', 'The displayed rational test evaluates the analytic symbol. It does not assert that every chosen spacing defines an integer periodic grid.')],
26:[
('an exact common-kernel projector', 'an exact projector onto the common kernel'),
('This is an important boundary of the diagnostic, recorded by the formal release.', 'The formal release records this limit of the diagnostic.'),
('Before celebrating a vanishing residual, ask whether the way its projector was defined already forced it to vanish.', 'Before interpreting a vanishing residual, check whether the definition of its projector already forces it to vanish.')],
27:[
('One complete calculation: opposite-site transfer', 'One calculation of transfer to the opposite site'),
('Return to the four-site shift', 'Return to the shift on four sites'),
('a single opposite-site output.', 'a single output at the opposite site.'),
('the opposite-site probability', 'the probability at the opposite site')],
28:[
('The plates visualize those calculations; their apparent smoothness or symmetry is not itself proof.', 'The plates make those calculations visible. Their appearance helps explain the result, while the equations and check records supply its evidence.'),
('The stated closed-form rotating and Bloch examples.', 'The explicit rotating and Bloch examples.'),
('Numerical replay &', 'Numerical record &'),
('These are inherited metadata, not a fresh kernel execution.', 'These counts describe the inherited checkpoint. This prose revision includes no new Lean kernel execution.'),
('uniform effective-operator control,', 'uniform control of effective operators,'),
('Choose one page, reproduce its matrix calculation, and then read the cited final-edition theorem with its hypotheses. The original finite and symbolic suite is replayed for this edition, with its exact assertions and rejected controls recorded separately. Fresh standard-library checks and their bounds are described on', 'Choose one page, reproduce its matrix calculation, and then read the cited theorem with its hypotheses. The retained execution records give the exact assertions, tested ranges, and rejected controls for the finite and symbolic suites. The additional examples and their recorded bounds are described on'),
('the channel-family distinction', 'the distinction between a known error and an error family'),
('the common-kernel caveat', 'the limitation of testing only the common kernel')],
29:[
('The standard packet is four-dimensional', 'The standard packet has dimension four'),
('A basis chosen inside the rank-four packet is a coordinate choice; it must not be mistaken for a canonical decomposition into two individual copies.', 'A basis chosen inside this packet supplies coordinates. It does not canonically distinguish the two copies of the standard representation.'),
('What is executed', 'What the retained check establishes'),
('The fresh exact check constructs', 'The retained exact check constructs')],
30:[
('a path-dependent constant in an $O(|\\pi|)$ operator-norm estimate.', 'a constant depending on the path in an $O(|\\pi|)$ estimate in operator norm.'),
('The fresh run checks the Gram identities, polar factor, intertwining, and rational two-step product. It also checks that the orthogonal-endpoint overlap has rank zero.', 'The retained run checks the Gram identities, polar factor, intertwining, and product of two rational steps. It also checks that the overlap has rank zero when the endpoint packets are orthogonal.')],
31:[
('The $00,11$ block is rank one and positive; the other nonzero eigenvalue is $9/25$. The fresh check also verifies every principal minor is nonnegative.', 'The $00,11$ block is positive and has rank one. The other nonzero eigenvalue is $9/25$. The retained check also verifies that every principal minor is nonnegative.'),
('Continuous-time symmetry has its own hypotheses', 'Symmetry in continuous time has its own hypotheses'),
('The finite exponential-series argument in the paper extends generator invariance to its semigroup. No master-equation solver is executed here, and symmetry alone supplies no scalar population closure inside higher-rank packets.', 'The paper uses the finite exponential series to extend generator invariance to the semigroup. The retained calculation uses no numerical solver for the master equation. Symmetry alone does not close the scalar population equations inside packets of higher rank.')],
32:[
('It acts as the identity on code-supported operators', 'It acts as the identity on operators supported on the code'),
('The zero-code case is vacuous and belongs to the separate formal boundary in the saved ledger.', 'The case of a zero code is vacuous and has its own formal statement in the saved ledger.'),
('The exact run verifies all nine', 'The retained exact run verifies all nine'),
('Null branches vanish; a separate complement rule makes the recovery a total channel.', 'Null branches vanish. Specifying the action on the complement makes the recovery a total channel.')],
33:[
('A TWO-POINT OPTIMAL SCALAR PROBLEM', 'THE OPTIMAL SCALAR FOR TWO SPECTRAL POINTS'),
('The displayed triangle argument supplies the all-complex-scalar lower bound; a finite list of candidates cannot do that.', 'The triangle argument proves the lower bound for every complex scalar. Checking a finite list of candidates would not establish that conclusion.')],
34:[
('The upper half-plane sign', 'The sign in the upper half plane'),
('The theorem bounds the actual difference by this common-gap expression. The hypotheses are uniform spectral separation and coupling control; they must be proved for a refinement family before using the bound uniformly.', 'The theorem bounds the difference using a common spectral gap. Applying the bound uniformly to a refinement family requires uniform spectral separation and control of the couplings.'),
('A low-energy series and its actual remainder', 'A series near zero energy and its exact remainder'),
('The geometric-series argument controls the infinite tail. The fresh check verifies that value, the complex sign identity, and the projected-resolvent and bare-truncation identities at four declared real spectral parameters.', 'The geometric series controls the infinite tail. The retained check verifies that remainder, the complex sign identity, and the identities for the projected resolvent and bare truncation at four specified real spectral parameters.'),
('At $z=2$ the hidden inverse fails; at a full eigenvalue the retained Feshbach inverse fails.', 'At $z=2$ the hidden inverse fails. At an eigenvalue of the full Hamiltonian, the retained Feshbach inverse fails.')],
35:[
('TWO HIDDEN FREQUENCIES AND A LOCAL-CLOSURE TEST', 'TWO HIDDEN FREQUENCIES AND A TEST OF LOCAL CLOSURE'),
('This one Gram test illustrates the factorization; the written identity explains positivity for all times and all vectors.', 'This Gram test illustrates the factorization. The written identity proves positivity for all choices of times and vectors.'),
('The checks cover the displayed kernel values, exact Gram factorization, and acceleration defect; no time discretization is used as proof of an integral equation.', 'The retained checks cover the displayed kernel values, exact Gram factorization, and acceleration defect. The integral equation follows from the written elimination argument.')],
36:[
('the entire minimum-energy eigenspace.', 'the entire eigenspace at the minimum energy.'),
('The fresh run checks the exact integer semigroup and diagonal ground error for $n=0,\\ldots,12$, and rejects a full-space logarithm for the singular control. Logarithms and the all-time functional-calculus statement are supplied by the written spectral argument, not by these bounded tests.', 'The retained run checks the integer semigroup and diagonal ground error for $n=0,\\ldots,12$, and rejects a logarithm on the full space for the singular control. The written spectral argument justifies the logarithms and extends the functional calculus statement to all times.')],
37:[
('two tiny grids', 'two small grids'),
('or an all-scale dimension plateau.', 'or a dimension plateau at every scale.'),
('The fixed-time proof bounds centered modes below by', 'At a fixed time, the proof bounds centered modes below by'),
('The fresh check verifies only the displayed two spectra, rational weights, traces, and dimension coefficients. It rejects confusing an unscaled four-cycle spectrum with the unit-circle scaled spectrum.', 'The retained check verifies the two displayed spectra, rational weights, traces, and dimension coefficients. It also distinguishes the unscaled cycle with four sites from the scaled unit circle grid.'),
('The strengthened window result is a convergence statement with a fixed-time choice.', 'The strengthened window result proves convergence after fixing a suitable time.')],
38:[
('The general approximate-transport result controls such residuals and commutator errors using both defect sizes and a common constraint norm bound; it does not replace a nonzero anomaly by an exact algebra.', 'The general result for approximate transport controls these residuals and commutator errors using the defect sizes and a common bound on the constraint norms. A nonzero anomaly remains an error that must be controlled.'),
('The fresh checks verify', 'The retained checks verify'),
('The fine-coordinate counterexample rejects extending an image statement to the whole space.', 'The added coordinate provides a counterexample to extending the identity on the image to the whole space.'),
('Closure is an operator-algebra statement. Refinement intertwining carries that statement on the embedded image; control the new degrees of freedom separately.', 'Closure is a statement about the operator algebra. Refinement intertwining transports it to the embedded image. The new degrees of freedom require their own control.')],
39:[
('On the direct-limit Hilbert space', 'On the Hilbert space of the direct limit'),
('Even-address projectors intertwine as well and give a fixed two-packet complete system in the limit.', 'Projectors onto even addresses also intertwine and give a fixed complete system of two packets in the limit.'),
('It does not meet the bounded direct-limit theorem, although its natural diagonal operator has a separately definable unbounded domain. That domain-sensitive construction is not obtained by dropping the uniform norm hypothesis.', 'It does not satisfy the bounded direct limit theorem. Its natural diagonal operator needs a separately specified domain. Dropping the uniform norm hypothesis does not supply that domain argument.'),
('The summable tail supplies an all-$n$ error bound.', 'The summable tail supplies an error bound for every $n$.'),
('Their infinite conclusion uses the displayed geometric-series argument', 'Their infinite conclusion uses the displayed geometric series'),
('Keep those two contracts explicit.', 'Keep the hypotheses of these two routes explicit.')],
40:[
('This exact check illustrates the finite quadratic-form argument that passes positivity to the limit.', 'This exact check illustrates how finite quadratic forms pass positivity to the limit.'),
('These are positive trace-class operators, used as a topology control; the limiting zero is not a finite-Hamiltonian heat operator.', 'These positive trace-class operators show why the choice of topology matters. Their zero limit is not the heat operator of a finite Hamiltonian.'),
('For actual two-state transfers', 'For transfers on two states'),
('the trace-norm error', 'the error in trace norm'),
('The trace-norm criterion for spectral-dimension convergence', 'The criterion for convergence of spectral dimension'),
('Heat-trace convergence alone', 'Convergence of the heat trace alone'),
('What is fresh, inherited, and still open', 'The retained evidence and the remaining open targets'),
(r"The extension has fresh bounded exact checks in $\QQ(\ii)$ using Python's standard-library \texttt{Fraction}. The original appendix's 180-check record, including its symbolic derivatives, remains available as inherited evidence. The original SymPy suite is replayed for this edition. Its exact assertions and rejected controls remain separate from the extended examples. All original model and vector sources remain supplied.", r"The extension includes retained exact checks over specified finite ranges in $\QQ(\ii)$ using \texttt{Fraction} from Python's standard library. The original appendix's record of 180 checks, including symbolic derivatives, is also retained. Both records come from earlier executions. This prose revision adds no symbolic or Lean kernel run. All model and vector sources remain supplied."),
('The saved v0.6.0 ledger lists 19 finite items; no Lean kernel run or expanded formal coverage is asserted. Its five original continuum/physical targets remain open. The strengthened edition supplies analytic proofs and bounded-limit criteria; neither these examples nor their check counts establish the unresolved physical existence claims.', 'The saved v0.6.0 ledger lists 19 finite items with their recorded hypotheses. Its five original targets for continuum and physical reconstruction remain open. The strengthened edition supplies analytic proofs and criteria for bounded limits. These results and examples do not establish the unresolved physical existence claims.')]
}

source_rels = ['editable/visual_guide/source/pages.tex','editable/visual_guide/source/extended_pages.tex']
page_coverage = []
for rel in source_rels:
    original = (ROOT/rel).read_text()
    pieces = re.split(r'(?=\\vpage\{)', original)
    revised = []
    for part in pieces:
        if not part.startswith(r'\vpage{'):
            revised.append(part)
            continue
        n = int(re.match(r'\\vpage\{(\d+)\}', part)[1])
        before = part
        for old,new in edits[n]:
            part = replace(part,old,new,f'V{n}')
        assert math_spans(before)==math_spans(part),n
        page_coverage.append({'visual_page':n,'source':rel,'reviewed_entire_body':True,
                              'replacements':len(edits[n]),'math_spans':len(math_spans(before)),
                              'math_spans_byte_identical':True})
        revised.append(part)
    save(rel,''.join(revised))

rel = 'editable/visual_guide/source/front.tex'
s = (ROOT/rel).read_text()
front_edits = [
('A compiled Lean theorem certifies its formal statement in the recorded environment. Reading links connect these accounts without enlarging any of their contracts.', 'A compiled Lean theorem certifies its formal statement in the recorded environment. The reading links help compare these accounts while keeping their hypotheses and evidence scopes distinct.'),
('The first 28 worked pages retain the ordered mathematical spans of the original appendix. Twelve further pages explain the strengthened results. All 38 editable TikZ plates and their supplied Python generators remain available. The monograph changes typography, source locators, and evidence wording. The exact example suites are replayed with their bounds and rejected controls recorded in separate execution manifests.', 'The first 28 worked pages retain the mathematical content of the original appendix. Twelve further pages explain the strengthened results. All 38 editable TikZ plates and their Python generators remain available. The retained execution records describe the example suites, their tested inputs, and their rejected controls. This revision improves the prose and layout without presenting those earlier checks as new executions.'),
('The broader quantum development and the five continuum research targets keep their separate written hypotheses. No finite check or picture closes those targets.', 'The broader quantum development retains its written hypotheses, and the five continuum research targets remain open. The examples explain how the finite results work and where further arguments are needed.')]
for old,new in front_edits:s=replace(s,old,new,'Visual front matter','Prose and accurate inherited evidence scope')
save(rel,s)

rel='editable/visual_guide/Paper_VII_Visual_Guide_Final.tex'
s=(ROOT/rel).read_text()
s=replace(s,'The Lean companion records the separate formal contract.','The Lean companion records the formal statements and their precise hypotheses.','Visual opening note')
save(rel,s)

# Synchronize the atlas from the reviewed bodies while preserving the atlas's
# noncircular source locators and all of its setup outside those bodies.
rel='editable/traditional/monograph_atlas.tex'
atlas=(ROOT/rel).read_text()
pat=re.compile(r'\\vpage\{(\d+)\}\{([^\n]*?)\}\{([^\n]*?)\}\{([^\n]*?)\}')
locators={int(m[1]):m[4] for m in pat.finditer(atlas)}
prefix=atlas[:atlas.index(r'\vpage{1}')]
suffix=atlas[atlas.rindex(r'\endgroup'):]
body='\n'.join((ROOT/rel2).read_text().rstrip() for rel2 in source_rels)+'\n\n'
def atlas_heading(m):
    loc=locators[int(m[1])].replace('Range-atlas details:','Details of the range atlas:')
    return r'\vpage{'+m[1]+'}{'+m[2]+'}{'+m[3]+'}{'+loc+'}'
save(rel,prefix+pat.sub(atlas_heading,body)+suffix)

# Only human-readable caption strings change in plates. Every draw command,
# coordinate, font, color, bounding box, and mathematical span is retained.
captions=[
('graphics','seed_rank',r'The stacked rows span $\CC^3$; their local orbits span $\CC^2\otimes\CC^3$.',r'The stacked rows span $\CC^3$. Their local orbits span $\CC^2\otimes\CC^3$.'),
('graphics','parity','Each coarse projector has rank four; all eight fine projectors have rank one.','Each coarse projector has rank four. All eight fine projectors have rank one.'),
('graphics','range_atlas',r'Ranges of $P(\theta)$; the anchor is the horizontal line.',r'The ranges of $P(\theta)$ are shown with a horizontal anchor.'),
('graphics','dephasing',r'$2\rho$; also $2D_{\rm parity}(\rho)$',r'$2\rho$, also $2D_{\rm parity}(\rho)$'),
('graphics_extended','defect',r'one pair: $1/10$; full family $\{I,A\}$: $1/5$',r'one pair: $1/10$, full family $\{I,A\}$: $1/5$'),
('graphics_extended','constraint_image',r'transported closure on $\operatorname{im}R$; new complement requires its own test',r'closure on $\operatorname{im}R$ transfers, and the new complement needs its own test')]
for directory,name,old,new in captions:
    for rel in [f'editable/visual_guide/{directory}/{name}.tex',
                f'editable/traditional/visual_{directory}/{name}.tex']:
        s=(ROOT/rel).read_text()
        s=replace(s,old,new,rel,'Caption prose only, with exact drawing geometry retained')
        save(rel,s)
    rel='editable/visual_guide/source/'+('generate_graphics.py' if directory=='graphics' else 'generate_extensions.py')
    s=(ROOT/rel).read_text()
    s=replace(s,old,new,rel,'Keep generator caption text synchronized')
    # A generator can be touched by several captions. Preserve the first input.
    if rel in changed:
        changed[rel]['after']=s
        (ROOT/rel).write_text(s)
    else:save(rel,s)

# Compare the final atlas with the final standalone prose under locator and
# setup normalization. The regular expressions touch only the heading locator.
def normalized_pages(s):
    s=s[s.index(r'\vpage{1}'):] if r'\vpage{1}' in s else s
    if r'\endgroup' in s:s=s[:s.rindex(r'\endgroup')]
    return pat.sub(lambda m:r'\vpage{'+m[1]+'}{'+m[2]+'}{'+m[3]+'}{LOCATOR}',s).strip()
assert normalized_pages((ROOT/'editable/traditional/monograph_atlas.tex').read_text()) == normalized_pages(body)
assert sorted(r['visual_page'] for r in page_coverage)==list(range(1,41))
assert len(re.findall(r'\\[vx]fig\{',body))==38

files=[];patch=[]
for rel,data in changed.items():
    baseline=(BASE/rel).read_text()
    assert baseline==data['before'],('Unexpected preexisting edit',rel)
    final=(ROOT/rel).read_text()
    assert math_spans(baseline)==math_spans(final),('Math changed',rel)
    files.append({'path':rel,'before_sha256':hashlib.sha256(baseline.encode()).hexdigest(),
                  'after_sha256':hashlib.sha256(final.encode()).hexdigest(),
                  'math_spans':len(math_spans(baseline)), 'math_spans_byte_identical':True})
    patch.extend(difflib.unified_diff(baseline.splitlines(True),final.splitlines(True),fromfile='before/'+rel,tofile='after/'+rel))
(OUT/'PROSE_EDITS.patch').write_text(''.join(patch))
(OUT/'PROSE_REVIEW.json').write_text(json.dumps({
    'status':'SOURCE_PROSE_COMPLETE_AWAITING_PDF_REVIEW',
    'scope':'All 40 visual pages, front matter, visual opening note, and six human-readable plate captions. Atlas bodies synchronized. All 38 figure calls retained.',
    'mathematical_token_changes':[],
    'preservation':'All extracted inline and display mathematical spans byte-identical in every edited source. Drawing geometry, labels, figure calls and page IDs retained.',
    'atlas_body_synchronization':'PASS after locator/setup normalization',
    'evidence_correction':'Replaced stale fresh/replayed-for-this-edition claims with retained earlier execution records. No new scientific, symbolic or Lean kernel execution asserted.',
    'page_coverage':page_coverage,
    'edits':ledger,
    'files':files,
    'validation_pending':'Root rebuilds all final PDFs. This reviewer then inspects all visual pages and atlas pages.',
    'generator_validation':'Caption strings synchronized exactly in active generators. The 12-plate extended generator reproduces all plate sources byte for byte (GENERATOR_REPLAY.json). The original graphics generator requires unavailable SymPy and was not executed.',
    'validation_helper_repair':'The first prose edit transaction stopped at a dollar-sign scanner that mistook a TikZ line break for a math escape. Only the owned sources were restored from the baseline. The scanner now counts preceding backslashes by parity, and the full closed edit list was rerun successfully.'
},indent=2)+'\n')
print(json.dumps({'status':'SOURCE_PROSE_COMPLETE','files':len(files),'replacements':len(ledger),'visual_pages':len(page_coverage),'mathematical_token_changes':0},indent=2))
