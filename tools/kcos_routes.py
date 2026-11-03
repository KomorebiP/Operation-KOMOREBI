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


def _label_targets(book):
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


def reading_paths(reader, book, page):
    """Return a small index guide, with every manuscript link label-resolved."""
    labels = _label_targets(book)

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
