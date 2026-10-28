"""Index explicit manuscript statements without inferring proof or Lean coverage.

Only literal TeX inputs and named environments are read. TeX is never executed.
Paper I keeps its separately transcribed correspondence records.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re

KINDS = ('theorem', 'lemma', 'proposition', 'corollary', 'definition', 'boundary',
         'conjecture', 'statement', 'standardfact', 'classicalinput', 'classical',
         'certificate', 'numericalcertificate', 'construction')
ENV = re.compile(r'\\begin\{('+'|'.join(KINDS)+r')\}')
ROMANS = 'i ii iii iv v vi vii viii ix x xi xii'.split()
PAPERS = ['paper-'+n for n in ROMANS]
SCOPE = ('Indexed from the written manuscript. A nearby proof block is a reading location, '
         'not a correctness assessment. Lean correspondence for individual claims has not been transcribed '
         'for this index. Consult the paper’s formal guide and evidence for its recorded scope.')


def clean_tex(text):
    """Mask comments and literal examples while preserving source offsets."""
    mask = lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0])
    text = re.sub(r'(?<!\\)%[^\n]*', mask, text)
    return re.sub(r'\\begin\{(verbatim|Verbatim|lstlisting|minted)\}.*?\\end\{\1\}',
                  mask, text, flags=re.S)


def plain_tex(text):
    text = re.sub(r'\\(?:label|index)\{[^{}]*\}', '', text)
    text = re.sub(r'\\(?:begin|end)\{[^{}]*\}', ' ', text)
    text = re.sub(r'\\(?:textbf|textit|emph|mathrm|mathbf|mathbb|mathcal|operatorname|text|textrm)\b', '', text)
    text = re.sub(r'\\([a-zA-Z]+)', r' \1 ', text)
    text = text.replace('~', ' ').replace('---', ' ').replace('--', ' ')
    return ' '.join(text.translate(str.maketrans('', '', '{}$\\')).split())


def optional_title(text, start):
    pos = start
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos == len(text) or text[pos] != '[':
        return '', start
    begin = pos + 1
    braces = 0
    pos += 1
    while pos < len(text):
        c = text[pos]
        if pos and text[pos-1] == '\\':
            pos += 1
            continue
        if c == '{': braces += 1
        elif c == '}': braces -= 1
        elif c == ']' and braces == 0:
            return text[begin:pos], pos + 1
        pos += 1
    raise ValueError('Unclosed statement title')


def statements(text, path, work, sha256):
    clean = clean_tex(text)
    result = []
    for match in ENV.finditer(clean):
        kind = match[1]
        title, start = optional_title(clean, match.end())
        end = clean.find('\\end{'+kind+'}', start)
        if end < 0:
            raise ValueError('Unclosed '+kind+' in '+path)
        body = clean[start:end]
        labels = re.findall(r'\\label\{([^{}]+)\}', body)
        line = clean.count('\n', 0, match.start()) + 1
        identity = labels[0] if labels else PurePosixPath(path).stem+'-L'+str(line)
        identifier = work+'-'+re.sub(r'[^a-zA-Z0-9_.-]+', '-', identity)
        tail_start = end + len('\\end{'+kind+'}')
        # Do not guess which claim a later proof belongs to.
        proof = re.match(r'\s*(?:\\label\{[^{}]*\}\s*)*\\begin\{proof\}', clean[tail_start:])
        proof_line = None
        if proof:
            at = tail_start + proof[0].rfind('\\begin{proof}')
            proof_line = clean.count('\n', 0, at) + 1
        result.append(dict(id=identifier, work_id=work,
                           title=plain_tex(title) or kind.capitalize()+': '+(labels[0] if labels else 'line '+str(line)),
                           kind=kind, status='written_statement', scope=SCOPE,
                           labels=labels, statement_path=path, statement_line=line,
                           proof_line=proof_line, source_sha256=sha256, lean=[],
                           search_text=plain_tex(body)))
    return result


def read_source(root, cache, path, entry):
    local = root/path
    raw = local.read_bytes() if local.is_file() else (cache/'blobs'/entry['git_blob_sha1']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry['sha256']:
        raise ValueError('Source receipt mismatch: '+path)
    return raw.decode('utf-8-sig')


def manuscript_sources(root, cache, entrypoint, owned):
    """Follow literal inputs in order, using the main document's working directory."""
    found = {}
    base = posixpath.dirname(entrypoint)
    def visit(path):
        if path in found:
            return
        text = read_source(root, cache, path, owned[path])
        found[path] = text
        for name in re.findall(r'\\(?:input|include)\s*\{([^{}]+)\}', clean_tex(text)):
            if '\\' in name or '#' in name:
                continue
            name = name if PurePosixPath(name).suffix else name+'.tex'
            candidates = [posixpath.normpath(posixpath.join(folder, name))
                          for folder in (base, posixpath.dirname(path))]
            target = next((p for p in candidates if p in owned), None)
            if target and target.endswith('.tex'):
                visit(target)
    visit(entrypoint)
    return found


def generate(root, cache):
    old = json.loads((root/'manifests/claim-navigation.json').read_bytes())
    first = [r for r in old['records'] if r.get('work_id', 'paper-i') == 'paper-i']
    first = [{**r, 'work_id':'paper-i'} for r in first]
    resources = json.loads((root/'manifests/browse-resources.json').read_bytes())['components']
    data = dict(schema=2, source_revision=old['source_revision'],
                scope='Reading locations for all 12 core papers. No new proof review or Lean execution.',
                sources=[s for s in old['sources'] if s['path'].startswith('papers/paper-i/')],
                works=[], records=first)
    for work in PAPERS:
        c = next(c for c in resources if c['id'] == work)
        receipt = json.loads((root/('manifests/source-imports/'+work+'.json')).read_bytes())
        owned = {c['destination']+'/'+f['path']:f for f in receipt['files']}
        entrypoint = next(r['path'] for r in c['resources'] if r['kind'] == 'text')
        if work == 'paper-ix':
            entrypoint = 'sources/main/Paper_IX_Traditional_Final.tex'
        entrypoint = c['destination']+'/'+entrypoint
        data['works'].append(dict(id=work, entrypoint=entrypoint,
                                  mode='correspondence' if work == 'paper-i' else 'manuscript'))
        if work == 'paper-i':
            continue
        sources = manuscript_sources(root, cache, entrypoint, owned)
        for path, text in sources.items():
            data['sources'].append(dict(path=path, git_blob_sha1=owned[path]['git_blob_sha1']))
            data['records'].extend(statements(text, path, work, owned[path]['sha256']))
    ids = set()
    for row in data['records']:
        # Repeated labels in retained appendices get a stable path suffix.
        if row['id'].lower() in ids:
            row['id'] += '-'+hashlib.sha256((row['statement_path']+':'+str(row['statement_line'])).encode()).hexdigest()[:8]
        assert row['id'].lower() not in ids
        ids.add(row['id'].lower())
    return data


def validate_claims(root, known_paths):
    data = json.loads((root/'manifests/claim-navigation.json').read_bytes())
    assert data['schema'] == 2
    assert [w['id'] for w in data['works']] == PAPERS
    sources = {}
    owners = {}
    for work in PAPERS:
        receipt = json.loads((root/('manifests/source-imports/'+work+'.json')).read_bytes())
        for f in receipt['files']:
            p = receipt['destination']+'/'+f['path']
            sources[p] = f
            owners[p] = work
    bound = set()
    for source in data['sources']:
        path = source['path']
        assert path in known_paths and source['git_blob_sha1'] == sources[path]['git_blob_sha1']
        bound.add(path)
    ids = set()
    counts = {p:0 for p in PAPERS}
    for row in data['records']:
        assert row['id'].lower() not in ids
        ids.add(row['id'].lower())
        path = row['statement_path']
        assert path in known_paths and owners[path] == row['work_id']
        assert sources[path]['sha256'] == row['source_sha256']
        assert type(row['statement_line']) is int and row['statement_line'] > 0
        assert row['proof_line'] is None or type(row['proof_line']) is int and row['proof_line'] > 0
        if row['work_id'] != 'paper-i':
            assert path in bound and row['status'] == 'written_statement' and row['lean'] == []
        counts[row['work_id']] += 1
        for d in row['lean']:
            if d['path']:
                assert d['path'] in known_paths and d['git_blob_sha1'] == sources[d['path']]['git_blob_sha1']
    assert all(counts.values())
    return data


def render_claim_index(site):
    import html
    e = html.escape
    records = site.claims['records']
    labels = {'standardfact':'Standard fact', 'classicalinput':'Classical input',
              'classical':'Classical input', 'numericalcertificate':'Numerical certificate'}
    name = lambda kind: labels.get(kind, kind.replace('_', ' ').capitalize())
    filter_kind = lambda kind: 'classical' if kind == 'classicalinput' else kind
    body = '<h1>Follow a written claim</h1><p>All 12 core papers are here. Find a statement, open its source passage and follow the available proof, Lean guide and evidence.</p>'
    body += '<p>Paper I retains its 108 correspondence records, including 69 labeled covered by that source. Papers II through XII index explicit statement blocks in their current manuscripts. These are reading locations, not new proof reviews or Lean coverage assessments.</p>'
    body += '<h2 id="core-papers">Choose a core paper</h2><nav class="paper-jumps" aria-label="Choose a core paper">'
    for work in site.claims['works']:
        wid = work['id']
        count = sum(r['work_id'] == wid for r in records)
        body += '<a data-claim-paper="'+wid+'" href="#'+wid+'">Paper '+wid[6:].upper()+' <span>('+str(count)+')</span></a>'
    body += '</nav><form id="claim-filters" class="filters"><label for="claim-query">Search titles, statement text, labels or Lean names</label><input id="claim-query" name="q" type="search" aria-describedby="claim-help"><p id="claim-help" class="status">Try “seed rank”, “automorphy” or a source label. Filters are saved in this page’s address so you can share the result.</p><label for="claim-paper">Paper</label><select id="claim-paper" name="paper"><option value="">All 12 papers</option>'
    body += ''.join('<option value="'+p+'">Paper '+p[6:].upper()+'</option>' for p in PAPERS)
    body += '</select><label for="claim-kind">Statement type</label><select id="claim-kind" name="kind"><option value="">All statement types</option>'
    body += ''.join('<option value="'+k+'">'+name(k)+'</option>' for k in sorted({filter_kind(r['kind']) for r in records}))
    body += '</select><button type="reset">Clear filters</button></form><p id="claim-count" role="status" aria-live="polite">'+str(len(records))+' records across 12 papers</p><p id="claim-empty" hidden>No matching statements. Try fewer words or clear the filters. You can also <a href="search.html">search the whole site</a>.</p><noscript><p>All records are shown below. Use the paper links above or your browser’s Find command.</p></noscript>'
    for work in site.claims['works']:
        wid = work['id']
        title = site.components[wid]['title']
        hub = 'collection/works/'+wid+'.html'
        rows = [r for r in records if r['work_id'] == wid]
        pdf = site.reader.primary_pdf(wid)
        guide = next((r for r in site.registry['components'] if r['id'] == wid))
        guide = next((site.reader.resolve(site.components[wid]['destination']+'/'+r['path'], 'claims.html')
                      for r in guide['resources'] if r['kind'] == 'formal_guide'), None)
        body += '<section class="claim-section" data-paper="'+wid+'" aria-labelledby="'+wid+'"><h2 id="'+wid+'" tabindex="-1">'+e(title)+'</h2><p>'+str(len(rows))+' '+('correspondence records' if work['mode']=='correspondence' else 'written statement records')+'.</p><nav class="document-routes" aria-label="Paper '+wid[6:].upper()+' reading routes">'
        routes = [('Read PDF',pdf['url']),('Paper overview',hub),('Lean guide',guide or hub+'#lean'),
                  ('Lean coverage',hub+'#lean'),('Code',hub+'#code'),('Evidence',hub+'#evidence'),
                  ('Worked examples',hub+'#worked-examples-for-this-work')]
        body += ''.join('<a href="'+url+'">'+label+'</a>' for label,url in routes)
        body += '</nav><p class="status">'+('The original record keeps its status and scope. A mapped module does not imply that every statement in this paper has been formalized.' if work['mode']=='correspondence' else 'Statement types are taken from the manuscript. Conjectures, definitions, classical inputs and certificates remain distinct. Lean mappings for individual claims are not assigned by this index.')+'</p>'
        for row in rows:
            identifier = row['id'].lower()
            statement = site.reader.resolve(row['statement_path'], 'claims.html', 'L'+str(row['statement_line']))
            proof = site.reader.resolve(row['statement_path'], 'claims.html', 'L'+str(row['proof_line'])) if row['proof_line'] else None
            assert statement
            search = ' '.join([row['id'], row['title'], row['kind'], row['status'], row['scope'], title,
                               'Paper '+str(PAPERS.index(wid)+1), ' '.join(row.get('labels', [])),
                               row.get('search_text',''), ' '.join(d['name'] for d in row['lean'])])
            site.search.append(dict(title=title.split(':')[0]+' / '+row['title'], group='Collection',
                                    kind='Claims', url='claims.html#'+identifier, text=search))
            body += '<article class="claim" id="'+identifier+'" data-paper="'+wid+'" data-kind="'+filter_kind(row['kind'])+'" data-search="'+e(search,quote=True)+'"><h3>'+e(row['title'])+'</h3><p class="status">'+e(name(row['kind']))+' · '+('Source status: '+e(row['status']) if wid=='paper-i' else 'Written statement')+'</p><p><a href="#'+identifier+'" aria-label="Permanent link to '+e(row['title'],quote=True)+'">Link to this record</a> · <code>'+e(row['id'])+'</code></p>'
            if wid == 'paper-i': body += '<p>'+e(row['scope'])+'</p>'
            if row.get('labels'): body += '<p class="status">Source labels: '+e(', '.join(row['labels']))+'</p>'
            body += '<p><a href="'+statement+'">Written statement</a>'+(' · <a href="'+proof+'">'+('Written proof' if wid=='paper-i' else 'Following proof block')+'</a>' if proof else ' · No separate proof block indexed')+'</p>'
            if row['lean']:
                body += '<details><summary>'+str(len(row['lean']))+' recorded Lean declarations</summary><ul>'
                for d in row['lean']:
                    url = site.reader.resolve(d['path'], 'claims.html') if d['path'] else None
                    label = '<code>'+e(d['name'])+'</code>'
                    body += '<li>'+('<a href="'+url+'">'+label+'</a>' if url else label+' (source location not recorded)')+'</li>'
                body += '</ul></details>'
            else:
                body += '<p class="status">'+('No declaration mapping recorded for this entry.' if wid=='paper-i' else 'Lean mapping for this statement has not been transcribed here.')+'</p>'
            body += '<p><a href="'+pdf['url']+'">Read paper</a> · <a href="'+hub+'#lean">Lean coverage</a> · <a href="'+hub+'#code">Code</a> · <a href="'+hub+'#evidence">Evidence</a> · <a href="#claim-filters">Back to filters</a></p></article>'
        body += '</section>'
    body += '<p><a href="collection/CLAIM_LINKS.html">Index scope and other works</a> · <a href="collection/GLOSSARY.html">Glossary</a> · <a href="search.html">Search the site</a></p>'
    site.page('claims.html', 'Follow a written claim', body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path = args.root/'manifests/claim-navigation.json'
    data = generate(args.root, args.source_cache)
    output = json.dumps(data, ensure_ascii=False, indent=2)+'\n'
    if args.check:
        if path.read_text(encoding='utf-8') != output:
            raise SystemExit('Claim navigation differs from the bound manuscript sources')
    else:
        path.write_text(output, encoding='utf-8', newline='\n')
    print(json.dumps({w['id']:sum(r['work_id']==w['id'] for r in data['records']) for w in data['works']}))


if __name__ == '__main__':
    main()
