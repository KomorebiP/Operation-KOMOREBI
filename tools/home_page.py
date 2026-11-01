"""The collection's compact introduction and manually selected research slides."""
import html


def research_slides():
    examples = [
        ('euler', 'Euler numbers', 'One sequence.<br><em>Several perspectives.</em>',
         'Follow packets, polynomial coordinates, and exact residual correction through one extended derivation.',
         'EULER_PACKETS', 'Read the Euler derivation',
         '<dl class="home-sequence" aria-label="Signed even Euler numbers">'
         + ''.join('<div><dt>E<sub>'+str(n)+'</sub></dt><dd>'+value+'</dd></div>'
                   for n, value in [(0, '1'), (2, '−1'), (4, '5'), (6, '−61'), (8, '1385')]) + '</dl>'),
        ('factorial', 'Factorial lanes', 'One factorial.<br><em>Ten exact lanes.</em>',
         'Reconstruct 34!, then follow hypergeometric coordinates and an exact five-adic reciprocal calculation.',
         'FACTORIAL_LANES', 'Read the factorial-lane derivation',
         '<div class="home-motif home-lanes" aria-hidden="true"><span>34!</span>'
         '<span class="home-motif-arrow">↔</span><div>'
         + ''.join('<span>'+str(n)+'</span>' for n in range(10)) + '</div></div>'),
        ('wavelet', 'Wavelets', 'One signal.<br><em>Exact multiresolution.</em>',
         'Follow four Haar levels, a finite filter, and exact residual repair. A complete Python calculation is included.',
         'WAVELET_POLYPHASE', 'Read the wavelet and polyphase derivation',
         '<div class="home-motif home-wavelet" aria-hidden="true"><svg viewBox="0 0 360 62" '
         'fill="none" stroke="currentColor" stroke-width="2"><path '
         'd="M0 31h22V9h24v42h24V21h24v20h24V5h24v52h24V19h24v24h24V13h24v36h24V25h24v12h24V17h24v28h26"/>'
         '</svg></div>'),
        ('stirling', 'Counting families', 'One partition triangle.<br><em>Two families.</em>',
         'Start with set partitions, obtain Bell and ordered Bell numbers, and follow the signed inverse and reciprocal packets.',
         'STIRLING_BELL_FUBINI', 'Read the Stirling, Bell and Fubini derivation',
         '<div class="home-motif home-counting" aria-hidden="true"><span>Partitions</span>'
         '<span class="home-motif-arrow">→</span><div><span>Bell</span><span>Ordered Bell</span></div></div>'),
        ('roots', 'Polynomial packets', 'One polynomial.<br><em>Three character packets.</em>',
         'Project degrees with roots of unity, move into falling-factorial coordinates, and reconstruct an exact value.',
         'ROOTS_UNITY_FALLING_FACTORIAL', 'Read the roots-of-unity and Newton derivation',
         '<div class="home-motif home-packets" aria-hidden="true"><span>Roots of unity</span>'
         '<span class="home-motif-arrow">↔</span><span>Newton<br>coordinates</span></div>'),
    ]
    panels = ''.join(
        '<section class="home-slide" id="home-research-'+key+'" aria-labelledby="home-'+key+'-title">'
        '<p class="home-feature-kicker">Research preview <span aria-hidden="true">/</span> '+label+'</p>'
        '<h2 id="home-'+key+'-title">'+title+'</h2><p class="home-feature-description">'+description+'</p>'
        +motif+'<a class="home-feature-link" href="collection/demonstrations/'+target+'.html">'+link+
        '<span aria-hidden="true">↗</span></a></section>'
        for key, label, title, description, target, link, motif in examples)
    topic_labels = {'euler': 'Euler', 'factorial': 'Factorials', 'wavelet': 'Wavelets',
                    'stirling': 'Counting', 'roots': 'Polynomials'}
    topics = ''.join(
        '<button type="button" id="home-topic-'+key+'" aria-controls="home-research-'+key+'">'+topic_labels[key]+'</button>'
        for key, label, *_ in examples)
    return ('<div class="home-showcase" aria-label="Research examples">'
            '<div class="home-topics" aria-label="Choose a research example" hidden>'+topics+'</div>'
            '<div class="home-feature">'+panels+
            '<div class="home-slide-controls" hidden><p class="home-slide-position" aria-live="polite" aria-atomic="true"></p>'
            '<div class="home-slide-arrows"><button type="button" data-slide-previous aria-label="Previous research example">'
            '<span aria-hidden="true">←</span></button><button type="button" data-slide-next aria-label="Next research example">'
            '<span aria-hidden="true">→</span></button></div></div></div></div>')


def home_page():
    routes = [
        ('Understand the project', 'An introduction and a first worked example.', 'NEW_READER', 'Start here'),
        ('Read the mathematics', 'Papers and books, with assumptions in view.', 'MATHEMATICS', 'Papers & books'),
        ('Examine a proof', 'Statements, formal sources, and recorded evidence.', 'PROOF_REVIEW', 'Proofs & sources'),
        ('Try the software', 'Runnable examples and their expected output.', 'SOFTWARE', 'Examples & tools'),
    ]
    cards = ''.join(
        '<a class="home-route" href="collection/routes/'+key+'.html"><span class="home-route-number" aria-hidden="true">'+str(index).zfill(2)+'</span>'
        '<div class="home-route-content"><p class="home-route-label">'+html.escape(label)+'</p><h3>'+title+'</h3><p>'+description+'</p></div>'
        '<span class="home-route-arrow" aria-hidden="true">↗</span></a>'
        for index, (title, description, key, label) in enumerate(routes, 1))
    return '''<section class="home-hero" aria-labelledby="home-title">
<div class="home-copy"><p class="home-kicker">The Komorebi research collection</p>
<h1 id="home-title">Explore the ideas.<br><em>Follow the evidence.</em></h1>
<p class="home-lede">A place to read mathematics, inspect the reasoning, and try the calculations for yourself.</p>
<div class="home-actions"><a class="button" href="collection/START_HERE.html">Start with the introduction <span aria-hidden="true">→</span></a><a class="button button-secondary" href="works.html">Browse all works</a></div>
<a class="home-jump" href="#home-ways-title">Find your starting point <span aria-hidden="true">↓</span></a>
</div>'''+research_slides()+'''</section>
<section class="home-ways" aria-labelledby="home-ways-title"><div class="home-section-heading"><h2 id="home-ways-title">Find your starting point.</h2><a href="collection/READING_ROUTES.html">All reading routes <span aria-hidden="true">↗</span></a></div>
<div class="home-route-grid">'''+cards+'''</div></section>
<section class="home-toolbox" id="home-interactive-title" aria-labelledby="home-toolbox-title"><div class="home-section-heading"><h2 id="home-toolbox-title">A few useful tools.</h2><p>Explore an idea, or find a specific passage.</p></div>
<div class="home-tool-links"><a href="interactive.html"><span class="home-tool-icon" aria-hidden="true">↔</span><span><strong>Interactive diagrams</strong><small>Change the inputs. Follow the result.</small></span><span aria-hidden="true">↗</span></a>
<a href="search.html"><svg class="home-tool-icon site-search-icon" viewBox="0 0 20 20" width="24" height="24" aria-hidden="true" focusable="false"><circle cx="8.5" cy="8.5" r="5.5"/><path d="m12.5 12.5 4 4"/></svg><span><strong>Search the collection</strong><small>Find a work, statement, or passage.</small></span><span aria-hidden="true">↗</span></a>
<a href="notation.html"><span class="home-tool-icon" aria-hidden="true">α</span><span><strong>Look up notation</strong><small>Find symbols and their source context.</small></span><span aria-hidden="true">↗</span></a></div></section>
<div class="home-notes"><details class="home-more"><summary>Explore the collections and how they connect</summary>
<div class="home-collection-list"><h2>Three repositories, one place to begin</h2><dl>
<dt><a href="collection/index.html">Operation KOMOREBI</a></dt><dd>Papers, books, research programs, formal sources and evidence.</dd>
<dt><a href="math/index.html">Komorebi Math</a></dt><dd>A Python library for finite mathematical constructions and inspectable certificates.</dd>
<dt><a href="polyphase/index.html">Polyphase Float</a></dt><dd>A C library for arbitrary-precision binary floating-point arithmetic.</dd></dl>
<h3>What connects the work?</h3><p>Describe an object in parts, transfer operations through those parts, and account for what a change of representation preserves or loses.</p>
<ul><li><a href="collection/PROJECT_MAP.html">See the project map</a> — explore the twelve core papers, related books and documented connections.</li>
<li><a href="collection/DEMONSTRATIONS.html">Follow a complete demonstration</a> — work through a calculation, run its program and follow the source evidence.</li>
<li><a href="collection/SPECIAL_FUNCTIONS.html">Explore Special Functions</a> — read the current volumes, compare five families, and run the coupled-function lab.</li></ul></div></details>
<details class="home-status"><summary>How to read completion and verification</summary><p>The collection records completion, formal coverage, and confidence separately. A linked file does not mean every claim has been verified. Software is beta.</p><p><a href="collection/COMPLETION_STATUS.html">Read the guide to evidence and status</a></p></details></div>'''
