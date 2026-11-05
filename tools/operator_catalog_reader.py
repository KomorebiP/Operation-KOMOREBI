"""Reader lookup and search routes for the maintained operator catalog."""
from __future__ import annotations

import hashlib
import html
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit

from operator_catalog import INDEX_PATH, RELATIONS_PATH, entry_path


def page_url(path: str) -> str:
    """Use the reader's ordinary Markdown routing, retaining entry fragments."""
    from build_reader_site import document_url
    source, marker, fragment = path.partition('#')
    return document_url('collection', source) + marker + fragment


def inline_parts(text: str) -> list[dict[str, str]]:
    """Keep small inline formulas separate from prose for safe reader rendering."""
    return [dict(type='math', text=part[1:-1]) if re.fullmatch(r'\$[^$\n]+\$', part)
            else dict(type='text', text=part)
            for part in re.split(r'(\$[^$\n]+\$)', text) if part]


def inline_html(text: str) -> str:
    return ''.join('<span class="arithmatex">\\(' + html.escape(part['text']) + '\\)</span>'
                   if part['type'] == 'math' else html.escape(part['text'])
                   for part in inline_parts(text))


def search_text(entry: dict, catalog: dict) -> str:
    """Share the catalog's actual names, formulas, scope, and source vocabulary."""
    number = int(entry['id'].split('-')[1])
    sources = [catalog['sources'][code]['title'] for code in entry['source_codes']]
    return ' '.join([entry['id'], entry['id'].replace('-', ''), 'OP' + str(number),
                     entry['name'], entry['section'], entry['kind'], entry['formula'],
                     entry['scope'], entry.get('review_note', ''), *sources,
                     *entry.get('check_ids', []), *entry.get('related_ids', [])])


def lookup_html(catalog: dict, page: str) -> str:
    """Add a small optional lookup without replacing the static family index."""
    e = html.escape
    families = {family['id']: family for family in catalog['families']}
    body = (
        '<section id="operator-catalog-lookup" class="operator-catalog-lookup" '
        'aria-labelledby="operator-catalog-lookup-title">'
        '<h2 id="operator-catalog-lookup-title">Find an operator</h2>'
        '<p id="operator-catalog-help">Search a name, OP number, formula, or words from '
        'the scope. Try “falling factorial”, “metric”, or “OP-025”. '
        'Each result opens its formula, assumptions, sources, and related entries.</p>'
        '<noscript><p>Quick lookup needs JavaScript. Browse the family links and '
        'alphabetical index below, or use your browser’s Find command.</p></noscript>'
        '<form id="operator-catalog-form" role="search" aria-label="Operator catalog" '
        'aria-describedby="operator-catalog-help operator-catalog-evidence-help" hidden>'
        '<div class="operator-catalog-query"><label for="operator-catalog-query">'
        'Name, OP number, or words to find</label>'
        '<input id="operator-catalog-query" type="search" name="q" autocomplete="off"></div>'
        '<div class="operator-catalog-filters"><div>'
        '<label for="operator-catalog-family">Family</label>'
        '<select id="operator-catalog-family" name="family"><option value="">All families</option>')
    body += ''.join('<option value="' + e(f['id'], quote=True) + '">' +
                    e(f['id'] + '. ' + f['title']) + '</option>' for f in catalog['families'])
    body += (
        '</select></div><div><label for="operator-catalog-checks">Finite examples</label>'
        '<select id="operator-catalog-checks" name="checks"><option value="">All entries</option>'
        '<option value="linked">With linked finite checks</option>'
        '<option value="unlinked">Without linked finite checks</option></select></div></div>'
        '<p id="operator-catalog-evidence-help">A linked finite check covers a named example '
        'or failure control. Read its scope in the entry.</p>'
        '<div class="operator-catalog-actions"><button type="submit">Find operators</button>'
        '<button type="reset">Clear filters</button></div></form>'
        '<p id="operator-catalog-status" role="status" aria-live="polite" aria-atomic="true" hidden></p>'
        '<div id="operator-catalog-matches" hidden><h3 id="operator-catalog-results-title" '
        'tabindex="-1">Matching entries</h3><ul id="operator-catalog-results">')
    for entry in sorted(catalog['operators'], key=lambda row: (row['name'].casefold(), row['id'])):
        target = page_url(entry_path(entry, catalog))
        path, _, fragment = target.partition('#')
        href = posixpath.relpath(path, posixpath.dirname(page)) + '#' + fragment
        checks = len(entry['check_ids'])
        evidence = (str(checks) + (' finite check linked' if checks == 1 else ' finite checks linked')) \
            if checks else 'No finite check assigned'
        family = families[entry['family_id']]
        body += (
            '<li id="operator-result-' + e(entry['id'].lower(), quote=True) + '" '
            'data-operator-entry data-operator-id="' + e(entry['id'], quote=True) + '" '
            'data-name="' + e(entry['name'], quote=True) + '" '
            'data-family="' + e(entry['family_id'], quote=True) + '" '
            'data-checks="' + str(checks) + '" '
            'data-search="' + e(search_text(entry, catalog), quote=True) + '">'
            '<h4><a href="' + e(href, quote=True) + '"><span class="operator-catalog-id">' +
            e(entry['id']) + '</span> ' + e(entry['name']) + '</a></h4>'
            '<p class="operator-catalog-family">' + e(family['id'] + '. ' + family['title']) + '</p>'
            '<p class="operator-catalog-scope">' + inline_html(entry['scope']) + '</p>'
            '<p class="operator-catalog-evidence">' + e(entry['kind']) + ' · ' + e(evidence) + '</p></li>')
    return body + '</ul></div></section>'


def source_work_ids(site, entry: dict, catalog: dict) -> list[str]:
    """Associate a search row only with works reached by its recorded sources."""
    works = set()
    components = getattr(site, 'components', {})
    collection = site.repos.get('collection', 'KomorebiP/Operation-KOMOREBI').casefold()
    for code in entry['source_codes']:
        url = urlsplit(catalog['sources'][code]['url'])
        parts = url.path.strip('/').split('/')
        if url.hostname != 'github.com' or len(parts) < 5 or parts[2] != 'blob':
            continue
        if '/'.join(parts[:2]).casefold() != collection:
            continue
        path = unquote('/'.join(parts[4:]))
        if '..' in PurePosixPath(path).parts:
            continue
        works.update(site.reader.document_works('collection', path))
        for work, component in components.items():
            destination = component.get('destination', '').rstrip('/')
            if destination and (path == destination or path.startswith(destination + '/')):
                works.add(work)
    return sorted(works & set(components))


def search_entries(site, catalog: dict) -> list[dict]:
    """Give each operator and relation an anchored collection-search result."""
    records = []
    for entry in catalog['operators']:
        checks = len(entry['check_ids'])
        evidence = ('Finite checks linked: ' + ', '.join(entry['check_ids']) + '.') \
            if checks else 'No finite fixture is assigned to this entry.'
        preview = entry['scope'] + ' ' + evidence
        records.append(dict(
            title=entry['id'] + ' · ' + entry['name'], group='Collection', kind='Guides',
            url=page_url(entry_path(entry, catalog)), work_ids=source_work_ids(site, entry, catalog),
            text=search_text(entry, catalog), preview=preview, preview_parts=inline_parts(preview),
            math_preview=entry['formula'][1:-1]))
    operators = {entry['id']: entry for entry in catalog['operators']}
    for relation in catalog['relations']:
        identifier = relation['id']
        number = int(identifier.split('-')[1])
        preview = (relation['assumptions'] + ' Finite checks linked: ' +
                   ', '.join(relation['check_ids']) + '.')
        text = ' '.join([
            identifier, identifier.replace('-', ''), 'REL' + str(number), relation['name'],
            'Composition and compatibility law', relation['law_tex'], relation['assumptions'],
            *relation['operator_ids'], *[operators[key]['name'] for key in relation['operator_ids']],
            *relation['check_ids']])
        records.append(dict(
            title=identifier + ' · ' + relation['name'], group='Collection', kind='Guides',
            url=page_url(RELATIONS_PATH + '#' + identifier.lower()), work_ids=[],
            text=text, preview=preview, preview_parts=inline_parts(preview),
            math_preview=relation['law_tex']))
    return records


def script_tag(site, page: str) -> str:
    """Load the enhancement only on the catalog index."""
    if page != page_url(INDEX_PATH):
        return ''
    name = 'operator-catalog.js'
    digest = hashlib.sha256((site.root / 'website/assets' / name).read_bytes()).hexdigest()[:12]
    url = site.rel('assets/' + name, page) + '?v=' + digest
    return '<script defer src="' + html.escape(url, quote=True) + '"></script>'
