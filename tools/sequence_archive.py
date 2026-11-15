"""Publish the recovered KOM records without changing the KSEQ catalogue."""
import csv
import hashlib
import io
import json
from collections import Counter
from html import escape as e
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/sequence-archive'
ARCHIVE_SHA256 = '15c3511fcba9d27547da59cc0440dc6b79b9945ab0fd0b791cdb9167a9118d40'
LABELS = {'known-OEIS': 'Known OEIS reference', 'known-family': 'Known family',
          'classical transform candidate': 'Classical transform / diagnostic', 'exploratory': 'Exploratory · novelty unassessed'}


def records(atlas=()):
    raw = json.loads((SOURCE/'candidate_registry.json').read_bytes())
    result = []
    for record in raw:
        values = list(map(str, record['terms']))
        overlap = []
        for entry in atlas:
            count = min(len(values), len(entry['terms']))
            if record['offset'] == entry['offset'] and count >= 9 and values[:count] == entry['terms'][:count]:
                overlap.append(dict(id=entry['id'], title=entry['title'], count=count))
        result.append(dict(id=record['code'], title=record['name'], kind=record['family'],
            formula=record['definition'], recurrence=record['note'], tags=[record['family'], record['classification']],
            status=LABELS[record['classification']], classification=record['classification'],
            explanation=record['research_source'], source_note=record['research_source'],
            oeis=record['existing_oeis_id'] or None, oeis_evidence=record['oeis_evidence'],
            priority=record['priority'], offset=record['offset'], index_symbol='j' if record['code']=='KOM084' else 'n', terms=values, overlap=overlap))
    return result


def bfile(entry):
    return '# Candidate '+entry['id']+', NOT an allocated OEIS A-number.\n# '+entry['title']+'\n'+''.join(f'{entry["offset"]+i} {v}\n' for i,v in enumerate(entry['terms']))+'\n'


def facts(entry):
    start=entry['offset']; end=start+len(entry['terms'])-1
    return '<dl class="sar-facts">'+''.join('<div><dt>'+key+'</dt><dd>'+e(value)+'</dd></div>' for key,value in [
        ('Internal ID',entry['id']),('Family',entry['kind']),('Review status',entry['status']),
        ('First index',str(start)),('Stored range',f'{start}–{end}'),('Exact terms',str(len(entry['terms'])))])+'</dl>'


def build(site, atlas):
    entries=records(atlas)
    data=dict(schema=1, archive_sha256=ARCHIVE_SHA256, entries=entries,
        scope='Recovered research records. Exact finite terms; no claim of novelty, infinite identity or new OEIS allocation.')
    site.write('assets/sequence-archive-data.json',json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    manifest=json.loads((SOURCE/'BFILE_SHA256.json').read_bytes())
    for entry in entries:
        if hashlib.sha256(bfile(entry).encode()).hexdigest()!=manifest[entry['id']+'_candidate_bfile.txt']:
            raise ValueError('Archive b-file identity failed: '+entry['id'])
    assets=['sequence-archive.css','sequence-archive.js','sequence-archive-core.mjs','sequence-archive-plot.mjs','sequence-plot-options.mjs','sequence-plot-options.css']
    versions={}
    version=lambda name:versions.get(name) or hashlib.sha256((site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
    for name in ['sequence-plot-options.mjs','sequence-plot-options.css','sequence-archive-core.mjs','sequence-archive-plot.mjs','sequence-archive.js','sequence-archive.css']:
        content=(site.root/'website/assets'/name).read_text(encoding='utf-8')
        if name.endswith(('.js','.mjs')):
            for dependency in assets+['sequence-atlas-core.mjs','sequence-atlas-search.mjs']:
                content=content.replace("'./"+dependency+"'","'./"+dependency+'?v='+version(dependency)+"'")
        site.write('assets/'+name,content)
        versions[name]=hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]
    def wrap(body, prefix=''):
        return '<link rel="stylesheet" href="'+prefix+'assets/sequence-archive.css?v='+version(assets[0])+'"><link rel="stylesheet" href="'+prefix+'assets/sequence-plot-options.css?v='+version('sequence-plot-options.css')+'"><div class="sar" data-archive>'+body+'</div><script type="module" src="'+prefix+'assets/sequence-archive.js?v='+version(assets[1])+'"></script>'
    out=io.StringIO(newline=''); writer=csv.writer(out);writer.writerow(['id','name','family','classification','offset','count','definition','oeis_reference','entry_url'])
    for x in entries:writer.writerow([x['id'],x['title'],x['kind'],x['classification'],x['offset'],len(x['terms']),x['formula'],x['oeis'] or '', 'sequence-archive/'+x['id']+'.html'])
    site.write('assets/sequence-archive-index.csv',out.getvalue())
    target=site.output/'assets/sequence-archive-sources.zip';target.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(target,'w',ZIP_DEFLATED) as bundle:
        for path in sorted(SOURCE.iterdir()):
            if path.is_file():
                info=ZipInfo(path.name,date_time=(2026,11,15,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
                bundle.writestr(info,path.read_bytes())
    families=Counter(x['kind'] for x in entries)
    options='<option value="">All families</option>'+''.join('<option>'+e(name)+'</option>' for name in sorted(families))
    reviews='<option value="">All review stages</option>'+''.join('<option value="'+key+'">'+e(value)+'</option>' for key,value in LABELS.items())
    cards=''.join('<article class="sar-card" data-record="'+x['id']+'"><p class="sar-kicker">'+x['id']+' / '+e(x['kind'])+'</p><h2><a href="sequence-archive/'+x['id']+'.html">'+e(x['title'])+'</a></h2><p class="sar-status">'+e(x['status'])+'</p><p class="sar-formula">'+e(x['formula'])+'</p><p class="sar-preview">n='+str(x['offset'])+': '+e(', '.join(x['terms'][:8]))+'…</p><p>'+str(len(x['terms']))+' stored terms · first index '+str(x['offset'])+'</p><p class="sar-match" hidden></p><a href="sequence-archive/'+x['id']+'.html#plot">Plot and inspect →</a></article>' for x in entries)
    header='<header class="sar-header"><p class="sar-kicker">Sequence atlas / Recovered collection</p><h1>Research sequence library</h1><p class="sar-lede">Follow an integer sequence from its definition to its exact values. Explore the recovered Komorebi collection, with original indices and clear review status.</p><div class="sar-stats"><span><strong>90</strong> records</span><span><strong>18</strong> families</span><span><strong>5,487</strong> exact terms</span></div><nav aria-label="Collection links"><a href="sequences.html#find">Curated atlas</a><a href="#records">Browse records</a><a href="#provenance">Sources and downloads</a></nav></header>'
    search='''<section class="sar-search" id="records"><h2>Find a research record</h2><form id="sar-search" role="search" aria-label="Search recovered sequences" hidden><label for="sar-query">Name, formula, ID, or exact terms</label><div class="sar-query"><input id="sar-query" type="search" maxlength="20000" placeholder="Try KOM085, name:Collatz, or 1, ?, 251" aria-describedby="sar-help sar-error"><button type="submit">Search</button><button id="sar-clear" type="button">Clear</button></div><div class="sar-controls"><label for="sar-family">Family<select id="sar-family">'''+options+'''</select></label><label for="sar-review">Review stage<select id="sar-review">'''+reviews+'''</select></label><label for="sar-sort">Order<select id="sar-sort"><option value="id">Record ID</option><option value="name">Name A–Z</option></select></label><label for="sar-match">Match terms<select id="sar-match"><option value="any">Anywhere in stored values</option><option value="start">At the first stored index</option></select></label></div><button id="sar-share" type="button">Copy search link</button><label id="sar-share-fallback" for="sar-share-value" hidden>Search link<input id="sar-share-value" readonly></label><p id="sar-error" role="alert" hidden></p></form><p id="sar-help">Combine words, quote a phrase, use | for alternatives or -word to exclude. Fields: id:, name:, formula:, tag:, kind:, oeis:, status:, terms:. Use ? for one unknown integer. Term results report the record's actual indices.</p><p id="sar-count" role="status" aria-live="polite">All 90 records are available below, including without JavaScript.</p><p id="sar-empty" hidden>No records match. Try fewer words or another review stage.</p></section>'''
    provenance='<section id="provenance" class="sar-provenance"><h2>Sources, review, and reuse</h2><p>Recovered from <strong>Komorebi_OEIS_Research_Expanded_v2_2026-11-15.zip</strong>. The 62 exploratory records are research constructions whose novelty remains unassessed. The remaining records are classical references, known families, or diagnostic transforms. KOM IDs are internal identifiers.</p><p>Terms were reproduced from the preserved exact Python generator and checked against the recovered registry and all 90 b-file checksums. Source notes retain their original attribution and limitations. OEIS references are archive annotations; no fresh full-corpus comparison is claimed.</p><p><a download href="assets/sequence-archive-data.json">Exact catalogue JSON (integer strings)</a> · <a download href="assets/sequence-archive-index.csv">Searchable index CSV</a> · <a download href="assets/sequence-archive-sources.zip">Reproduction source bundle</a> · <a href="https://github.com/KomorebiP/Operation-KOMOREBI/tree/main/research/sequence-archive">Source history and provenance</a></p><details><summary>Archive receipt</summary><p>SHA-256: <code>'+ARCHIVE_SHA256+'</code>. The source bundle is the sequence subset, not the complete historical research ZIP.</p></details></section>'
    site.page('sequence-archive.html','Research sequence library',wrap(header+search+'<div id="sar-records" class="sar-grid">'+cards+'</div>'+provenance))
    site.search.append(dict(title='Research sequence library',group='Collection',kind='Examples',work_ids=[],url='sequence-archive.html',text='90 recovered integer sequence records; exact definitions, offsets, plotting, modular views and review stages.'))
    for entry in entries:
        identifier=entry['id']; start=entry['offset'];last=start+len(entry['terms'])-1
        site.write('sequence-archive/'+identifier+'.json',json.dumps(entry,ensure_ascii=False,indent=2)+'\n')
        site.write('sequence-archive/'+identifier+'.txt',bfile(entry))
        symbol=entry['index_symbol']
        site.write('sequence-archive/'+identifier+'.csv',symbol+',a('+symbol+')\n'+''.join(str(start+i)+','+v+'\n' for i,v in enumerate(entry['terms'])))
        triangle=identifier=='KOM084'
        index_note=("This record flattens the coefficient triangle of P_n(s) by rows. The stored index j=n(n+1)/2+k selects coefficient [s^k]P_n(s), with 0≤k≤n. It is not the polynomial row number. The table also shows (n,k)." if triangle else f'The first stored index is {start}; the first term is a({start})={entry["terms"][0]}. The offset describes an index, not a value. The recovered data stops at index {last}; the plot never extrapolates beyond it.')
        rows=[]
        for i,value in enumerate(entry['terms']):
            flat=start+i
            extra=''
            if triangle:
                n=0
                while (n+1)*(n+2)//2<=flat:n+=1
                extra='<td>'+str(n)+'</td><td>'+str(flat-n*(n+1)//2)+'</td>'
            rows.append('<tr id="n-'+str(flat)+'"><th scope="row">'+str(flat)+'</th>'+extra+'<td>'+value+'</td></tr>')
        overlap=''.join('<li><a href="../sequences/'+x['id']+'.html">'+e(x['title'])+' · '+x['id']+'</a>: '+str(x['count'])+' stored terms agree at the same indices. This finite comparison does not prove infinite identity.</li>' for x in entry['overlap'])
        refs=('<p><a href="https://oeis.org/'+entry['oeis']+'">OEIS '+entry['oeis']+'</a> · '+e(entry['oeis_evidence'])+'</p>' if entry['oeis'] else '<p>'+e(entry['oeis_evidence'])+'</p>')
        plot='''<section id="plot" data-archive-id="'''+identifier+'''"><h2>Plot and inspect</h2><p>Plot the recorded values, their least nonnegative residues, or consecutive residue pairs. Differences use the previous stored term; partial sums begin at the record's first index. Log coordinates approximate signed log10(1+|value|); the values and modular arithmetic stay exact.</p><div id="sar-explorer" hidden><div id="sar-presets" class="sp-preset-bar" role="group" aria-label="Plot presets"></div><p>Presets keep the current window. Lines connect discrete samples; they do not add interpolated data.</p><form id="sar-plot-form" novalidate><div class="sar-controls"><label for="sar-view">View<select id="sar-view"><option value="mod">Residues modulo m</option><option value="raw">Original values</option><option value="difference">First differences</option><option value="sum">Partial sums</option><option value="pairs">Consecutive residue pairs</option></select></label><label for="sar-scale">Scale for integer values<select id="sar-scale"><option value="signed-log">Signed logarithm</option><option value="linear">Linear</option></select></label><label for="sar-start">First index<input id="sar-start" type="number" min="'''+str(start)+'''" max="'''+str(last)+'''" value="'''+str(start)+'''" step="1"></label><label for="sar-size">Index positions<input id="sar-size" type="number" min="1" max="1000" value="'''+str(min(32,len(entry['terms'])))+'''" step="1"></label><label for="sar-mod">Modulus m<input id="sar-mod" type="number" min="2" max="1000000" value="7" step="1"></label></div><button type="submit">Update plot</button><button type="button" id="sar-export">Export this window CSV</button><button type="button" id="sar-view-link">Copy plot link</button><label id="sar-plot-fallback" for="sar-plot-link" hidden>Plot link<input id="sar-plot-link" readonly></label><p id="sar-plot-error" role="alert" hidden></p></form><div id="sar-plot-options"><label for="sar-marks">Marks<select id="sar-marks"><option value="points">Points</option><option value="line">Connected points</option><option value="stems">Stems and points</option></select></label><label for="sar-color">Color points<select id="sar-color"><option value="single">One color</option><option value="value">By displayed value mod m</option><option value="index">By index mod m</option></select></label></div><div class="sp-window-bar" role="group" aria-label="Plot window"><button id="sar-previous" type="button">Previous window</button><button id="sar-next" type="button">Next window</button><button id="sar-zoom-in" type="button">Zoom in</button><button id="sar-zoom-out" type="button">Zoom out</button><button id="sar-all" type="button">Fit stored data</button><button id="sar-svg" type="button">Export SVG</button><button id="sar-png" type="button">Export PNG (2x)</button></div><p id="sar-window" role="status" aria-live="polite"></p><div id="sar-plot" class="sar-plot"></div><p id="sar-point" role="status">Select or focus a point to inspect its exact value. Use Left/Right within the plot to move between points.</p><label for="sar-inspect">Inspect stored index<input id="sar-inspect" type="number" min="'''+str(start)+'''" max="'''+str(last)+'''" value="'''+str(start)+'''" step="1"></label><p id="sar-exact" class="sar-exact" aria-live="polite"></p><details><summary>Exact values in this plot</summary><div class="sar-scroll" tabindex="0" role="region" aria-label="Exact plotted values"><table><thead><tr><th scope="col">Index</th><th scope="col">a(n)</th><th scope="col">Plotted exact value</th><th scope="col">Following residue</th></tr></thead><tbody id="sar-window-values"></tbody></table></div></details></div><p id="sar-static-note">The complete exact table and downloads are available below. Enable JavaScript for interactive plots.</p></section>'''
        plot=plot.replace('<th scope="col">a(n)</th>','<th scope="col">a('+symbol+')</th>')
        body='<nav aria-label="Breadcrumb"><a href="../sequences.html">Sequence atlas</a> / <a href="../sequence-archive.html#records">Research library</a> / '+identifier+'</nav><header class="sar-header"><p class="sar-kicker">'+identifier+' / Recovered record</p><h1>'+e(entry['title'])+'</h1><p class="sar-status">'+e(entry['status'])+'</p>'+facts(entry)+'<nav aria-label="Entry sections"><a href="#definition">Definition and indexing</a><a href="#plot">Plot and inspect</a><a href="#exact-data">Exact data</a><a href="#sources">Sources</a></nav></header><section id="definition"><h2>Definition and indexing</h2><p class="sar-formula">'+e(entry['formula'])+'</p><p>'+e(index_note)+'</p>'+(('<p>'+e(entry['recurrence'])+'</p>') if entry['recurrence'] else '')+'</section>'+plot+'<section id="exact-data"><h2>Exact data</h2><p><a download href="'+identifier+'.csv">Download CSV</a> · <a download href="'+identifier+'.txt">Download indexed text</a> · <a download href="'+identifier+'.json">Download entry JSON</a> · <a download href="../assets/sequence-archive-sources.zip">Python generator and source records</a></p><div class="sar-scroll" tabindex="0" role="region" aria-label="Complete exact terms"><table><caption>Stored indices '+str(start)+'–'+str(last)+'</caption><thead><tr><th scope="col">'+('Flat index j' if triangle else 'n')+'</th>'+('<th scope="col">Row n</th><th scope="col">Column k</th>' if triangle else '')+'<th scope="col">a('+symbol+')</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></section><section id="sources"><h2>Sources and review</h2><p>'+e(entry['source_note'])+'</p>'+refs+'<p>KOM identifiers are local archive labels. These exact finite data do not establish novelty, a global theorem, or physical circuit realization.</p>'+('<h3>Overlapping atlas data</h3><ul>'+overlap+'</ul>' if overlap else '')+'<p>To reproduce this record, extract the source bundle and run the preserved generator with <code>python reproduce.py --output regenerated</code>. Read its provenance and review queue before using a research claim.</p></section>'
        site.page('sequence-archive/'+identifier+'.html',entry['title']+' · '+identifier,wrap(body,'../'))
        site.search.append(dict(title=entry['title']+' · '+identifier,group='Collection',kind='Examples',work_ids=[],url='sequence-archive/'+identifier+'.html',text=entry['formula']+' '+entry['status']+' '+entry['kind']+' '+', '.join(entry['terms'][:8])))
    return dict(entries=len(entries),terms=sum(len(x['terms']) for x in entries),families=len(families))
