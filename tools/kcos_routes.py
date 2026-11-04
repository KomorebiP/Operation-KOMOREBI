"""Compact reading paths into the published K-COS manuscript."""
from html import escape


REQUIRED_LABELS = (
    'ch:gaussian', 'ch:packets', 'app:atlas', 'app:lean',
    'sec:worked-law', 'sec:worked-stream', 'sec:worked-tilt',
    'sec:worked-enclosure',
)
CONTINUATION = 'collection/works/monographs-cos-method-formal-continuation.html'
WORKED_EXAMPLE = (
    ('sec:worked-law', 'Factor and law',
     'Start with the factor, spectrum, and exact probability law.'),
    ('sec:worked-stream', 'Storage blocks',
     'Follow the same factor through three storage blocks.'),
    ('sec:worked-tilt', 'Tilt and packets',
     'Revisit the example under exponential tilting.'),
    ('sec:worked-enclosure', 'Probability enclosure',
     'Complete the calculation and check the requested accuracy.'),
)


def label_targets(book):
    """Resolve each route once, using the nodes that own the source labels.

    Prepared chapters share a cross-reference dictionary, so iterating each
    chapter.labels would count the same destination repeatedly.
    """
    labels = {}
    for spec, _, chapter in book['chapters']:
        for node in chapter.nodes:
            for label in node.get('labels', []):
                if label not in REQUIRED_LABELS:
                    continue
                url, anchor = spec.get('url'), node.get('id')
                if not url or not anchor:
                    raise ValueError('K-COS reading-path label '+label+
                                     ' needs a published page and anchor')
                target = url+'#'+anchor
                if label in labels:
                    raise ValueError('Duplicate K-COS reading-path label '+label+
                                     ': '+labels[label]+' and '+target)
                labels[label] = target
    missing = [label for label in REQUIRED_LABELS if label not in labels]
    if missing:
        raise ValueError('Missing K-COS reading-path labels: '+', '.join(missing))
    destinations = {}
    for label, target in labels.items():
        if target in destinations:
            raise ValueError('Duplicate K-COS reading-path destination '+target+
                             ': '+destinations[target]+' and '+label)
        destinations[target] = label
    return labels


def calculation_navigation(reader, book):
    """Place a route control after each complete worked-example section.

    Controls are separate from authored nodes. A following heading at the same
    or a higher level ends the section; a final section ends with its chapter.
    """
    from readable_chapters import HEADINGS
    labels = label_targets(book)
    controls = {}
    total = len(WORKED_EXAMPLE)
    for position, (label, _, _) in enumerate(WORKED_EXAMPLE):
        page, anchor = labels[label].split('#', 1)
        owners = [(chapter, i) for spec, _, chapter in book['chapters']
                  if spec['url'] == page for i, node in enumerate(chapter.nodes)
                  if node.get('id') == anchor]
        if len(owners) != 1:
            raise ValueError('K-COS calculation label needs one owning section: '+label)
        chapter, start = owners[0]
        heading = chapter.nodes[start]
        if heading['kind'] not in HEADINGS:
            raise ValueError('K-COS calculation label must identify a section heading: '+label)
        level = HEADINGS[heading['kind']]
        end = next((i for i in range(start+1, len(chapter.nodes))
                    if chapter.nodes[i]['kind'] in HEADINGS and
                    HEADINGS[chapter.nodes[i]['kind']] <= level), len(chapter.nodes))
        if end == start+1:
            raise ValueError('K-COS calculation section has no content: '+label)
        placement = (page, chapter.nodes[end-1]['id'])
        if placement in controls:
            raise ValueError('Overlapping K-COS calculation sections: '+label)

        def link(target, text, description=None):
            aria = ' aria-label="'+escape(description, quote=True)+'"' if description else ''
            return '<a href="'+escape(reader.site.rel(target, page), quote=True)+'"'+aria+'>'+escape(text)+'</a>'

        body = ('<nav class="reading-guide-return reading-actions" '
                'aria-label="Worked calculation, step '+str(position+1)+' of '+str(total)+'" '
                'data-kcos-calculation="'+escape(label, quote=True)+'">'
                '<strong>Worked calculation · '+str(position+1)+' of '+str(total)+'</strong>')
        if position:
            previous, title, _ = WORKED_EXAMPLE[position-1]
            body += link(labels[previous], '← Previous: '+title,
                         'Previous calculation step: '+title)
        body += link(book['config']['index']+'#kcos-worked-example', 'All calculation steps')
        if position+1 < total:
            following, title, _ = WORKED_EXAMPLE[position+1]
            body += link(labels[following], 'Next: '+title+' →',
                         'Next calculation step: '+title)
        controls[placement] = body+'</nav>'
    return controls


def reading_paths(reader, book, page):
    """Return a small index guide, with every manuscript link label-resolved."""
    labels = label_targets(book)

    def link(label, title):
        target = escape(reader.site.rel(labels[label], page), quote=True)
        return '<a href="'+target+'">'+escape(title)+'</a>'

    body = ('<section class="kcos-reading-guide" aria-labelledby="kcos-reading-paths">'
            '<h2 id="kcos-reading-paths">Choose a reading path</h2><ul>')
    body += ('<li>'+link('ch:gaussian', 'Full matrix-to-tail route')+
             ' — Begin with Gaussian quadratic forms, then follow the structured '
             'operators, spectral recovery, inversion, and certified computation.</li>')
    body += ('<li>'+link('ch:packets', 'Starting from a supplied spectrum')+
             ' — Review the '+link('ch:gaussian', 'Gaussian setup')+
             ', then read from exponential tilting and spectral packets through '
             'certified probability enclosures.</li>')
    body += ('<li>'+link('app:atlas', 'Visual studies')+
             ' — Explore the representations and their error budgets in Appendix A.</li></ul>')
    body += ('<nav class="paper-reading-path" aria-labelledby="kcos-worked-example">'
             '<h3 id="kcos-worked-example">Follow one calculation</h3><ol>')
    for label, title, description in WORKED_EXAMPLE:
        target = escape(reader.site.rel(labels[label], page), quote=True)
        body += ('<li><a href="'+target+'"><span>'+escape(title)+'</span>'+
                 escape(description)+'</a></li>')
    body += '</ol></nav>'
    continuation = escape(reader.site.rel(CONTINUATION, page), quote=True)
    body += ('<p><strong>Formal companion.</strong> Read '+
             link('app:lean', 'Appendix B')+
             ' for the monograph’s theorem correspondence and formal coverage. '
             'The <a href="'+continuation+'">separate formal continuation</a> '
             'records subsequent work.</p></section>')
    return body
