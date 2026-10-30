"""Reading aids keyed to the original Paper VI TikZ labels.

Integer cells name original labels. Every label appears exactly once.
"""
from paper_iv_atlas_descriptions import figure, table, text

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
