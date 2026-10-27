"""Reconcile the preserved August development into the October reader.

The original files are read only. All substantive editorial changes are explicit.
"""
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'evidence/recovered/Projector_Resolved_Hodge_Calculus_Dyadic_Completion_Source/Projector_Resolved_Hodge_Calculus_Dyadic_Completion_Source'
original = (SOURCE / 'Projector_Resolved_Hodge_Calculus_Complete.tex').read_text()
body = original.split('\\mainmatter', 1)[1].split('\\addcontentsline{toc}{part}{Appendices}', 1)[0]

def replace(old, new):
    global body
    if old not in body:
        alternative = re.sub(r'\$([^$]+)\$', lambda m: '\\(' + m.group(1) + '\\)', old)
        if alternative in body:
            old = alternative
    if old not in body:
        raise ValueError('Missing editorial anchor: ' + old[:90])
    body = body.replace(old, new)

replace('Let $V\\subseteq H^{2p}(X,\\R)$ be the Hodge packet under study.',
        'Let $V\\subseteq H^{2p}(X,\\R)$ be the real extension of the rational Hodge packet under study. For the positive frame certificate below, require every $c_j$ to belong to $V$. This can be achieved by a rational algebraic packet projector when such a projector has been constructed. Projection through an arbitrary orthogonal Hodge projector does not establish that the projected vectors are algebraic.')
replace('Choose a polarization-compatible positive inner product on $H^{2p}(X,\\R)$ and let $P_{\\Hdg}^p$ and $P_{\\Alg}^p$ denote orthogonal projectors.',
        'Choose a positive inner product on $H^{2p}(X,\\R)$. The orthogonal projectors $P_{\\Hdg}^p$ and $P_{\\Alg}^p$ act on the real scalar extensions $\\Hdg^p(X)\\otimes_{\\Q}\\R$ and $\\Alg^p(X)\\otimes_{\\Q}\\R$. These real orthogonal projectors provide a reformulation. They are not asserted to be rational matrices or algebraic correspondences.')
replace('The selected cycles span $V$ if and only if $S|_V$ is positive definite.',
        'Under the stated containment $c_j\\in V$, the selected cycles span $V$ if and only if $S|_V$ is positive definite. Without containment, positivity only detects the absence of vectors in $V$ orthogonal to the cycle span and does not prove that span contains $V$.')
replace('Then $A\\supseteq V$ if and only if $\\lambda_{\\min}(G)>0$.',
        'Under $A\\subseteq V$, we have $A=V$ if and only if $\\lambda_{\\min}(G)>0$. Without that containment, use the exact rank certificate $\\operatorname{rank}[C\\ H]=\\operatorname{rank}C$ to test $V\\subseteq A$.')
replace('Equivalently, the Hodge-restricted positive frame has positive minimum eigenvalue.',
        'A positive compressed frame is equivalent only when the supplied cycle vectors lie in the target packet, or when a separately verified invariant restriction supplies the required containment. The rank equality is valid without that extra hypothesis.')
replace('Positive cycle-frame certificate & Proved & Requires an explicit finite cycle family',
        'Positive cycle-frame certificate & Corrected & Requires explicit algebraic cycles contained in the selected packet')
replace('where $Q$ projects onto the range of $L$ and $\\Pi$ onto a finite-dimensional obstruction space. Let $R$ be a right inverse of $L$ on the range.',
        'where $Q$ projects onto the closed range of $L$ and $\\Pi$ onto a finite-dimensional obstruction space. Choose a gauge-fixed complement to $\\ker L$ as the domain and let $R$ be a right inverse of $L$ taking values in that complement. Use norms on the projected data for which $\\|QB(a,b)\\|\\le C\\|a\\|\\|b\\|$.')
replace('unique fixed point in the ball $\\|a\\|\\le2M\\|Qf\\|$.',
        'unique fixed point in the gauge-fixed ball $\\|a\\|\\le2M\\|Qf\\|$. If $Qf=0$, the ball is the singleton $\\{0\\}$ and the range solution is immediate.')
replace('Suppose the codimension-$p$ components are $Z_1,\\ldots,Z_r$. Purity gives',
        'Suppose $Z$ has codimension at least $p$ and its codimension-$p$ components are $Z_1,\\ldots,Z_r$. Purity gives')
replace('This permits a complete symbolic analysis of addresses, conductors, local prime phases, and candidate algebraic correspondences.',
        'This permits exact symbolic analysis of individual addresses, conductors, local prime phases, and candidate algebraic correspondences. A complete classification at every mixed conductor is a separate coverage problem.')
replace('Kang states a published generalized-Hodge theorem covering every degree',
        'Kang is cited in the checked later literature as proving the relevant generalized Hodge statement in arbitrary degree')
replace('the all-degree trivalent-tree uniqueness theorem',
        'the proposed all-degree trivalent-tree classification')
replace('Rational packets correspond to \\(U_m\\)-orbits in \\(\\mathcal B_m\\).',
        'After additionally identifying coordinate permutations by algebraic automorphisms, the count-vector descriptions correspond to \\(U_m\\)-orbits in \\(\\mathcal B_m\\). The dimension of a fixed rational character packet is computed from distinct ordered unit conjugates before this permutation quotient.')
start = body.index('Under the standard associative Fermat join formalism, (9.2)')
end = body.index('\\section{Dual charges}', start)
body = body[:start] + r'''The algebraic implication must use the actual classical correspondence operations. A balanced four-entry packet is algebraic by Lefschetz $(1,1)$ on a Fermat surface. Concatenate the $N$ surface characters using the Shioda--Ran construction, then remove precisely the $2N-3$ complementary pairs by the classical pair-removal theorem. The ambient dimension rises to $4N-2$ before cancellation. This proves algebraicity of a packet admitting such an identity once those cited operations and their character conventions have been checked. It does not authorize cancellation of arbitrary tensor factors. The August 15 status note correctly demanded a complete correspondence-level account of the proposed general grammar. The concrete degree-210 application below spells out the necessary stabilization and uses only the checked pair-removal theorem.

''' + body[end:]
start = body.index('Because the graph is defined over')
end = body.index('\\begin{figure}', start)
body = body[:start] + r'''The Laurent exponent match is a useful exact certificate, but by itself it does not prove that a rational class lifts through a compact graph. A complete manuscript argument instead uses the torus-carrier criterion developed in Chapter~\ref{ch:carrier70}. For the reordered character, the exponent matrix $A$ of the cubic satisfies
\[
A^T\widetilde a/33=\beta=(1,2,2,1,1,2),\qquad C=33A^{-1}.
\]
With $r_0$ the first row of $A$, put $u=\beta-3r_0$. Then $\mathbf1^Tu=0$ and $C^Tu=\widetilde a-99e_0$. These identities establish triviality of the selected character on the torus deck group. Every selected character has full support, so its restriction to the coordinate torus is an isomorphism on the packet. Finite étale descent gives a pure rational weight-four Hodge substructure on the cubic torus. The lowest-weight image theorem and semisimplicity give a rational $(2,2)$ lift to the smooth cubic. Classical cubic algebraicity then supplies a surface class. Pull back through a resolved graph, apply the rational orbit projector, and use boundary injectivity to identify the returned class.

\begin{manuscriptclaim}[Degree-33 packet construction]
Subject to the resolved graph and the cited mixed-Hodge inputs in the preceding argument, the rational packet generated by $(7,10,13,19,22,28)$ is algebraic on $X_{33}^4$. The exponent identities are finite exact certificates. The compact geometric implication is a manuscript argument and is not certified by those identities alone.
\end{manuscriptclaim}

''' + body[end:]
replace('The resulting Klein--Delsarte map then seeds infinite conductor towers.',
        'A completed Klein--Delsarte correspondence supplies a seed for infinite conductor towers.')
replace('In particular, the degree-33 exceptional packet yields a 20-dimensional algebraic packet on every $X_{33k}^4$.',
        'Applied to the preceding degree-33 construction under its geometric hypotheses, this gives a 20-dimensional algebraic packet on every $X_{33k}^4$.')

# The later August 15 source explicitly downgraded uniform dyadic coverage.
dyad_start = body.index('\\chapter{Weighted dyadic reconstruction}')
dyad_end = body.index('\\chapter{Finite global audit through degree 100}', dyad_start)
dyad = body[dyad_start:dyad_end]
dyad = dyad.replace('The remainder of this chapter proves that this orbit is the only one in every dyadic degree.',
    'The remaining derivation proposes an all-degree explanation. Its uniform status was downgraded by the later August 15 note, so this edition preserves the argument as a manuscript claim requiring a complete audit.')
for env in ('theorem','proposition','lemma','corollary'):
    dyad = dyad.replace('\\begin{'+env+'}', '\\begin{manuscriptclaim}').replace('\\end{'+env+'}', '\\end{manuscriptclaim}')
dyad = dyad.replace('\\begin{resultbox}[Dyadic target closed]', '\\begin{resultbox}[Uniform dyadic status]')
dyad = dyad.replace('The former ``uniform dyadic uniqueness\'\' assumption is now a theorem. Its proof is independent of the finite search: it uses an integral triangle basis, an exact total-variation model on a trivalent tree, discrete coarea, and the conductor of the unique four-star obstruction.',
    'The August 6 manuscript called uniform uniqueness closed. The August 15 status note restored it to a uniform write-up obligation. The proposed proof uses an integral triangle basis, an exact total-variation model, discrete coarea, and star conductor. This edition does not reverse the later downgrade on the strength of finite agreement.')
dyad = dyad.replace('corroborate the theorem but are not used in place of its proof.',
    'support the finite identities. They do not supply a current independent proof of the all-degree claim.')
body = body[:dyad_start]+dyad+body[dyad_end:]
replace('All named verification groups pass:', 'The archived named verification groups report the following outcomes:')
replace('The dyadic weighted identity passes \\(89{,}478{,}480\\) coefficient checks through \\(2^{14}\\). The exact packet audit is complete through degree \\(100\\) for the implemented grammar.',
        'The archived dyadic report records \\(89{,}478{,}480\\) coefficient checks through \\(2^{14}\\). The October replay independently checked 87,376 coefficients for exponents $3\\le s\\le9$. The larger historical count was not rerun in full. The archived packet audit reports completeness through degree \\(100\\) for its implemented grammar, which is not a completeness theorem for all correspondence channels.')
replace('and reduce \\(C,D\\) modulo \\(q\\) to positive representatives \\(c,d\\). Define',
        'and reduce \\(C,D\\) modulo \\(q\\) to representatives \\(c,d\\). Require $c,d,e$ to be nonzero modulo $q$ so that all three resulting character blocks have full support. Degenerate cases must leave this construction and be handled through pair removal or another channel. For example $(1,14,2,9,14,5)$ at modulus 15 is balanced and admits the indicated phase split, but $P=(1,14)$ gives $c=0$. The phase condition alone is insufficient. Define')
replace('At the motive level, write\n\\[\nN=M(C_P)\\otimes M(S_T).\n\\]',
        'After fixing a common cyclotomic coefficient field and a diagonal character projector, write the selected factor schematically as\n\\[\nN=e_{\\mathrm{diag}}\\bigl(M(C_P)\\otimes M(S_T)\\bigr).\n\\]\nAn ordinary tensor product of rational packets contains off-diagonal embedding pairs and is generally not rank one. Rank one here refers only to a selected eigenspace after scalar extension. The coefficient field and projector are part of the unresolved correspondence specification.')
start = body.index('Let \\(F_d\\) be the Fermat curve of the minimal CM conductor')
end = body.index('\\chapter{Correct literature and novelty map}', start)
body = body[:start] + r'''For an audited CM type, the lower Fermat curve provides a candidate rational character-orbit factor of its Jacobian. Write $e_{\mathrm{orb}}J(F_d)$ for that factor, up to isogeny. The idempotent selects the complete rational Galois orbit. A projector onto just one holomorphic CM half-plane would not be rational and is not an algebraic rational packet projector.

The desired correspondence is schematically
\[
\Gamma\in\CH^{\ast}(F_d\times C_P\times S_T)_{\Q},\qquad
\Gamma_*:e_{\mathrm{orb}}H^1(F_d)\longrightarrow
e_{\mathrm{diag}}\bigl(M(C_P)\otimes M(S_T)\bigr)(1).
\]
This formula is a target specification, not a constructed map. Its coefficient field, diagonal projector, rational multiplicities, and dimensions must be fixed before an isomorphism can be asserted. The smaller CM conductor can have a smaller rational degree than the original packet. Matching sign functions alone does not resolve that difference.

After the typing has been supplied, a nonzero equivariant map between corresponding rank-one eigenspaces is an isomorphism over the splitting field. Proving that the map is induced by an algebraic correspondence remains essential. One needs a Kummer or half-twist correspondence with the correct covariance and a nonzero period or intersection coefficient. Tensoring a verified map with the conjugate lower curve packet can then place a class in divisor degree on a product of curves or abelian varieties. Lefschetz $(1,1)$ and actual Fermat join maps would transport it back.

\begin{openproblem}[Typed CM packet correspondence]
Specify the fields, projectors and rational multiplicities, construct the algebraic map, and prove its nonzero character coefficient. The 364 audited sign certificates identify candidate factors. They do not solve this problem. The finite-field Chow-motive constructions of Otsubo and Yamazaki provide related context, and are not a characteristic-zero correspondence proof for these packets \cite{OtsuboYamazaki}.
\end{openproblem}

''' + body[end:]
replace('a weighted dyadic recursion and an all-degree uniqueness theorem with one SAT(3) orbit',
        'a weighted dyadic recursion and a proposed all-degree classification with one SAT(3) orbit')
replace('The final universal constructive theorem is the explicit CM packet correspondence, not the abstract equality of Hodge and algebraic subspaces.',
        'Universal constructive coverage also requires a complete mixed-conductor grammar. The typed CM correspondence is one focused gap inside that larger problem.')
replace('The universal dyadic uniqueness statement is not inferred from these checks; it is proved in Chapter 13 by the integral triangle basis and trivalent-tree coarea argument.',
        'The proposed dyadic uniqueness statement is not inferred from these checks. Its manuscript derivation is preserved with the later uniform-write-up downgrade.')
replace('Assume the following correspondence statements:',
        'Fix a packet that is admitted by the implemented certificate grammar. Assume the following correspondence statements for its chosen channel:')
replace('Then every rational middle Hodge packet on every Fermat fourfold has an explicit packet-resolved algebraic cycle representative.',
        'Then that packet has an explicit packet-resolved algebraic cycle representative. A conclusion for every Fermat fourfold packet additionally requires universal mixed-conductor coverage by this grammar, which has not been proved here.')
replace('Classify the seed by the pair, saturation, curve, Delsarte, dyadic, or Kummer phase grammar.',
        'Use the supplied grammar certificate for the seed, whether pair, saturation, curve, Delsarte, dyadic, or a Kummer phase channel.')
replace('Finally sum the Galois orbit to obtain a rational cycle.',
        'Finally use the rational orbit projector or rational group-module reconstruction. A bare sum of all complex conjugate eigenvectors may vanish and is not a substitute for that rational construction.')
replace('Dyadic weighted classification & Complete & Triangle basis, trivalent coarea, star conductor',
        'Dyadic finite identities & Replayed in a bounded range & Weighted coefficient identities and finite tree data')
replace('K23 local phase classification & Complete & Pair--triple lemma',
        'K23 local phase reduction & Audited instances & Pair--triple identity with nonzero-entry conditions')
replace('All-degree constructive algorithm & Conditional & Assemble all correspondence channels',
        'All-degree constructive algorithm & Open & Universal coverage plus all required correspondence maps')
replace('The odd prime-power classification and the all-degree dyadic trivalent-tree theorem show that local primes impose distinct packet grammars.',
        'The odd prime-power manuscript classification and the proposed dyadic tree derivation explain why local primes require distinct packet grammars.')
replace('The mixed-prime residuals resolve into a finite Kummer phase system.',
        'The audited mixed-prime residuals display a small Kummer phase system, without a proof that these patterns exhaust arbitrary conductors.')
replace('Construct one nonzero equivariant Chow correspondence between the explicit CM carrier and each remaining packet factor.',
        'Construct a correctly typed nonzero equivariant Chow correspondence for each admitted CM packet, and separately prove universal coverage of the certificate grammar.')

# Remove old-font figures and obsolete status illustrations. The first 32 were
# rebuilt in an isolated working copy. New guide figures cover the later layers.
def filter_figure(match):
    block = match.group(0)
    found = re.search(r'\{(\d\d)_[^}]+\.pdf\}', block)
    replacements={
      2:('03_fourfold_middle','Hodge bidegree positions for a fourfold. The diagram gives indices rather than numerical Hodge dimensions.'),
      4:('04_projector_diagnostic','The real orthogonal obstruction is a diagnostic reformulation. An algebraic realization of the full Hodge projector is not supplied.'),
      6:('06_corrected_rational_frame','A finite rational frame example with its cycle vectors contained in the selected target. Actual geometric applications must supply algebraic vectors with verified cohomology coordinates.'),
      11:('07_positive_polyphase','Positive parent-child frame assembly. The identity combines frames without assuming their ranges are orthogonal.'),
      14:('08_support_verification','The restriction-to-complement test verifies a supplied support. It does not construct a support for an arbitrary Hodge class.'),
      15:('09_correspondence_degrees','The exact degree shifts required for lowering to divisor degree and returning. Actual Chow kernels and invertibility are additional inputs.'),
      18:('10_rational_inverse','A finite rational example of polynomial inversion. The geometric theorem requires the operator to be induced by algebraic correspondences.'),
    }
    if found and int(found.group(1)) in replacements:
        stem,caption=replacements[int(found.group(1))]
        return r'\begin{figure}[tbp]\centering\includegraphics[width=0.98\linewidth]{'+stem+r'.pdf}\caption{'+caption+r'}\end{figure}'
    return ''
body = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', filter_figure, body, flags=re.S)
new_figures=[
 ('\\chapter{Exact conductor polyphase}','11_balanced_orbit70','Every ordered unit conjugate of the named degree-70 character has sum 210. This exact example identifies Hodge type and does not itself construct a cycle.'),
 ('\\chapter{Algebraic certificate grammar}','12_conductor_descent','Exact conductor descent in the named example. Coordinate-power inflation enlarges the ambient degree while preserving the old conductor.'),
 ('\\chapter{Infinite towers and full-conductor promotion}','15_klein33_route','The degree-33 torus/cubic construction requires deck invariance, full-support boundary control, a rational Hodge lift and the resolved algebraic graph.'),
 ('\\section{Complement defects and dyadic triangles}','13_dyadic_sat3','The three finite dyadic representatives have exact SAT(3) identities. These identities do not prove all-degree grammar coverage.'),
 ('\\section{The integral triangle basis}','14_dyadic_tree32','The finite degree-32 defect tree. The proposed uniform derivation is retained separately with its publication-status boundary.'),
 ('\\chapter{Imaginary CM selector}','16_k23_factorization50','A valid finite K23 factorization at modulus 50, with all required character entries nonzero.'),
 ('\\chapter{Explicit carrier and remaining Chow map}','17_cm_imaginary_sign','The exact imaginary selector sign in a retained example. Matching signs does not construct a rational Chow correspondence.'),
 ('\\chapter{Correct literature and novelty map}','18_missing_chow_bridge','The typed algebraic CM bridge is an open construction. Coefficient field, projectors, multiplicities and nonzero period are part of the target.'),
]
for anchor,stem,caption in new_figures:
    if anchor in body:
        fig=r'\begin{figure}[tbp]\centering\includegraphics[width=0.98\linewidth]{'+stem+r'.pdf}\caption{'+caption+r'}\end{figure}'
        body=body.replace(anchor,fig+'\n\n'+anchor)
body=body.replace('A nilpotent block gives the elementary counterexample.',
    'For example, $N=\\left(\\begin{smallmatrix}0&1&0\\\\0&0&1\\\\0&0&0\\end{smallmatrix}\\right)$ is nonzero, while $N^3=0$ and $\\operatorname{Tr}(N^r)=0$ for every positive integer $r$. This is the elementary negative control.')
body = body.replace('M"obius', 'M\\"obius')
body = body.replace('It is nonzero in the degree-three Jacobian ring. The residue pullback has the exact exponent identity',
    'Its exponent vector is $b=(0,1,1,0,0,1)$. Write $C=33A^{-1}$ for the cubic exponent matrix $A$. The class is nonzero in the degree-three Jacobian ring. The residue pullback has the exact exponent identity')
body = body.replace('p{0.43\\textwidth}p{0.17\\textwidth}p{0.32\\textwidth}', 'p{0.42\\textwidth}p{0.17\\textwidth}p{0.32\\textwidth}')
body = body.replace('The companion verifier \\path{data/Fermat_Hodge_Dyadic_Uniqueness_VERIFICATION.json} independently reproduces the complete orbit counts through \\(m=128\\), identifies exactly the three displayed representatives at \\(m=32,64,128\\), checks the tree/SAT(2) criterion against exhaustive certificate search, and audits the structural identities through \\(2^{14}\\).',
    'The archived companion dyadic verification report records complete orbit counts through $m=128$ and structural identities through $2^{14}$. The October replay freshly reconstructs the complete census through 128 and the triangle/tree identities through $2^9$. The report file is preserved evidence, rather than an executable verifier or a current replay of the larger historical range.')
body = body.replace('\\chapter{The next realistic theorem: multi-incidence saturation}', '\\chapter{A focused multi-incidence target}')
body = body.replace('Kang states a generalized-Hodge theorem for Fermat varieties of dimensions three and four in arbitrary degree',
    'Kang is cited in the checked later literature for the all-degree Fermat-fourfold Hodge result, while its original exact theorem and proof were not extracted here')
body = body.replace('is the orthogonal projector onto $\\Hdg^p(X)\\cap\\Alg^p(X)^\\perp$.',
    'is the orthogonal projector onto $(\\Hdg^p(X)\\otimes_{\\Q}\\R)\\cap(\\Alg^p(X)\\otimes_{\\Q}\\R)^\\perp$.')
body = body.replace('use the exact rank certificate $\\operatorname{rank}[C\\ H]=\\operatorname{rank}C$',
    'use a rational basis matrix $H_{\\Q}$ for the target and the exact certificate $\\operatorname{rank}_{\\Q}[C\\ H_{\\Q}]=\\operatorname{rank}_{\\Q}C$')
body = body.replace('a\\in\\mathcal B_m', 'n(a)\\in\\mathcal B_m')
body = body.replace('Consequently\n\\[\\mathcal B_m', 'Consequently\n\\[\\mathcal B_m')
body = body.replace('Writing \\(a=g(a)b\\), the coordinate-power map',
    'For a count vector, $L_k$ denotes scaling each residue entry by $k$ while multiplying the modulus by $k$. Writing \\(a=g(a)b\\), the coordinate-power map')
body = body.replace('If \\(w(n)\\ne0\\),', 'Writing $w(n)=\\sum_r n_r w(r)$, if \\(w(n)\\ne0\\),')
body = body.replace('This formulation is the basis for the prime-power classification and the conductor-defect tree.',
    'Here $n(a)$ is the residue count vector. This formulation underlies the prime-power filtration and the proposed conductor-defect tree.')
body = body.replace('The odd prime-power classification follows from a primitive-character filtration and a six-entry mass bound.',
    'The following manuscript classification uses a primitive-character filtration and a six-entry mass bound. At filtration level one the kernel-to-lower-level argument must be replaced by the base-prime Fourier argument stated below.')
body = body.replace('Primitive odd characters force \\(\\delta_j\\) to be constant on the kernel cosets of',
    'For $s\\ge2$, primitive odd characters force \\(\\delta_j\\) to be constant on the kernel cosets of')
body = body.replace('\\section{Large odd primes}',r'''At $s=1$, all odd characters modulo $p$ are primitive. Their sawtooth Fourier coefficients are nonzero, so the odd count vector has every Fourier coefficient zero and is zero. This gives complementary pairing at the base prime level. The higher-level mass argument applies only for $s\ge2$. The needed odd-character nonvanishing is a classical analytic leaf, checked through Sharifi's cyclotomic-field notes \cite{SharifiDirichlet}.

\section{Large odd primes}''')
body = body.replace('At \\(p=3\\), a kernel orbit has three elements.',
    'For $p=3$ and $r\\ge2$, a higher-level kernel orbit has three elements.')
body = body.replace('The packet \\(\\Gamma_b\\) is a balanced four-packet.',
    'Take $1\\le b<q$ with $3\\nmid b$, ensuring all entries are nonzero. Then \\(\\Gamma_b\\) is a balanced four-packet.')
body = body.replace('At \\(p=5\\), a nonzero odd defect consumes exactly five unit entries.',
    'For $p=5$ and $r\\ge2$, a nonzero odd defect consumes exactly five unit entries. The base case $r=1$ was already handled by the base-prime Fourier argument.')
body = body.replace('Let \\(m=2^s\\) and \\(h=2^{s-1}\\).',
    'Let $s\\ge3$, \\(m=2^s\\), \\(h=2^{s-1}\\), and write $\\rho_s=\\rho_{2^s}$.')
body = body.replace('\\sum_{r\\in\\gamma}w(r)=0', '\\sum_r\\gamma_r w(r)=0')
body = body.replace('\\prod_{a\\in\\{c,d,e\\}}', '\\prod_{j=1}^3')
body = body.replace('\\sin\\frac{\\pi\\langle ua\\rangle_q}{q}', '\\sin\\frac{\\pi\\langle u\\ell_j\\rangle_q}{q}')
body = body.replace('Every sine factor is positive,', 'Here $(\\ell_1,\\ell_2,\\ell_3)=(c,d,e)$ is an indexed triple, so repeated residues contribute repeated factors. Every sine factor is positive,')
body = body.replace('\\begin{theorem}[Exact K23 packet identity]',
    'For any nonzero-entry block $B$ at modulus $m$, put $h_B(u)=m^{-1}\\sum_{r\\in B}\\langle ur\\rangle_m$, with multiplicities retained.\\n\\n\\begin{theorem}[Exact K23 packet identity]')
body = body.replace('The most concentrated target is the rank-one CM map (17.1).',
    'A concentrated target is the correctly typed CM correspondence specified above. Universal mixed-conductor coverage is a separate obligation.')
body = body.replace('every K5, K4, and K23 local phase packet has its prescribed Kummer--Schur or CM half-twist Chow correspondence',
    'every K5, K4, and K23 packet used by the chosen certificate has its correctly typed Chow correspondence with a proved nonzero character coefficient')
body = body.replace('These statements are compatible if the latter concerns explicit or restricted constructions rather than abstract existence, but the literature relation should be audited before publication.',
    'The October source contracts authenticate the Kang attribution through the checked later literature while recording that its original proof was not extracted. No historical priority claim is made for this constructive program.')
body = body.replace('several explicit new or potentially new correspondences',
    'several explicit manuscript correspondence constructions, without a historical novelty claim')
body = body.replace('The Fermat extension adds:', 'The archived Fermat extension reports the following historical checks, whose fresh replay ranges are distinguished in the current evidence chapter:')
body = body.replace('WashingtonCyclotomic}', 'WashingtonCyclotomic,SharifiDirichlet}')
body = body.replace('\\le MC(\\|a\\|+\\|b\\|)\\|a-b\\|<\\|a-b\\|.',
    '\\le MC(\\|a\\|+\\|b\\|)\\|a-b\\|.\\n\\]\\nThe Lipschitz constant is strictly less than one on the stated ball.\\n\\[')
# Convert inherited formula tags to genuine equation labels, so prose references
# resolve against this edition's chapter numbering.
def number_legacy(match):
    content=match.group(1)
    tag=re.search(r'\\tag\{([^}]+)\}',content)
    if not tag:return match.group(0)
    key='legacy-'+tag.group(1)
    content=content.replace(tag.group(0),'').strip()
    return '\\begin{equation}\\label{eq:'+key+'}\n'+content+'\\end{equation}'
body=re.sub(r'\\\[(.*?)\\\]',number_legacy,body,flags=re.S)
for tag in ('7.1','7.2','7.3','8.1','8.2','8.3','9.1','9.2','10.1','12.1','12.2','13.1','13.2','13.3','13.4','13.5','13.6','13.7','15.1','16.1','16.2','16.3'):
    body=body.replace('('+tag+')','\\eqref{eq:legacy-'+tag+'}')
body = body.replace(';', ',')
body = body.replace('with multiplicities retained.\\n\\n\\begin{theorem}', 'with multiplicities retained.\n\n\\begin{theorem}')
body = body.replace('\\|a-b\\|.\\n\\]\\nThe Lipschitz constant is strictly less than one on the stated ball.\\n\\[\n\\]',
    '\\|a-b\\|.\n\\]\nThe Lipschitz constant is strictly less than one on the stated ball.')
body = body.replace('\\begin{center}\n\\input{tables/', '\\begin{center}\n\\small\n\\input{tables/')
(HERE / 'august_development.tex').write_text(body)
for table in (SOURCE / 'tables').glob('*.tex'):
    shutil.copyfile(table, HERE / 'tables' / table.name)

# Regenerate the original finite illustrations, without changing the preserved
# source or reclassifying their floating-point checks as exact mathematics.
script = (SOURCE / 'scripts/projector_resolved_hodge_calculus.py').read_text()
script = script.replace("'figure.facecolor': PAPER,", "'pdf.fonttype': 42,\n    'ps.fonttype': 42,\n    'figure.facecolor': PAPER,")
colors = {'#17202A':'#243138', '#2E86AB':'#21676B', '#2A9D8F':'#21676B', '#F4A261':'#A45C36', '#E76F51':'#A45C36', '#6C5CE7':'#627078', '#A23E8C':'#627078', '#E9C46A':'#C29A70', '#FBFBF8':'#FFFFFF'}
for old,new in colors.items(): script = script.replace(old,new)
(HERE / 'historical_assets/projector_illustrations.py').write_text(script)
print('October mathematical development reconciled, historical source unchanged')
