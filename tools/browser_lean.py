"""Keep the former playground URL as an alias for our local browser compiler."""
import hashlib
import html
from html.parser import HTMLParser
import json

PAGE = 'lean/playground.html'
TARGET = 'lean/browser/index.html'


def build(reader):
    site = reader.site
    def asset(name):
        digest = hashlib.sha256((site.root / 'website/assets' / name).read_bytes()).hexdigest()[:12]
        return site.rel('assets/' + name, PAGE) + '?v=' + digest
    target = html.escape(site.rel(TARGET, PAGE), quote=True)
    body = f'''<link rel="stylesheet" href="{asset('lean-reader.css')}">
<section class="lean-browser">
<nav class="breadcrumbs" aria-label="Lean navigation"><a href="{site.rel('lean/index.html', PAGE)}">Inspect Lean</a></nav>
<header class="lean-heading"><h1>Lean workspace</h1>
<p class="lean-lede">Open our browser compiler to choose a published workspace, edit a proof, and check it on your device.</p></header>
<p><a class="button" data-lean-workspace href="{target}">Open the Lean workspace</a></p>
<noscript><p>Follow the workspace link to continue.</p></noscript>
</section><script defer src="{asset('lean-playground.js')}"></script>'''
    site.page(PAGE, 'Lean workspace', body)
    site.write('lean/playground.json', json.dumps(dict(
        schema=2, source_revision=site.revision, target=TARGET,
        execution='local WebAssembly', retired_route=True,
        build_runs_lean=False, changes_recorded_verification=False), indent=2) + '\n')
    return dict(redirects=1, execution='local WebAssembly', build_runs_lean=False)


def verify(root, documents):
    class Routes(HTMLParser):
        def __init__(self):
            super().__init__(); self.targets = []; self.frames = []; self.resources = []
            self.in_main = False; self.main_count = 0
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'main':
                self.in_main = True; self.main_count += 1
            if tag == 'a' and 'data-lean-workspace' in attrs:
                self.targets.append(attrs.get('href'))
            if tag == 'iframe':
                self.frames.append(attrs)
            if self.in_main and tag in {'a', 'script', 'link'}:
                self.resources.append(attrs.get('href', attrs.get('src', '')))
        def handle_endtag(self, tag):
            if tag == 'main':
                self.in_main = False
    from urllib.parse import urlsplit
    data = json.loads((root / 'lean/playground.json').read_bytes())
    assert data['source_revision'] == documents.get('source_revision', data['source_revision'])
    assert data['schema'] == 2 and data['target'] == TARGET and data['retired_route'] is True
    assert data['execution'] == 'local WebAssembly'
    assert data['build_runs_lean'] is False and data['changes_recorded_verification'] is False
    parser = Routes(); parser.feed((root / PAGE).read_text(encoding='utf8'))
    assert parser.main_count == 1
    assert parser.targets == ['browser/index.html']
    assert not parser.frames
    assert all(not urlsplit(url).scheme and not urlsplit(url).netloc for url in parser.resources)
    return dict(redirects=1, target=TARGET, external_frames=0, build_runs_lean=False)
