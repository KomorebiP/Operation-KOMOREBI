"""Editorial reading paths into the unchanged Quantum and Circuits edition."""
from html import escape

from quantum_reading import CHAPTERS, PREFIX, WORK

PAGE = PREFIX+'start.html'
PATHS = [
    ('visual', 'Visual introduction', 'Begin with pictures and a concrete calculation.',
     'Useful background: vectors, probabilities, and the idea of a change of basis. The pictures provide an entry point; follow their linked text when a definition is unfamiliar.', [
        ('visual-one-arithmetic-selector-three-realizations', 'One selector, three realizations', 'Follow the same finite selector through arithmetic, Fourier coordinates, and quantum language.'),
        ('visual-amplitudes-and-probabilities-tell-different-stories', 'Amplitudes and probabilities', 'Compare the amplitude picture with the measurement histogram.'),
        ('visual-a-basis-change-makes-the-hidden-distinction-observable', 'Change the measurement basis', 'Follow the visual example of a distinction that becomes visible after a basis change.'),
        ('symmetry-the-exact-weight-two-benchmark', 'A symmetry example', 'Inspect the weight-two benchmark and the costs retained in its model.'),
        ('circuit-visual-a-dirty-scratch-wire-can-be-fully-restored', 'A restored scratch wire', 'See the boundary-restoration requirement in a circuit example.')],
     'Checkpoint: explain what a representation changes, what a measurement records, and what must be restored. Then choose a treatment in the full-study route.'),
    ('study', 'Full study', 'Read the four treatments with their models in view.',
     'Useful background: complex linear algebra and finite Fourier transforms for arithmetic and symmetry; gate costs for catalysis; Boolean polynomials over the binary field for circuits.', [
        ('arithmetic-overview', 'Chapters 1–2 · Arithmetic realizations', 'Follow the selector, Fourier projector, and normalized state. Work through the modulus-twelve calculation before the finite bridge theorem.'),
        ('symmetry-the-symmetry-collapse-question', 'Chapters 3–7 · Symmetry collapse', 'Track the packet coordinates, updates, and measurement costs alongside the dimension of the compressed representation.'),
        ('catalytic-nested-gate-models-and-distortion-invariants', 'Chapters 8–12 · Catalytic gate sets', 'Keep the restricted gate alphabet, allowed excursion, cost convention, and restored boundary state explicit.'),
        ('circuits-scope-notation-and-computational-model', 'Chapters 13–21 · Circuit obstructions', 'Read the circuit model before the cut comparison, safe covers, projection, and visual examples.')],
     'Checkpoint: for a result you want to use, write down its model, hypotheses, resource convention, and conclusion. Use the formal companion to inspect its recorded coverage.'),
    ('formal', 'Formal companion', 'Trace selected results into their types and evidence.',
     'Useful background: the corresponding written result and enough Lean notation to read a declaration type. Begin with coverage before selecting a source file.', [
        ('verification-verification-and-proof-boundaries', 'Read the verification boundaries', 'Start with Appendix F to distinguish the retained formal records, written arguments, and finite computations.'),
        ('formal-arithmetic-trust-boundary-and-current-verification', 'Inspect the arithmetic companion', 'Read the trust boundary in Appendix A, then follow its proof architecture and individual formal statements.'),
        ('formal-circuits-model-and-definitions', 'Inspect the circuit model', 'Compare the definitions in Appendix D with the written boundary and restoration conditions.'),
        ('formal-circuits-complete-declaration-register', 'Find a circuit declaration', 'Follow the register to its full type, source location, block, and axiom set.'),
        ('circuit-coverage-complete-numbered-result-index', 'Return to the written result', 'Use Appendix E to open a numbered statement in HTML or at its printed PDF page.'),
        ('formal-circuits-reproduce-and-inspect-the-authoritative-files', 'Read the reproduction instructions', 'Identify the authoritative files and recorded execution requirements before attempting a replay.')],
     'Checkpoint: match a declaration’s full type to the written statement and its hypotheses. The inventories include supporting declarations and do not certify the entire volume.')]


def publish(reader, book):
    site=reader.site
    available={c['url'] for c in CHAPTERS}
    def link(slug, title):
        target=PREFIX+slug+'.html'
        if target not in available:raise ValueError('Unknown Quantum reading-path destination: '+target)
        return '<a href="'+escape(site.rel(target,PAGE),quote=True)+'">'+escape(title)+'</a>'
    body='<div class="quantum-start"><p class="eyebrow">Quantum and Circuits · Guided reading</p><h1>Start with a question</h1>'
    body+='<p class="lede">Choose a visual introduction, study the four treatments, or trace a selected result into its formal record.</p>'
    body+='<p class="quantum-guide-facts">21 chapters · 6 appendices · '+str(len(CHAPTERS)+1)+' reading pages</p>'
    body+='<nav class="quantum-path-cards" aria-label="Choose a reading path">'
    for i,(key,title,summary,*_) in enumerate(PATHS,1):
        body+='<a class="route" href="#'+key+'"><span class="eyebrow">Path '+str(i).zfill(2)+'</span><h2>'+escape(title)+'</h2><p>'+escape(summary)+'</p><span>Explore this path →</span></a>'
    body+='</nav><p>These are suggested reading sequences. Each destination retains the volume’s statements, figures, and source links.</p>'
    for key,title,summary,background,steps,checkpoint in PATHS:
        body+='<section class="quantum-path" id="'+key+'" aria-labelledby="'+key+'-title"><h2 id="'+key+'-title">'+escape(title)+'</h2><p>'+escape(background)+'</p><ol>'
        for slug,label,description in steps:
            body+='<li>'+link(slug,label)+'<p>'+escape(description)+'</p></li>'
        body+='</ol><p class="notice">'+escape(checkpoint)+'</p>'
        if key=='visual':
            body+='<p>Try the existing <a href="'+site.rel('read/quantum-phase-measurement.html',PAGE)+'">phase and measurement walkthrough</a>, then <a href="'+site.rel('playground.html',PAGE)+'#physics-arithmetic-phase">change the phase in the browser</a>.</p>'
        if key=='study':
            body+='<p>'+link('volume-preface-and-volume-guide','Preface and volume guide')+' · '+link('glossary-shared-glossary','Shared glossary')+'</p>'
        if key=='formal':
            body+='<p>For the other treatments, consult the '+link('symmetry-companion-theorem-and-evidence-status-ledger','symmetry evidence ledger')+' and '+link('catalytic-companion-conjecture-and-obligation-ledger','catalytic obligation ledger')+'.</p>'
        body+='<p><a href="#top">Choose another path ↑</a></p></section>'
    body+='<nav class="quantum-guide-return" aria-label="Volume resources"><a class="button" href="index.html">Full contents</a><a href="'+site.rel('collection/works/'+WORK+'.html',PAGE)+'">Work overview and sources</a></nav></div>'
    body=body.replace('<div class="quantum-start">','<div class="quantum-start" id="top">',1)
    site.page(PAGE,'Quantum and Circuits: Start here',body)
    site.search.append(dict(title='Quantum and Circuits / Start here',group='Collection',kind='Guides',work_ids=[WORK],url=PAGE,
        text='Guided reading prerequisites visual introduction full study formal companion '+ ' '.join(p[1]+' '+p[2] for p in PATHS)))
