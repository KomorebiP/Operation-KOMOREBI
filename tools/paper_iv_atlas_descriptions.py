"""Reading aids for the retained Paper IV drawings.

Integer cells refer to original TikZ labels, never retyped mathematical values.
Every label must occur exactly once in the structured transcript. Descriptions
explain spatial relationships; the atlas's original evidence notes stay adjacent.
"""


def text(*nodes, title=None):
    return dict(kind='text',nodes=list(nodes),title=title)


def table(caption, headers, rows):
    return dict(kind='table',caption=caption,headers=headers,rows=rows)


def matrix(caption, start, size):
    return table(caption,['Row / column']+['Column '+str(i) for i in range(size)],
                 [['Row '+str(i)]+list(range(start+i*size,start+(i+1)*size)) for i in range(size)])


def figure(alt, description, *blocks):
    return dict(alt=alt,description=description,blocks=list(blocks))


FIGURES = {
    'three_views': figure(
        'Three panels connect residue lanes, a triangular coefficient system, and rotational zero orbits.',
        'Read left to right. The first panel groups monomials into three residue lanes. The middle panel shows a lower-triangular coefficient matrix and the beginning of its reciprocal solution. The right panel places two four-point orbits on the coordinate axes. These are different small-order models, as explained in the plate; they are not one diagram at a single common order or scale.',
        table(0,['Lane','First term','Second term','Third term','Fourth term'],
              [['Residue 0',3,4,5,6],['Residue 1',7,8,9,10],['Residue 2',11,12,13,14]]),
        text(15),matrix(1,16,3),text(25),text(2,26,title='Rotational picture')),
    'root_filter': figure(
        'Four phase directions accompany four residue lanes; the residue-two lane is highlighted.',
        'The left panel places the four complex phases on perpendicular arrows from a common origin. The finite average below them selects matching coefficient addresses. The right panel lists four residue lanes. Its shaded third row contains the monomials selected in the worked example; shading is also identified explicitly in the table.',
        text(0,5),table('Phase directions',['Direction','Phase'],[['Right',1],['Up',2],['Left',3],['Down',4]]),
        table('Residue lanes',['Lane','First term','Second term','Third term','Highlight'],
              [[6,7,8,9,''],[10,11,12,13,''],[14,15,16,17,'Selected lane'],[18,19,20,21,'']]),text(22)),
    'cyclic_product': figure(
        'A three-by-three product table highlights the three mixed pairs contributing to residue zero.',
        'Columns are the selected sections of the second polynomial and rows are those of the first. Each interior cell is their exact product. The top-left, middle-right and bottom-middle cells are shaded: together they supply the residue-zero output. Reading only the top-left cell omits the two mixed contributions.',
        table('Products of the selected sections',['First section / second section',0,1,2],
              [[3,4,5,6],[7,8,9,10],[11,12,13,14]]),text(15,16)),
    'signed_shift': figure(
        'The signed shift matrix and its exponential are shown beside their cycle, initial-value and determinant identities.',
        'Read the two matrices by row and column in the ordered basis e₀, e₁, e₂. Columns describe inputs and rows describe outputs. The minus sign in the top-right corner closes the signed cycle. In the exponential matrix, each upper-triangular minus sign records a wrap across that edge. The derivative rules underneath use the abbreviated section names explained in the plate.',
        matrix(0,1,3),matrix(10,11,3),text(20,21,22,23,title='Identities below the matrices')),
    'signed_addition': figure(
        'A quotient-algebra multiplication table records the negative sign introduced by a cyclic wrap.',
        'The row and column labels are the three basis elements. Products crossing the cubic relation acquire a minus sign. The addition formula below the table reads the constant-coordinate contributions: one has no wrap and two have a wrap.',
        table('Signed quotient multiplication',['Row factor / column factor',0,1,2],
              [[3,4,5,6],[7,8,9,10],[11,12,13,14]]),text(15,16,17,18)),
    'hypergeometric': figure(
        'Three rows group the six scaled factorial factors into two retained parameters and the omitted unit parameter.',
        'The rows separate the scaled factorial factors by residue. Their two entries multiply to the Pochhammer product in the last column. The middle row supplies the factorial already present in hypergeometric notation, so its unit parameter is omitted from the parameter set. The final formula retains both the initial monomial and the argument scaling.',
        text(0),table('Factorial groups',['First factor','Second factor','Product'],[[1,2,3],[4,5,6],[7,8,9]]),text(10,11,12)),
    'orbit_reduction': figure(
        'Two four-point zero orbits in the normalized complex plane map to two simple reduced zeros.',
        'The left panel marks two radial levels on each of the four coordinate rays. The fourth-power arrow identifies all four members of each orbit with one point on the positive reduced axis. The two reduced points are labeled separately as one zero each. The map changes the radius scale and removes repeated orbit members; it does not multiply local multiplicity.',
        text(0,1,title='Original normalized plane'),text(2,title='Power map'),
        table('Reduced points',['Position','Multiplicity label'],[[3,4],[5,6]]),text(7,8)),
    'triangular_inverse': figure(
        'A lower-triangular denominator matrix times the reciprocal coefficient vector equals the unit-series vector.',
        'Read the matrix equation from left to right: denominator convolution, the unknown coefficient vector, and the unit series. Each matrix row introduces one new coefficient. The values shown are ordinary reduced-variable coefficients. The final line separately converts them to block exponential-generating-function coefficients.',
        matrix(0,1,4),table(17,['Index','Coefficient'],[['0',18],['1',19],['2',20],['3',21]]),text(22),
        table(23,['Index','Coefficient'],[['0',24],['1',25],['2',26],['3',27]]),text(28,29,30,31)),
    'bell_partitions': figure(
        'Three partition types contribute the cubic, quadratic and linear terms of the reciprocal-order polynomial.',
        'Each row names a partition type, gives its logarithmic contribution, and gives the resulting term after the plate’s factorial normalization. Three singleton pieces produce the cubic term, a pair and singleton produce the quadratic term, and a single triple produces the linear term. The Bell-polynomial identity underneath combines the three rows.',
        table('Partition contributions',['Partition type','Logarithmic term','Normalized contribution'],[[0,1,2],[3,4,5],[6,7,8]]),text(9)),
    'newton_addition': figure(
        'A Newton determinant and four block-convolution contributions give the same reciprocal coefficient.',
        'The left panel shows a three-by-three determinant with a negative superdiagonal. Its normalization is stated immediately below. The right panel has four contributions, indexed from zero to three, to the parameter-addition calculation. The middle contributions use the larger block binomial weights rather than ordinary binomial weights.',
        matrix(0,1,3),text(10),table('Parameter-addition contributions',['Block index','Contribution'],[[12,11],[14,13],[16,15],[18,17]]),text(19,20)),
    'riccati': figure(
        'Two linear differential equations are paired with their logarithmic-derivative equations.',
        'Read each row across: the denominator equation on the left becomes the corresponding nonlinear tangent equation on the right. The line below restricts logarithmic differentiation to the nonzero set of the denominator. The last line gives an order-four tangent series as a separate coefficient example.',
        table('Linear and nonlinear equations',[0,1],[[2,3],[4,5]]),text(6,7)),
    'branch_domain': figure(
        'A zero-free disk about the origin is separate from a loop around a simple zero.',
        'The shaded disk represents an admissible fixed-logarithm region around the origin. A separate loop encircles the marked simple zero outside that disk. The labels beneath the picture track the logarithm’s change and the resulting phase factor for the reciprocal power. This is a schematic domain picture, not a sampled proof of a winding-number statement.',
        text(0,title='Admissible region'),text(1,2,title='Loop outside that region'),text(3,4,5,title='Local continuation rules'),text(6,title='Phase-factor examples')),
    'different_reciprocals': figure(
        'A coefficient table contrasts secant, hyperbolic secant, and the normalized reciprocal of hyperbolic sine.',
        'Read across each function row using the factorial-scaled monomials in the column headers. The rows differ in signs and rational values even though each normalized function has constant term one. The identity beneath the table records removal of the forced zero before forming the third reciprocal.',
        table('Block exponential-generating-function coefficients',[0,1,2,3,4],[[5,6,7,8,9],[10,11,12,13,14],[15,16,17,18,19]]),text(20)),
    'appell_operator': figure(
        'The solid transformed quartic is compared with the dashed input quartic and its inverse differential operation.',
        'The horizontal axis is the polynomial variable and the vertical axis is the polynomial value. The solid output crosses the axis four times, at the roots stated in the plate, while the dashed input touches it at the origin. These are polynomial roots, not zeros of the analytic denominator. The formula below the graph gives the exact finite inverse operation.',
        text(*range(0,5),title='Horizontal-axis ticks'),text(*range(5,10),title='Vertical-axis ticks'),text(10,11,title='Curve labels'),text(12,title='Inverse operation')),
    'theta': figure(
        'Solid even-order and dashed odd-order theta curves show different behavior at minus one.',
        'The horizontal axis is the common parameter and the vertical axis is the first theta coefficient. Both displayed curves pass through zero at the origin. At minus one the solid even-order curve also vanishes, whereas the dashed odd-order curve does not. The distinction illustrates the boundary stated in the accompanying text.',
        text(0,1,2,title='Horizontal-axis ticks'),text(3,4,5,6,7,title='Vertical-axis ticks'),text(8,9,title='Curve labels'),text(10)),
    'indicator': figure(
        'The order-four exponent square is paired with its directional growth indicator.',
        'The left panel is the square of exponent roots in the complex plane. The right panel plots the corresponding support-function formula against angle. Its four minima occur at the coordinate-ray angles, where adjacent dominant exponentials tie. The curve describes directional growth through a limsup; it does not remove the cancellations or zeros possible along those rays.',
        text(0,1,title='Exponent polygon'),text(2,3,4,5,6,title='Angular-axis ticks'),text(7,8,title='Indicator-axis ticks'),text(9,10)),
    'two_term': figure(
        'A solid normalized cubic denominator is compared with a dashed cosine model and marked model zeros.',
        'The horizontal axis is the real argument. The solid curve includes the small positive exponential remainder; the dashed curve omits it. Circles mark zeros of the cosine model. The solid crossings are slightly displaced from those markers, with displacement decreasing along the displayed positive direction. The next plate supplies separate rational certificates.',
        text(0,1,2,3,4,5,title='Argument-axis ticks'),text(6,7,8,title='Value-axis ticks'),text(9,title='Normalized expression'),text(10,title='Curve and marker key')),
    'cubic_certificates': figure(
        'Four certified lower endpoints are tabulated beside approximate displacement diagnostics.',
        'Each row identifies one local root interval. The first numeric column is its certified lower endpoint; the upper endpoint is obtained by the exact increment stated below the table. The remaining columns describe displacement and relative discrepancy numerically. They are diagnostics, distinct from the rational interval certificates. This table does not enumerate every zero.',
        table('Certified intervals and numerical diagnostics',['Index',16,17,18],[[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15]]),text(19,20)),
    'counting': figure(
        'Two rows compare four-at-a-time radial counts with one-at-a-time reduced-zero counts.',
        'The upper row marks successive normalized radii and counts all four orbit members. The lower row marks their fourth powers and counts one reduced zero per orbit. The tables retain both the jump locations and the counts at those locations. The formulas include zeros on the disk boundary.',
        table(0,['Radial location','Count at the jump'],[[1,2],[3,4],[5,6]]),
        table(7,['Reduced location','Count at the jump'],[[8,9],[10,11],[12,13]]),text(14)),
    'product': figure(
        'The reduced cosine function is compared with three finite zero products.',
        'The horizontal axis is the reduced variable and the vertical axis is the function or product value. All curves start at one. The thick curve is the entire function; three line styles identify products with increasing numbers of factors. Their agreement improves with the truncation size, while the plate states a separate quantitative tail bound and its range.',
        text(0,1,2,3,4,title='Reduced-variable ticks'),text(5,6,7,8,9,title='Value-axis ticks'),text(10,title='Function and product'),text(11,title='Line-style key')),
    'moments': figure(
        'Three stacked bars show the growing share of the nearest reduced zero in successive moments.',
        'Each horizontal bar has five finite zero contributions followed by the remaining tail. The total is the exact rational moment labeled for that row. The table also transcribes the displayed decimal share of the nearest zero. As the inverse-power order increases, that nearest-zero share occupies more of the bar; the widths themselves are numerical visualizations.',
        table('Moments and nearest-zero shares',['Moment order','Exact total and displayed share'],[[0,1],[2,3],[4,5]]),text(6)),
    'pole_asymptotic': figure(
        'A downward error plot compares eight exact secant coefficients with their nearest-pole asymptotic scale.',
        'The horizontal ticks are the eight tested block indices. The vertical axis is the base-ten logarithm of one minus the enclosed coefficient ratio. The plotted values decrease as the approximation improves over this tested range. Rational bounds support these finite comparisons; the picture is not an additional all-index error theorem.',
        text(*range(0,8),title='Tested-index ticks'),text(*range(8,13),title='Logarithmic-error ticks'),text(13,title='Ratio and plotted quantity'),text(14)),
    'zeta_plane': figure(
        'Two complex planes shade convergence half-planes and mark the continued poles for orders two and four.',
        'In each panel the shaded region lies strictly to the right of the stated real-part threshold. An open circle on the boundary marks the single pole of the meromorphic continuation. The open circles are poles, not zeros. The two different boundaries reflect the different growth rates of the reduced zero sequences.',
        table('Convergence and continued poles',['Case','Real-part boundary','Shaded region','Pole label'],[[2,0,1,3],[6,4,5,7]])),
    'worked_circuit': figure(
        'Five rows connect the order-four denominator, logarithm, zero moments, reciprocal, and tangent.',
        'Read the rows from denominator through tangent. Every row uses the same order-four normalization. The identities at the bottom recover the reciprocal coefficient sixty-nine and the tangent coefficient thirty-four from the first two zero moments. The prose below gives both routes to the reciprocal coefficient and states the analytic input behind the zero-sum interpretation.',
        table('One order-four calculation',['Description','Series or values'],[[0,1],[2,3],[4,5],[6,7],[8,9]]),text(10)),
}
