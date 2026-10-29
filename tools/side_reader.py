"""Build an on-site catalogue and two-pane reading workspace."""
import html
import json
import re
from urllib.parse import urlsplit


def catalogue(site):
    pages = {}
    for file in sorted(site.output.rglob('*.html')):
        path = file.relative_to(site.output).as_posix()
        if path.startswith('assets/') or path in {'side-by-side.html', '404.html'}:
            continue
        text = file.read_text(encoding='utf-8')
        title = re.search(r'<title>(.*?)</title>', text, re.S)
        pages[path] = html.unescape(title[1]).removesuffix(' · Komorebi')
    entries = []
    seen = set()
    for row in site.search:
        if urlsplit(row['url']).path not in pages or row['url'] in seen:
            continue
        seen.add(row['url'])
        entries.append(dict(url=row['url'], title=row['title'], kind=row.get('kind', 'Guides'),
                            works=row.get('work_ids', []), text=row.get('text', '')[:350]))
    represented = {urlsplit(row['url']).path for row in entries}
    for path, title in pages.items():
        if path not in represented:
            work = path.split('/')[1] if path.startswith('read/') and path.count('/') > 1 else ''
            entries.append(dict(url=path, title=title, kind='Guides',
                                works=[work] if work in site.components else [], text=''))
    from readable_chapters import BOOKS
    works = []
    for row in site.registry['components']:
        work = row['id']
        hub = 'collection/works/'+work+'.html'
        pdf = site.reader.primary_pdf(work)
        left = BOOKS[work]['index'] if work in BOOKS else pdf['url'] if pdf else hub
        edition = site.editorial_editions.get(work)
        if edition:
            left = edition['manuscript_url']
        works.append(dict(id=work, title=site.components[work]['title'],
                          left=left, right=hub+'#written-proofs'))
    return dict(schema=1, revision=site.revision, pages=pages, works=works, entries=entries)


def pane(side):
    name = side.capitalize()
    return f'''<section class="side-pane" id="{side}-pane" aria-labelledby="{side}-heading">
<header class="side-pane-header"><div class="side-pane-top"><h2 id="{side}-heading">{name} pane</h2>
<div class="side-pane-actions"><button type="button" id="{side}-read" disabled>Read {side} pane</button>
<a id="{side}-standalone" target="_blank" rel="noopener" hidden>Open on its own <span class="side-new-tab">(new tab)</span></a></div></div>
<p class="side-current" id="{side}-current">Choose a document</p>
<details class="side-picker" id="{side}-picker" open><summary>Choose a document for the {side} pane</summary>
<form id="{side}-form"><div class="side-filter-grid"><div>
<label for="{side}-work">Work</label><select id="{side}-work"><option value="">All works and guides</option></select></div><div>
<label for="{side}-kind">Type</label><select id="{side}-kind"><option value="">All types</option></select></div></div>
<label for="{side}-query">Find a title, claim or phrase</label><input id="{side}-query" type="search" autocomplete="off">
<label for="{side}-document">Document or passage</label><select id="{side}-document" size="6" required></select>
<p class="status" id="{side}-count" role="status" aria-live="polite"></p>
<button type="submit">Open in {side} pane</button><button type="reset" class="side-secondary">Clear filters</button></form></details>
<label class="side-send" for="{side}-send"><input type="checkbox" id="{side}-send">Open links from this document in the other pane</label>
</header><p id="{side}-status" class="status side-load-status" role="status" aria-live="polite"></p>
<iframe id="{side}-frame" class="side-frame" title="{name} reading pane" hidden></iframe>
</section>'''


def build(site):
    data = catalogue(site)
    site.write('side-reader-index.json', json.dumps(data, ensure_ascii=False)+'\n')
    body = '''<div class="side-heading"><h1>Read side by side</h1>
<p>Keep a paper open while you follow a claim, written proof, Lean source, program or worked example.</p></div>
<noscript><p>This workspace needs JavaScript. You can still open <a href="documents.html">papers</a>,
<a href="claims.html">claims</a> and <a href="collection/HAND_WORKED_EXAMPLES.html">worked examples</a> in separate tabs.</p></noscript>
<div id="side-reader" data-index="side-reader-index.json?v='''+site.revision+'''" hidden>
<div class="side-toolbar"><div class="side-view" role="group" aria-label="Visible reading panes">
<button type="button" data-side-view="both" aria-pressed="true">Both panes</button>
<button type="button" data-side-view="left" aria-pressed="false">Left only</button>
<button type="button" data-side-view="right" aria-pressed="false">Right only</button></div>
<button type="button" id="side-swap">Swap sides</button><button type="button" id="side-share">Copy link to this pair</button>
<button type="button" id="side-focus" aria-pressed="false">Focus on reading</button>
<details class="side-layout"><summary>Layout and help</summary>
<label for="side-width">Left pane width <output id="side-width-value" for="side-width">50%</output></label>
<input type="range" id="side-width" min="35" max="65" value="50" step="5">
<p>Each pane scrolls independently. Use its document picker to change what you read.
To follow a reference without moving the current page, turn on <strong>Open links from this document in the other pane</strong>.
External links and the full PDF viewer open in a new tab. PDF toolbar links stay within the PDF viewer.</p>
<p>Use <strong>Read left pane</strong> or <strong>Read right pane</strong> to move keyboard focus into a document.
Its <strong>Return to pane controls</strong> links bring you back. The browser Back button restores earlier pairs.
On small screens, show either pane at full width, or choose Both panes to stack them.</p>
<p>Pair links keep the document addresses and HTML passage anchors. PDF toolbar page and zoom changes are not included.
These reading links do not change the recorded proof or Lean status.</p></details></div>
<div id="side-share-fallback" hidden><label for="side-share-url">Link to this pair</label><input id="side-share-url" type="url" readonly></div>
<div class="side-panes" id="side-panes">'''+pane('left')+pane('right')+'''</div></div>
<p id="side-status" role="status" aria-live="polite">Loading the document list…</p>
<p><a href="documents.html">Browse papers and PDFs</a> · <a href="collection/ACCESSIBILITY.html">Reading and accessibility help</a></p>
<script defer src="assets/side-reader-core.js?v='''+site.revision+'''"></script>
<script defer src="assets/side-reader.js?v='''+site.revision+'''"></script>'''
    site.page('side-by-side.html', 'Read side by side', body)
    return dict(pages=len(data['pages']), entries=len(data['entries']), works=len(data['works']))


def check(root, pages):
    from check_reader_site import check_search_targets
    data = json.loads((root/'side-reader-index.json').read_bytes())
    build = json.loads((root/'build-info.json').read_bytes())
    assert data['revision'] == build['collection_revision']
    assert data['schema'] == 1 and len(data['works']) == build['works']
    assert 'side-by-side.html' not in data['pages']
    assert set(data['pages']) == set(pages)-{'side-by-side.html', '404.html'}
    check_search_targets(data['entries'], pages)
    for work in data['works']:
        check_search_targets([{'url':work['left']}, {'url':work['right']}], pages)
    assert {row['kind'] for row in data['entries']} >= {'Claims','Written proofs','Lean','Code','Examples'}
    page = pages['side-by-side.html']
    assert len(page.iframes) == 2
    assert {'side-reader','side-swap','side-share','side-width','left-document','right-document'} <= set(page.ids)
    return dict(pages=len(data['pages']), entries=len(data['entries']), works=len(data['works']))
