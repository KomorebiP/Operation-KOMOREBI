"""The retained Paper V monograph's contiguous reading ranges.

The 33 main sections, four appendices and three orientation pages retain the
original source lines. The forty-plate atlas remains linked in the original PDF.
"""
BASE = 'papers/paper-v/current/editable/traditional/'
MAIN = BASE+'Paper_V_Traditional_Final.tex'
SECTIONS = [
    (217, 'orientation', 'Reading this edition', None),
    (262, 'signal-realization', 'The signal realization of the seed calculus', True),
    (308, 'polyphase-coordinates', 'Residue projectors and exact polyphase coordinates', True),
    (407, 'transfer-matrices', 'Linear time-invariant operators as transfer matrices', True),
    (480, 'perfect-reconstruction', 'Analysis banks, synthesis banks, and perfect reconstruction', True),
    (598, 'wavelet-packets', 'Wavelet packets as addressed refinements', True),
    (637, 'known-edge-packets', 'Known edge packets and spectral reconstruction', True),
    (699, 'packet-error', 'Mask, amplitude, and smooth-background error', True),
    (761, 'numerical-study-1d', 'One-dimensional numerical study', True),
    (802, 'edge-packets-2d', 'Two-dimensional edge packets', True),
    (857, 'sparse-approximation', 'Sparse wavelet packets and global Fourier modes', True),
    (889, 'adaptive-packet-trees', 'Finite adaptive packet trees', True),
    (1056, 'nonlinear-packets', 'Nonlinear signal packets', True),
    (1104, 'smith-coordinates', 'Smith coordinates as cyclic signal coordinates', True),
    (1219, 'phase-factorization', 'Dyadic--odd phase factorization and boundary weighting', True),
    (1274, 'boundary-error', 'Boundary-localized error and claim control', True),
    (1301, 'implementation', 'Implementation and reproducibility', True),
    (1355, 'core-conclusions', 'Conclusions', True),
    (1375, 'algorithms', 'Algorithm statements', True),
    (1421, 'numerical-record', 'Numerical record', True),
    (1454, 'notation', 'Notation crosswalk', True),
    (1479, 'formalization', 'Formalization and reproducibility record', True),
    (1590, 'extended-orientation', 'Extended mathematical development', None),
    (1608, 'extended-introduction', 'Introduction', True),
    (1722, 'lattice-addresses', 'Signal seeds and lattice addresses', True),
    (1756, 'sublattice-coordinates', 'Polyphase coordinates on finite index sublattices', True),
    (1902, 'convolution', 'Convolution as a packet transfer matrix', True),
    (2034, 'stable-filter-banks', 'Filter banks, frame bounds, and lifting', True),
    (2328, 'admissible-packet-trees', 'Wavelet packet trees and admissible bases', True),
    (2503, 'singular-packets', 'Singular packets and exact reconstruction', True),
    (2695, 'estimated-packet-error', 'Exact error formulas for estimated packets', True),
    (2886, 'separated-jump-recovery', 'Stable recovery of separated jumps', True),
    (3183, 'haar-localization', 'Haar localization and annihilating differences', True),
    (3376, 'gibbs-phenomenon', 'Packet separation and the Gibbs phenomenon', True),
    (3486, 'nonlinear-interactions', 'Nonlinear interactions in residue coordinates', True),
    (3589, 'finite-illustrations', 'Finite numerical illustrations', True),
    (3639, 'cayley-coordinates', 'Cyclic Cayley coordinates', True),
    (3747, 'limits', 'Limits and further directions', True),
    (3759, 'extended-conclusion', 'Conclusion', True),
    (3789, 'visual-atlas', 'Forty worked visual plates', None),
]
CHAPTERS = [dict(source=MAIN, url='read/paper-v/'+slug+'.html', title=title, work='paper-v',
                 start_line=start, end_line=SECTIONS[i+1][0]-1 if i+1<len(SECTIONS) else 3808,
                 heading_title=title if heading else None,
                 figure_roots=['', 'extension_figures/' if start>=1590 else 'core_figures/'])
            for i,(start,slug,title,heading) in enumerate(SECTIONS)]
BOOK = dict(work='paper-v', label='Paper V', base=BASE, main=MAIN,
            bib=BASE+'references.bib', index='read/paper-v/index.html',
            bib_page='read/paper-v/references.html', title='Multiresolution Signal Calculus',
            chapters=CHAPTERS, main_chapters=33, monolithic=True,
            required_macros=['Pcal','Qcal','Rcal','Scal','id','bbC','bbZ'],
            figure_descriptions='website/paper-v-figure-descriptions.json',
            figure_receipts='assets/figures/paper-v/figures.json',
            pdf_inputs={'atlas-pages.tex':'Read the forty worked visual plates in the PDF'})
