"""Descriptions and label relationships for the retained Paper I drawings."""
DESCRIPTIONS={
 'grammar_budget':('Minimum seeds under four acting algebras','Four rows compare the same six-dimensional space under scalar action, a single operator, the operator with chain projectors, and the full matrix algebra. Filled squares and the numbers at right give minimum seed counts; they do not show timings.'),
 'linked_chains':('Two length-three chains with linked coefficients','The operator advances along each of two chains and then sends the last vector to zero. Dotted vertical pairings indicate equal coefficients in the orbit of the mixed seed; they are not extra operators.'),
 'quotient_heads':('A quotient retaining two independent chain heads','The columns of the two-by-six quotient matrix follow the displayed basis labels. Each output retains one chain head and discards its advanced positions.'),
 'left_ideal':('Right multiplication can destroy a seed relation','Three matrices display C, B and their product in that order. The source labels show that C kills the seed while CB returns the seed, illustrating the difference between a left ideal and a two-sided ideal.'),
 'typed_spaces':('Type reachability and missing directions','Three rows show the basis directions at U and V. With the seed supported at U, the v3 slot is unfilled and the hull has dimension four. Adding the pure v3 seed, or using the displayed mixed seed, fills all five directions.'),
 'oblique_vectors':('Exact reconstruction from oblique components','A horizontal line and a diagonal line are the two packet images. The vectors Px and Qx add to x through the displayed parallelogram; their geometry is not that of perpendicular projections.'),
 'block_square':('An operator and its exact square','Two matrices show T and T squared. Rows are outputs and columns are inputs; each entry of the square sums over intermediate packet indices.'),
 'cancelled_paths':('Two weighted paths cancel in one transfer block','A weighted diamond gives two routes from the first vertex to the fourth. Their signed contributions cancel. The adjacent Krylov matrix records the resulting orbit and its rank.'),
 'support_closure':('A support pattern and its transitive closure','Three matrices show the allowed support, a product that escapes it, and the transitive closure. Ones in the support arrays mean allowed positions; the middle array is an actual matrix product.'),
 'transported_packets':('An operator transported with its packet projectors','The upper row shows T, the shear U and the conjugated operator. The lower row shows both transported projectors. The changed matrix entries are read relative to the changed packet coordinates.'),
 'shared_independent':('Shared and independent scalar actions','Two panels start from the vector (1,1). Shared scalar control generates the diagonal line. Independent coordinate control generates the plane; the shaded region is only a finite window.'),
 'row_budget':('Three seeds covering five multiplicity directions','Three two-by-five seed matrices show the row directions supplied in sequence. Their labeled cumulative orbit dimensions are four, eight and ten.'),
 'primary_krylov':('Krylov matrices with equal and distinct primary labels','Two six-by-six matrices use the same mixed seed with different operators. Equal primary labels give rank three; distinct labels give the displayed nonzero determinant. Matrix rows run from top to bottom in the fixed chain basis.'),
 'path_walks':('Walk counts from an endpoint of a five-vertex path','The dark endpoint is the seed. The matrix rows correspond to graph vertices and its columns to powers of the adjacency operator. Its entries count walks and expose the unit triangular structure.'),
 'cycle_multiplicity':('A six-cycle and its exact eigenspace dimensions','Two dark vertices identify the displayed generating pair on the six-cycle. The bars at right give exact eigenspace dimensions at the labeled eigenvalues; they are not a sampled frequency spectrum.'),
 'normal_form':('Two coefficient lanes in a coordinate ring','Two rows retain independent polynomial coefficient slots for a(x) and b(x). The final relation rewrites higher powers of y into these lanes rather than discarding them.'),
 'shift_tail':('An infinite sequence viewed through a finite window','Stems display part of the nonzero sequence indexed by all integers. Shading marks the truncation window with absolute index at most three. The omitted tail remains present in the infinite sequence.'),
 'residue_carry':('Three residue packets on the integer lattice','Rows zero, one and two contain their respective integer addresses modulo three. The bottom example follows address two to address three, carrying one step into the coarse index.'),
 'hull_iteration':('Dimensions of successive generated subspaces','The horizontal axis is iteration and the vertical axis is subspace dimension. The dashed curve permits only N; the solid curve also permits both chain projectors. Repeated plateau values indicate the checked stopping condition.'),
 'tensor_rectangle':('All four coefficients in a tensor expansion','Row and column labels give the factors in the two linear combinations. The rectangular table retains both diagonal and cross coefficients; the displayed expansion below it uses all four terms.'),
}
FIGURES={name:dict(alt=alt,description=description,blocks=[]) for name,(alt,description) in DESCRIPTIONS.items()}


def matrix(start,rows,columns,caption):
    return dict(kind='table',caption=caption,headers=['Row']+['Column '+str(i+1) for i in range(columns)],
        rows=[['Row '+str(i+1)]+list(range(start+i*columns,start+(i+1)*columns)) for i in range(rows)])


def label_blocks(name,nodes):
    tables={
        'grammar_budget':[dict(kind='table',caption=8,headers=['Allowed algebra','Minimum seeds'],rows=[[0,1],[2,3],[4,5],[6,7]])],
        'quotient_heads':[dict(kind='table',caption=12,headers=['Output']+list(range(13,19)),rows=[['First output']+list(range(6)),['Second output']+list(range(6,12))])],
        'left_ideal':[matrix(0,2,2,4),matrix(5,2,2,9),matrix(10,2,2,14)],
        'block_square':[matrix(0,3,3,9),matrix(10,3,3,19)],
        'cancelled_paths':[matrix(8,4,3,20)],
        'support_closure':[matrix(0,3,3,9),matrix(10,3,3,19),matrix(20,3,3,29)],
        'transported_packets':[matrix(0,2,2,4),matrix(5,2,2,9),matrix(10,2,2,14),matrix(15,2,2,19),matrix(20,2,2,24)],
        'row_budget':[matrix(0,2,5,10),matrix(11,2,5,21),matrix(22,2,5,32)],
        'primary_krylov':[matrix(0,6,6,36),matrix(37,6,6,73)],
        'path_walks':[dict(kind='table',caption='Endpoint Krylov matrix: vertices by walk length',headers=[35]+list(range(30,35)),rows=[[i]+list(range(5+i*5,10+i*5)) for i in range(5)])],
        'tensor_rectangle':[dict(kind='table',caption=4,headers=['Factors',5,6],rows=[[7,0,1],[8,2,3]])],
    }.get(name,[])
    lookup={}
    for number,table in enumerate(tables):
        values=[table['caption']]+table['headers']+[value for row in table['rows'] for value in row]
        for value in values:
            if isinstance(value,int):
                if value in lookup:raise ValueError('Repeated Paper I table label')
                lookup[value]=number
    blocks=[];seen=set()
    for index in range(len(nodes)):
        if index in lookup:
            number=lookup[index]
            if number not in seen:
                blocks.append(tables[number]);seen.add(number)
        elif blocks and blocks[-1]['kind']=='text':blocks[-1]['nodes'].append(index)
        else:blocks.append(dict(kind='text',nodes=[index]))
    return blocks
