"""Editorial discipline discovery for the public research collection.

Classification is independent of recorded completion, Lean coverage and evidence.
This module neither changes source files nor infers mathematical correctness.
"""
from collections import Counter
from html import escape
import json

CATALOG_PATH = 'manifests/discipline-catalog.json'
GROUP_LABELS = {
    'papers': 'Core paper',
    'monographs': 'Book / monograph',
    'research': 'Research program',
    'packages': 'Software package',
    'experiments': 'Experiment',
}


def load_catalog(root, registry, assessments):
    """Require one explicit primary discipline for every indexed primary work."""
    data = json.loads((root / CATALOG_PATH).read_text(encoding='utf-8'))
    if data.get('schema') != 1:
        raise ValueError('Unsupported discipline catalogue schema')
    subjects = data.get('disciplines', {})
    if set(subjects) != {'math', 'cs', 'physics', 'other'}:
        raise ValueError('Disciplines must be mathematics, CS, physics and other')
    entries = data.get('components', [])
    ids = [row['id'] for row in entries]
    expected = {row['id'] for row in registry['components']}
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError('Discipline catalogue must cover each indexed primary work exactly once')
    if not expected.issubset(assessments):
        raise ValueError('Missing assessment for a discipline catalogue entry')
    for row in entries:
        primary = row.get('primary')
        related = row.get('related', [])
        if primary not in subjects:
            raise ValueError('Unknown primary discipline for ' + row['id'])
        if not isinstance(related, list) or len(related) != len(set(related)):
            raise ValueError('Invalid related disciplines for ' + row['id'])
        if any(d not in subjects or d == primary for d in related):
            raise ValueError('Related discipline duplicates primary or is unknown: ' + row['id'])
    return data, {row['id']: row for row in entries}


def facet_records(root, registry, assessments):
    """Generate the same authoritative facets for work browsing and text search."""
    data, subjects = load_catalog(root, registry, assessments)
    works = {}
    for row in registry['components']:
        identifier = row['id']
        assessment = assessments[identifier]
        works[identifier] = {
            'discipline': subjects[identifier]['primary'],
            'related': subjects[identifier].get('related', []),
            'stage': assessment['stage'],
            'lean': assessment['lean'],
            'evidence': assessment['confidence'],
        }
    return {'schema': 1, 'disciplines': data['disciplines'], 'works': works}


def render_works_catalog(root, registry, components, assessments, status):
    """Render four accessible sections, then add independent client-side facets."""
    data, subjects = load_catalog(root, registry, assessments)
    labels = status['labels']
    indexed = [components[row['id']] for row in registry['components']]
    by_id = {row['id']: row for row in indexed}
    counts = Counter(subjects[row['id']]['primary'] for row in indexed)
    e = lambda value: escape(str(value), quote=True)

    def choices(kind, prompt, values):
        return ('<option value="">' + e(prompt) + '</option>' +
                ''.join('<option value="' + e(code) + '">' +
                        e(labels[kind][code][0]) + '</option>'
                        for code in labels[kind] if code in values))

    stages = {assessments[c['id']]['stage'] for c in indexed}
    lean = {assessments[c['id']]['lean'] for c in indexed}
    confidence = {assessments[c['id']]['confidence'] for c in indexed}

    out = [
        '<link rel="stylesheet" href="assets/discipline-catalog.css">',
        '<h1>Explore the research collection</h1>',
        '<p><a href="search.html">Search documents, proof references, Lean and code</a> · '
        '<a href="claims.html">Find individual statements by paper and type</a></p>',
        '<p class="catalog-intro">Browse by discipline and narrow by manuscript completion, '
        'recorded Lean coverage, and the strongest recorded evidence. These are separate '
        'dimensions: a completed reading edition need not prove an open conjecture.</p>',
        '<nav class="discipline-overview" aria-label="Choose a discipline">',
    ]
    for key, subject in data['disciplines'].items():
        out.append(
            '<a class="discipline-link" href="works.html?discipline=' + e(key) +
            '#catalog-results"><span class="discipline-name">' + e(subject['label']) +
            '</span><span class="discipline-count">' + str(counts[key]) +
            ' primary works</span><span class="discipline-detail">' +
            e(subject['description']) + '</span></a>'
        )
    out.append('</nav>')
    out += [
        '<form id="catalog-filters" class="catalog-filters" role="search">',
        '<div><label for="catalog-query">Search titles and subjects</label>'
        '<input type="search" id="catalog-query" name="q" autocomplete="off" '
        'placeholder="e.g. Hilbert 12, SKAT, packet, quantum"></div>',
        '<div><label for="catalog-discipline">Discipline</label>'
        '<select id="catalog-discipline"><option value="">All disciplines</option>' +
        ''.join('<option value="' + e(key) + '">' + e(x['label']) + '</option>'
                for key, x in data['disciplines'].items()) + '</select></div>',
        '<div><label for="catalog-stage">Completion stage</label><select id="catalog-stage">' +
        choices('stage', 'Any stage', stages) + '</select></div>',
        '<div><label for="catalog-lean">Lean coverage</label><select id="catalog-lean">' +
        choices('lean', 'Any Lean coverage', lean) + '</select></div>',
        '<div><label for="catalog-evidence">Evidence basis</label><select id="catalog-evidence">' +
        choices('confidence', 'Any evidence basis', confidence) + '</select></div>',
        '<div><label for="catalog-group">Publication type</label>'
        '<select id="catalog-group"><option value="">All publication types</option>' +
        ''.join('<option value="' + e(key) + '">' + e(label) + '</option>'
                for key, label in GROUP_LABELS.items()) + '</select></div>',
        '<div class="catalog-reset"><button type="reset">Clear all filters</button></div>',
        '</form>',
        '<p class="catalog-notice">Subject assignments are editorial finding aids, '
        'not evaluations. The completion and evidence labels reproduce the existing '
        'recorded assessments; a Lean contract covers only its declared claims. '
        'Read the <a href="collection/COMPLETION_STATUS.html">status guide</a> before '
        'interpreting them. Cross-disciplinary subjects have one primary home and '
        'may list related fields.</p>',
        '<div id="catalog-results">',
        '<p id="catalog-count" role="status" aria-live="polite">' +
        str(len(indexed)) + ' primary works · evidence status recorded ' +
        e(status.get('as_of', 'in the project manifest')) + '</p>',
        '<p id="catalog-empty" hidden>No matches. Try broader terms or clear a filter.</p>',
    ]
    for key, subject in data['disciplines'].items():
        entries = [c for c in indexed if subjects[c['id']]['primary'] == key]
        out.append('<section class="catalog-section" data-catalog-section="' +
                   e(key) + '" id="discipline-' + e(key) + '"><h2>' +
                   e(subject['label']) + ' <small>' + str(len(entries)) +
                   ' primary works</small></h2><div class="catalog-items">')
        for component in entries:
            identifier = component['id']
            assessment = assessments[identifier]
            listing = assessment.get('reader_listing', {})
            incubator = listing.get('placement') == 'incubator'
            meta = subjects[identifier]
            stage = labels['stage'][assessment['stage']][0]
            lean_name = labels['lean'][assessment['lean']][0]
            evidence_name = labels['confidence'][assessment['confidence']][0]
            summary = assessment.get('reader_summary') or component['summary']
            related = ', '.join(data['disciplines'][d]['label'] for d in meta.get('related', []))
            searchable = ' '.join((component['title'], summary, identifier,
                                   GROUP_LABELS[component['group']], subject['label'],
                                   related))
            out.append(
                '<article class="catalog-item" id="work-' + e(identifier) +
                '" data-search="' + e(searchable) + '" data-discipline="' + e(key) +
                '" data-stage="' + e(assessment['stage']) + '" data-lean="' +
                e(assessment['lean']) + '" data-evidence="' + e(assessment['confidence']) +
                '" data-group="' + e(component['group']) + '">'
                '<p class="catalog-type">' + e(GROUP_LABELS[component['group']]) +
                (' · Incubator' if incubator else '') + '</p>'
                '<h3><a href="collection/works/' + e(identifier) + '.html">' +
                e(component['title']) + '</a></h3><p>' + e(summary) + '</p>' +
                ('<p class="catalog-related">Related field: ' + e(related) + '</p>' if related else '') +
                '<dl class="catalog-assessment"><div><dt>Completion</dt><dd>' +
                e(stage) + '</dd></div><div><dt>Lean coverage</dt><dd>' +
                e(lean_name) + '</dd></div><div><dt>Evidence</dt><dd>' +
                e(evidence_name) + '</dd></div></dl>'
                '<p class="catalog-item-links"><a href="collection/STATUS_CATALOG.html#' +
                e(identifier) + '">Evidence record</a> · <a href="search.html?work=' +
                e(identifier) + '">Search within work</a></p></article>'
            )
        out.append('</div></section>')
    out += [
        '</div>',
        '<noscript><p>All works are listed by primary discipline. Filtering needs '
        'JavaScript, but every work and evidence record remains linked.</p></noscript>',
        '<script defer src="assets/discipline-catalog.js"></script>'
    ]
    return '\n'.join(out)
