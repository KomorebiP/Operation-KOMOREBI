"""Bind the retained Machine-Native Reasoning result map to reading routes.

Call prepare_scope(reader, book) after constructing chapters and proof_pairs,
then publish_scope(reader, book) from the reading edition's publish_start.
This resolves lexical declaration locations. It never executes Lean or turns a
source-map status into a fresh proof-verification claim.
"""
import hashlib
import html
import json
import re

WORK = 'monographs-machine-native-reasoning'
BASE = 'monographs/machine-native-reasoning/'
PAGE = 'read/' + WORK + '/formal-scope.html'
MAP = BASE + 'THEOREM_MAP.json'
MODULES = BASE + 'MODULES.json'
ADMISSION = BASE + 'release/ADMISSION_RECORD.json'
READER_RECORD = BASE + 'reader/READER_VERIFICATION.json'
ORIGINAL = BASE + 'source/core_v0.2.tex'
READER_SOURCE = BASE + 'reader/source/book.tex'
FORMAL_CORRESPONDENCE = BASE + 'reader/source/formal_correspondence.tex'
RESOURCES = [
    (MAP, 'Source-to-Lean result map'),
    (MODULES, 'Registered production modules'),
    (ADMISSION, 'Accepted release record'),
    (READER_RECORD, 'Reviewed reader publication record'),
    (BASE + 'release/ACCEPTED_PROGRESS_LEDGER.md', 'Accepted progress ledger'),
    (BASE + 'release/REPORT.md', 'Release verification report'),
    (BASE + 'release/BOOK_RECOVERY.md', 'Separate expanded-book recovery record'),
    (BASE + 'reader/WIDER_MONOGRAPH_STATUS.md', 'Wider monograph status'),
    (ORIGINAL, 'Unchanged Reviewed Core v0.2 statements'),
    (FORMAL_CORRESPONDENCE, 'Authored formal correspondence chapter'),
]


def _mask_source(text):
    """Hide comments and strings, keeping every source offset and newline."""
    clean = list(text)
    i, depth, string = 0, 0, False
    while i < len(text):
        pair = text[i:i+2]
        if depth:
            size = 2 if pair in {'/-', '-/'} else 1
            if pair == '/-': depth += 1
            elif pair == '-/': depth -= 1
        elif string:
            size = 2 if text[i] == '\\' and i + 1 < len(text) else 1
            if text[i] == '"': string = False
        elif pair == '/-':
            depth, size = 1, 2
        elif pair == '--':
            end = text.find('\n', i)
            size = (len(text) if end < 0 else end) - i
        elif text[i] == '"':
            string, size = True, 1
        else:
            i += 1
            continue
        for j in range(i, min(i + size, len(text))):
            if text[j] != '\n': clean[j] = ' '
        i += size
    return ''.join(clean)


def qualified_declarations(text):
    """Return named declaration locations with their source namespaces.

    These names are navigation aids, not an elaborated declaration inventory.
    The caller requires a unique location for every registered endpoint.
    """
    from lean_reader import declarations
    masked = _mask_source(text)
    by_line = {}
    for entry in declarations(masked):
        by_line.setdefault(entry['line'], []).append(entry)
    scopes, result = [], []
    for line, value in enumerate(masked.splitlines(), 1):
        event = re.match(r'^\s*(?:noncomputable\s+)?(namespace|section|end)\b\s*([\w.\']*)', value)
        if event:
            kind, name = event.groups()
            if kind in {'namespace', 'section'}:
                scopes.append((kind, name))
            elif scopes:
                scopes.pop()
        namespace = '.'.join(name for kind, name in scopes if kind == 'namespace')
        for entry in by_line.get(line, []):
            name = entry['name']
            qualified = name[len('_root_.'):] if name.startswith('_root_.') else '.'.join(filter(None, [namespace, name]))
            result.append(dict(entry, qualified_name=qualified))
    return result


def _review_documents(entry):
    """Choose the retained source-facing discussion for this admission block."""
    match = re.fullmatch(r'KERNEL_CHECKED_BLOCK(\d+)(?:_RECOVERY)?', entry['status'])
    if not match:
        raise ValueError('Review unrecognized Machine-Native Reasoning map status')
    block = int(match[1])
    if block == 1:
        names = ['docs/ASSUMPTION_REVIEW.md']
    elif 2 <= block <= 15:
        names = ['docs/ASSUMPTION_REVIEW_BLOCK%02d.md' % block,
                 'docs/BLOCK%02d_PROOF_GUIDE.md' % block]
    else:
        names = {
            16: ['docs/CORE83_PROOF_GUIDE.md'],
            17: ['docs/CORE24_SOURCE_CORRESPONDENCE.md', 'docs/CORE24_PROOF_GUIDE.md'],
            18: ['docs/CORE25_CORRESPONDENCE_AUDIT.md', 'docs/CORE25_PROOF_GUIDE.md'],
            19: ['release/CLAUSE_CORRESPONDENCE.json', 'docs/CORE32_PROOF_GUIDE.md'],
        }.get(block)
        if names is None:
            raise ValueError('Review new Machine-Native Reasoning admission block')
    return [BASE + name for name in names]


def prepare_scope(reader, book):
    """Resolve the accepted 27-result map to exact HTML and Lean passages."""
    if 'mnr_scope' in book:
        return book['mnr_scope']
    def load(path, title=None):
        record = reader.add(path, title)
        if not record:
            raise ValueError('Missing receipt-bound Machine-Native Reasoning source: ' + path)
        return reader.site.read_source(record)
    for path, title in RESOURCES:
        load(path, title)
    entries = json.loads(load(MAP))
    modules = json.loads(load(MODULES))
    admission_raw = load(ADMISSION)
    admission = json.loads(admission_raw)
    publication = json.loads(load(READER_RECORD))
    counts = admission['counts']
    if (admission['status'] != 'PASS' or publication['status'] != 'PASS'
            or len(entries) != 27 or len({item['label'] for item in entries}) != 27
            or counts['selected_source_results'] != len(entries)
            or counts['selected_source_total'] != len(entries)
            or counts['pending_source_results'] != 0
            or publication['formal_selected_results'] != len(entries)
            or publication['formal_selected_total'] != len(entries)
            or publication['formal_admission_record_sha256'] != hashlib.sha256(admission_raw).hexdigest()):
        raise ValueError('Review Machine-Native Reasoning admission and publication binding')
    if len(modules) != len(set(modules)) or len(modules) != counts['production_modules_per_gate']:
        raise ValueError('Review Machine-Native Reasoning production module inventory')
    declarations = {}
    for module in modules:
        if not re.fullmatch(r'MachineTheory(?:\.[A-Za-z][A-Za-z0-9_]*)*', module):
            raise ValueError('Unexpected Machine-Native Reasoning module path')
        path = BASE + module.replace('.', '/') + '.lean'
        text = load(path).decode('utf-8-sig')
        for declaration in qualified_declarations(text):
            declarations.setdefault(declaration['qualified_name'], []).append(dict(
                declaration, module=module, path=path,
                url=reader.records[path]['url'] + '#L' + str(declaration['line'])))
    written = {}
    for spec, _, chapter in book['chapters']:
        for node in chapter.nodes:
            for label in node.get('labels', []):
                if label in written:
                    raise ValueError('Repeated Machine-Native Reasoning reading label: ' + label)
                written[label] = (spec, chapter, node)
    results = []
    original = load(ORIGINAL).decode('utf-8-sig').splitlines()
    for entry in entries:
        label = entry['label']
        if label not in written:
            raise ValueError('Missing written Machine-Native Reasoning result: ' + label)
        spec, chapter, node = written[label]
        if (node['kind'] != entry['kind'] or node['number'] != entry['number']
                or node['title'] != entry['title']):
            raise ValueError('Machine-Native Reasoning statement identity changed: ' + label)
        proof_id = getattr(chapter, 'proof_pairs', {}).get(node['id'])
        proofs = [p for p in chapter.nodes if p['id'] == proof_id and p['kind'] == 'proof']
        if len(proofs) != 1:
            raise ValueError('Missing paired Machine-Native Reasoning written proof: ' + label)
        first, last = entry['source_lines']
        if ('\\label{' + label + '}') not in '\n'.join(original[first-1:last]):
            raise ValueError('Machine-Native Reasoning original source anchor changed: ' + label)
        endpoints = []
        for name in entry['lean_endpoints']:
            matches = declarations.get(name, [])
            if len(matches) != 1:
                raise ValueError('Expected one Machine-Native Reasoning Lean endpoint: ' + name)
            endpoints.append(dict(matches[0], name=name))
        review_paths = _review_documents(entry)
        for path in review_paths:
            load(path)
        anchor = label.replace(':', '-')
        scope_url = PAGE + '#' + anchor
        route = ('Recorded formal scope', scope_url)
        related = chapter.related_readings.setdefault(node['id'], [])
        if not any(target == scope_url for _, target in related):
            related.append(route)
        results.append(dict(entry, anchor=anchor, statement_url=spec['url']+'#'+node['id'],
            proof_url=spec['url']+'#'+proof_id, endpoints=endpoints, review_paths=review_paths,
            original_url=reader.records[ORIGINAL]['url']+'#L'+str(first)))
    formal = load(FORMAL_CORRESPONDENCE).decode('utf-8-sig')
    if not formal.startswith(r'\chapter{Formal correspondence}' + '\n'):
        raise ValueError('Review changed Machine-Native Reasoning formal chapter')
    scope = dict(results=results, admission=admission, publication=publication, formal_correspondence=formal,
                 module_count=len(modules), endpoint_count=sum(len(r['endpoints']) for r in results))
    book['mnr_scope'] = scope
    return scope


def publish_scope(reader, book):
    """Publish source navigation and retained assurance, without a new audit."""
    scope = prepare_scope(reader, book)
    site, escape = reader.site, html.escape
    config, admission, publication = book['config'], scope['admission'], scope['publication']
    counts = admission['counts']
    def link(label, target):
        return '<a href="'+escape(site.rel(target, PAGE), quote=True)+'">'+escape(label)+'</a>'
    def resource(label, path):
        return link(label, reader.records[path]['url'])
    body = '<p class="eyebrow">Machine-Native Reasoning · Recorded formal evidence</p>'
    body += '<h1>Selected results and their formal scope</h1>'
    body += '<p>The accepted release '+escape(admission['version'])+' records all 27 selected results of Reviewed Core v0.2, with no pending selected result. Each entry below connects the written statement, its full written proof, the source-facing discussion of assumptions, and the exact retained Lean declarations.</p>'
    body += '<p>'+resource('Accepted release record', ADMISSION)+' · '+resource('Source-to-Lean map', MAP)+' · '+link('All chapters', config['index'])+' · '+link('Find statements and proofs', 'read/'+WORK+'/statements.html')+'</p>'
    body += '<section id="formal-correspondence"><h2>Formal correspondence</h2>'
    body += '<p>'+resource('Read the original authored correspondence chapter', FORMAL_CORRESPONDENCE)+'</p>'
    # Preserve the full authored chapter, including its actual proof boundary.
    from readable_chapters import Chapter
    formal = Chapter('', book.get('macros', {}), check_refs=False)
    formal.url = PAGE
    formal.labels = book['chapters'][0][2].labels
    content = scope['formal_correspondence'].split('\n', 1)[1]
    for paragraph in re.split(r'\n\s*\n', content):
        if paragraph.strip():
            body += '<p>'+formal.inline(paragraph.strip())+'</p>'
    body += '</section>'
    body += '<h2>What the accepted record covers</h2>'
    body += '<p>The two recorded cold gates each checked '+str(counts['production_modules_per_gate'])+' production modules, '+str(counts['kernel_replays_per_gate'])+' substantive replays through the same Lean kernel, '+str(counts['controls_per_gate'])+' rejection controls, and '+format(counts['axiom_audited_declarations'], ',')+' transitive axiom records. The actual axiom union is <code>'+escape(', '.join(admission['actual_axiom_union']))+'</code>. These are retained execution receipts; this HTML edition performs no new Lean execution or mathematical review.</p>'
    body += '<p>'+resource('Read the verification report and trusted-base limits', BASE+'release/REPORT.md')+' · '+resource('Read the accepted progress ledger', BASE+'release/ACCEPTED_PROGRESS_LEDGER.md')+'</p>'
    body += '<h2>Keep the editions separate</h2><ul>'
    body += '<li><strong>Reviewed Mathematical Core:</strong> the '+str(publication['pages'])+'-page reader presented here, with 27 selected results and their written proofs. '+resource('Reader publication record', READER_RECORD)+'.</li>'
    body += '<li><strong>Wider reviewed continuation:</strong> a separate 74-page working edition retaining an older 23/27 map. '+link('Open its work page', 'collection/works/research-machine-native-reasoning-wider.html')+'.</li>'
    body += '<li><strong>Expanded monograph:</strong> the accepted release records the later 1,155-page edition as unrecovered. Its publication and coverage remain a separate task. '+resource('Read the source recovery boundary', BASE+'release/BOOK_RECOVERY.md')+'.</li></ul>'
    body += '<p>The formal counterparts apply to their declared mathematical contracts. They do not establish learned representations, empirical performance, a deployed system, or external permission to act. A source-map entry alone is not an acceptance receipt.</p>'
    body += '<h2>27 selected results</h2>'
    body += '<p>Numbers follow the authored core, including gaps occupied by counterexamples. Original source-page and line references in the map belong to <code>source/core_v0.2.tex</code>; the HTML statement links open the refreshed reader. Declaration links resolve namespace-qualified names in retained source bytes and are navigation aids.</p>'
    body += '<ol class="scope-result-list">'
    for entry in scope['results']:
        body += '<li><a href="#'+escape(entry['anchor'], quote=True)+'">'+escape(entry['number']+' — '+entry['title'])+'</a></li>'
    body += '</ol>'
    for entry in scope['results']:
        label = entry['kind'].capitalize()+' '+entry['number']
        body += '<section id="'+escape(entry['anchor'],quote=True)+'" class="recorded-result-scope"><h3>'+escape(label+': '+entry['title'])+'</h3>'
        body += '<p>'+link('Written statement', entry['statement_url'])+' · '+link('Written proof', entry['proof_url'])+' · '+link('Unchanged source statement', entry['original_url'])+'</p>'
        body += '<p>Source label <code>'+escape(entry['label'])+'</code>. Read the domains, quantifiers, and required hypotheses in the statement and the retained formal interfaces.</p>'
        for key in ('formalization_note', 'admission_boundary', 'assurance_note'):
            if entry.get(key):
                body += '<p><strong>Recorded map qualification.</strong> '+escape(entry[key])+'</p>'
        body += '<p>'+ ' · '.join(resource('Assumptions and source correspondence' if i == 0 else 'Proof guide', path)
                                  for i,path in enumerate(entry['review_paths']))+'</p>'
        body += '<details><summary>Formal declarations ('+str(len(entry['endpoints']))+')</summary><ul>'
        for endpoint in entry['endpoints']:
            body += '<li>'+link(endpoint['name'], endpoint['url'])+' <small>('+escape(endpoint['module'])+', line '+str(endpoint['line'])+')</small></li>'
        body += '</ul></details></section>'
    site.page(PAGE, 'Machine-Native Reasoning selected results and formal scope', body)
    site.search.append(dict(title='Machine-Native Reasoning / Selected results and formal scope',
        group='Collection', kind='Guides', work_ids=[WORK], url=PAGE,
        text='27 selected results accepted formal scope assumptions Lean written statements proofs '+
             ' '.join(entry['number']+' '+entry['title']+' '+entry['label'] for entry in scope['results'])))
    return scope


# Short aliases ease integration with reading modules that use prepare/publish.
prepare = prepare_scope
publish = publish_scope
prepare_scopes = prepare_scope
publish_scopes = publish_scope
