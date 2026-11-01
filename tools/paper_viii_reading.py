"""Source-bound Paper VIII manuscript sections and all six appendices."""
BASE = 'papers/paper-viii/current/editable/traditional/'
MAIN = BASE+'Paper_VIII_Traditional_Final.tex'

# Inclusive source ranges retain statement and proof permalinks.
SECTIONS = [
    (1, 'introduction', 'Introduction'),
    (56, 'packet-operators', 'Packet operator representations'),
    (245, 'arithmetic-storage-and-movement', 'Arithmetic, storage, and data movement'),
    (453, 'structured-primitives', 'Structured packet primitives'),
    (656, 'low-rank-algebra', 'Exact low rank algebra and recompression'),
    (946, 'transfer-graphs', 'Sparse transfer graphs and schedules'),
    (1092, 'krylov-and-preconditioning', 'Krylov methods and packet preconditioning'),
    (1250, 'mixed-precision', 'Packetwise mixed precision'),
    (1459, 'exact-compilation', 'Discovery and exact packet compilation'),
    (1722, 'device-scheduling', 'Device scheduling and amortization'),
    (1808, 'benchmark-contracts', 'Benchmark contracts and measurement protocol'),
    (1857, 'recorded-measurements', 'Recorded CPU and GPU corpus'),
    (2030, 'implementation', 'Implementation and verification'),
    (2066, 'boundaries', 'Hardware implications and exact boundaries'),
    (2082, 'conclusion', 'Conclusion'),
]

APPENDICES = [
    ('exact-semantics', 'A. Exact semantics, support, and low-rank identities'),
    ('compilation-and-costs', 'B. Exact compilation, continuous precision, and explicit costs'),
    ('product-chains-and-budgets', 'C. Product chains, Krylov spaces, and integer budgets'),
    ('transforms-and-precision', 'D. Structured transforms and clipped precision'),
    ('graph-schedules', 'E. Constructed graph schedules, support, and preconditioning'),
    ('small-core-recompression', 'F. Global small-core recompression from ordered thin SVD data'),
]

CHAPTERS = [
    dict(source=MAIN, url='read/paper-viii/orientation.html', title='Reading this edition',
         work='paper-viii', start_line=115, end_line=171),
    dict(source=BASE+'monograph_examples.tex', url='read/paper-viii/three-exact-models.html',
         title='Three exact models', work='paper-viii', figure_roots=[''],
         numbering_state=dict(section=0, subsection=0, subsubsection=0, counter=0, appendix=False)),
]
for i,(start,slug,title) in enumerate(SECTIONS):
    CHAPTERS.append(dict(source=BASE+'parts/01_manuscript.tex',
        url='read/paper-viii/'+slug+'.html', title=title, work='paper-viii',
        start_line=start, end_line=SECTIONS[i+1][0]-1 if i+1<len(SECTIONS) else 2094))
for i,(slug,title) in enumerate(APPENDICES,1):
    spec=dict(source=BASE+'parts/02_supplement_0'+str(i)+'.tex',
              url='read/paper-viii/appendix-'+slug+'.html', title=title, work='paper-viii')
    if i==1:
        spec['numbering_state']=dict(section=0, subsection=0, subsubsection=0, counter=0, appendix=True)
    CHAPTERS.append(spec)

BOOK = dict(work='paper-viii', label='Paper VIII', base=BASE, main=MAIN,
    bib=BASE+'references.bib', index='read/paper-viii/index.html',
    bib_page='read/paper-viii/references.html',
    title='Packet Operator Algorithms, Exact Compilation, and GPU Realization',
    chapters=CHAPTERS, main_chapters=15, number_floats=True,
    required_macros=['Pcal','IR','DP','cost','err','id'],
    statement_navigation=True, require_table_reading_aids=True,
    figure_receipts='assets/figures/paper-viii/figures.json',
    main_inputs=['monograph_examples.tex','parts/01_manuscript.tex']+
                ['parts/02_supplement_0'+str(i)+'.tex' for i in range(1,7)]+['monograph_atlas.tex'],
    pdf_inputs={'monograph_atlas.tex':'Read the worked visual atlas in the original PDF'},
    reading_introduction='Read the opening orientation and three exact models, all 15 manuscript sections, '
                         'and Appendices A–F. The worked visual atlas remains in the original PDF.')

BOOK['table_reading_aids']={
    ('monograph_examples.tex','L49'): dict(caption='Candidate-tree node costs and errors',
        headers=['Node','$r$','$a$','$b$','$a_1$','$a_2$'],row_header_column=0),
    ('monograph_examples.tex','L57'): dict(caption='All three legal prunings',
        headers=['Selected nodes','Total cost','Total error'],row_header_column=0),
    ('monograph_examples.tex','L85'): dict(caption='Fast and accurate options for each packet edge',
        headers=['',r'\multicolumn{2}{c}{F}',r'\multicolumn{2}{c}{A}'],
        subheaders=['Edge','Cost','Error','Cost','Error'],row_header_column=0),
    ('monograph_examples.tex','L97'): dict(caption='All eight discrete precision assignments',
        headers=['Assignment','Cost','Error','Assignment','Cost','Error'],
        row_header_column=0,row_header_columns=[0,3]),
    ('parts/01_manuscript.tex','L1861'): dict(headers=['Suite','Rows','Suite','Rows'],
        row_header_column=0,row_header_columns=[0,2]),
    ('parts/01_manuscript.tex','L1888'): dict(
        headers=['Method','Median time in ms','Logical GFLOP per second','Relative error'],row_header_column=0),
    ('parts/01_manuscript.tex','L2046'): dict(headers=['Layer','Verification target'],row_header_column=0),
    ('parts/02_supplement_02.tex','L168'): dict(caption='Storage and arithmetic under the declared event model',
        headers=['Representation','Scalar storage','Modeled work for $q$ right sides'],row_header_column=0),
    ('parts/02_supplement_02.tex','L239'): dict(caption='Remaining items at the historical second checkpoint',
        headers=['Remaining items','Work not yet fully formalized'],row_header_column=0),
    ('parts/02_supplement_03.tex','L239'): dict(caption='Exact-rational executable checks at the third checkpoint',
        headers=['New test category','Count'],row_header_column=0),
    ('parts/02_supplement_04.tex','L254'): dict(caption='Remaining items at the historical fourth checkpoint',
        headers=['Item','Remaining result'],row_header_column=0),
    ('parts/02_supplement_06.tex','L203'): dict(caption='Small-core recompression modules and supporting declarations',
        headers=['Module','Main purpose','Theorems'],row_header_column=0),
}
