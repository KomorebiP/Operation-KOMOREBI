"""Reading aids for the retained Euler plots; recorded data are projected only."""

DESCRIPTIONS={
 'normalization':('Reciprocal series and factorial normalization',
    'Three boxes run downward from the normalized source series to its reciprocal coefficients and then to the original Euler coefficients. The first arrow takes a reciprocal. The second multiplies by the address factorial. A row step corresponds to the section width times that step in Euler degree.'),
 'threshold':('Earlier and threshold-free valuation bounds',
    'The two heat maps use starting rows zero through twelve horizontally and difference orders one through twelve vertically. The earlier bound is the smaller of the order and starting row. The new bound is the order throughout each horizontal strip. The dashed diagonal marks equality of the row and order. Colors represent proved bounds, not sampled coefficient valuations.'),
 'mixed_stencil':('The eight signed offsets for steps one, two and four',
    'Each offset from zero through seven has one signed weight, above or below the zero line. The weights come from the exact subset expansion of three commuting differences. The following table retains the offsets and weights from the recorded exact data.'),
 'final_exponents':('Original Euler congruence exponents at unit step',
    'The horizontal axis is difference order, one through thirty-two; height is bits of divisibility for the original Euler coefficients. Addresses zero and one share an exact curve. Address three has a proved lower bound. Address two has the larger lower bound, with exactness marked at powers of two. The table uses the recorded theorem-derived arrays.'),
 'address_two_envelope':('The two normalized address-two bounds and their envelope',
    'The dashed curve is the constant-surplus bound. The dotted curve adds the paired-filtration gain. The solid curve takes their maximum. Powers of two mark the universally exact orders. These are normalized coefficients; the original Euler normalization adds one to the displayed bounds.'),
 'mixed_cancellation':('Factorial baseline and exact valuations for six pairs of steps',
    'Paired bars compare the factorial baseline with the exact valuation at starting row zero and address zero. A taller exact bar records additional cancellation. The table gives the six pairs and their recorded values; the parity criterion in the source explains when equality holds at every starting row.'),
 'metric':('First-difference valuation against step valuation',
    'Four lines have slope one, with original Euler scale offsets one, one, five and three for addresses zero through three. Addresses zero and one overlap. Points at step valuations zero through six illustrate the exact arithmetic. The line law is universal; these displayed points are finite illustrations.'),
 'periods':('Binary logarithms of least row periods',
    'For precision exponents one through twelve, each staircase is zero until precision exceeds its address scale and then rises by one per bit. Addresses zero and one share a staircase. Height zero means row period one, not period zero. Euler degree periods are four times the row periods.'),
 'residue_permutations':('Four exact residue permutations modulo 256',
    'The four panels have periods 128, 128, 8 and 32. The horizontal coordinate is row index over one full period. The vertical coordinate subtracts the address factorial and divides by the known power-of-two scale before reducing to the period. Every allowed scaled residue occurs once. The tables retain every plotted row, Euler residue and scaled residue.'),
 'isometry_matrices':('Input and output low-bit precision matrices for address two',
    'Both eight-by-eight matrices show the valuation of a difference between two rows. The right matrix uses the scaled output residues from the address-two permutation. Their colors agree at every off-diagonal position. Blank diagonals mean the infinite valuation of zero. The recorded input-output pairs below identify all eight rows without interpreting the blank diagonal as a finite number.'),
 'rank_scales':('Normalized and Euler scales at ranks two, four and eight',
    'Two arrays place section rank on the vertical axis and address zero through seven on the horizontal axis. Blank cells are outside the permitted address range. The left entries are normalized scales; the right entries add the valuation of the address factorial. These proved arrays do not extend the same metric law to every higher-rank address.'),
 'analytic_slopes':('Positive-degree Taylor coefficient valuation bounds',
    'The degree axis runs from one through sixty-four. Addresses zero and one have exact valuation equal to degree. Address three has that same proved lower bound. The address-two lower envelope grows more steeply; powers of two from four onward mark exact values. Degree zero is excluded. The source gives an exact radius for address two and a lower bound for address three.'),
 'worked/reciprocal_rows':('Exact reciprocal coefficients at rank four',
    'The four rows correspond to addresses zero through three. Columns give the normalized reciprocal at rows zero, one and two as exact rational values. They are retained from the worked-example result record.'),
 'worked/normalization_loss':('A factorial changes the three-adic difference valuation',
    'The normalized difference has value 64/455 and valuation zero. Multiplication by the address factorial gives original Euler difference 384/455 and valuation one. The dashed level is one. This example concerns width six and address three.'),
 'worked/odd_prime_sign':('Untwisted and sign-twisted coefficients at width three',
    'Rows zero, one and two compare the original normalized coefficients with their alternating-sign twist. The untwisted first difference is minus two, a three-adic unit. The twisted first difference is zero, with infinite valuation. The next twisted difference is eighteen.'),
 'worked/newton_cutoff':('Newton coefficient valuations and the eight-bit cutoff',
    'Points show the recorded Newton valuations for orders one through sixteen at rank four, address zero. The dashed line is eight bits. Orders five and above lie at or above it. The source uses the coefficient theorem for the uniform truncation and separately records finite reconstruction checks through row thirty-two.'),
 'worked/smooth_tower':('Five successive compatible three-adic root corrections',
    'Rows give the first five stages for a root of x squared minus seven, starting at one modulo three. Each row shows the precision modulus, current representative, correcting digit and next representative. A zero correcting digit preserves compatibility and does not stop the construction.'),
 'worked/singular_block':('All three candidate digits fail to lift the singular root',
    'For x squared minus three, the old root class is zero modulo three. The candidates zero, three and six all leave residue six modulo nine. The table displays every possible next digit and the exact residual. The source also distinguishes singularity with a zero obstruction, where lifts can exist.'),
 'worked/shared_obstruction':('Available shared residuals miss the required zero vector',
    'The required residual is marked at the origin. The three available shared digits give residual pairs (0, 2), (1, 0) and (2, 1). Each coordinate can vanish separately, but no shared digit makes both vanish. The axes are the first and second residuals modulo three.'),
 'worked/weighted_motion':('One digit of precision is lost in root displacement',
    'For the displayed exponents two through seven, coefficient precision is the exponent, while root displacement precision is one less. Both lines rise with slope one. The derivative has valuation one, and the source derives the loss exactly from the two linear equations.')
}


def data_tables(name,exact,worked):
    """Copy retained finite data. No coefficient, lift or congruence is recomputed."""
    table=lambda caption,headers,rows:dict(caption=caption,headers=headers,rows=rows)
    if name=='mixed_stencil':
        return [table('Exact signed stencil',['Offset','Signed weight'],exact['mixed_stencil']['offset_weights'])]
    if name=='final_exponents':
        data=exact['theorem_derived_unit_step_exponents']
        return [table('Recorded theorem-derived unit-step exponents',['Order','Addresses 0 and 1 (exact)','Address 2 (lower bound)','Address 3 (lower bound)'],list(zip(data['orders'],data['Euler_j01'],data['Euler_j2'],data['Euler_j3'])))]
    if name=='mixed_cancellation':
        return [table('Recorded mixed order-two examples',['Steps','Baseline','Exact valuation','Exact difference'],[[str(tuple(r['steps'])),r['lower'],r['actual'],r['value']] for r in exact['mixed_order_two']])]
    if name in ('residue_permutations','isometry_matrices'):
        records=exact['residue_permutations'] if name=='residue_permutations' else [exact['residue_permutations'][2]]
        return [table('Address '+str(r['j'])+': recorded residues modulo 256',['Row','Euler residue','Scaled residue'],[[i,e,y] for i,(e,y) in enumerate(zip(r['Euler_residues'],r['scaled_residues']))]) for r in records]
    if name=='worked/reciprocal_rows':
        return [table('Exact reciprocal rows',['Address','C(0)','C(1)','C(2)'],[[j,*r] for j,r in enumerate(worked['first_rows'])])]
    if name=='worked/normalization_loss':
        return [table('Retained normalization witness',['Quantity','Exact value'],list(worked['normalization'].items()))]
    if name=='worked/odd_prime_sign':
        return [table('Exact sign correction',['Row','Untwisted C(n)','Sign-twisted C(n)'],[[i,c,t] for i,(c,t) in enumerate(zip(worked['sign']['C'],worked['sign']['twisted']))])]
    if name=='worked/newton_cutoff':
        return [table('Recorded Newton valuations',['Order','Valuation'],[[k,v] for k,v in enumerate(worked['newton']['valuations'][1:17],1)])]
    if name=='worked/smooth_tower':
        return [table('First five recorded root corrections',['Stage','Modulus','Current representative','Digit','Next representative'],[[r[k] for k in ('L','modulus','x','digit','next')] for r in worked['tower'][:5]])]
    if name=='worked/singular_block':
        return [table('Recorded residues for the three candidate digits',['Digit','Residual modulo 9'],[[t,r] for t,r in enumerate(worked['blocked_residues'])])]
    if name=='worked/shared_obstruction':
        return [table('Available shared corrections',['Digit','First residual','Second residual'],[[t,*r] for t,r in enumerate(worked['shared_residuals'])])]
    if name=='worked/weighted_motion':
        return [table('Recorded root displacement',['Exponent','Root','Coefficient valuation','Displacement valuation'],[[r[k] for k in ('A','root','coefficient_valuation','motion_valuation')] for r in worked['motion']])]
    return []
