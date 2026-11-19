"""Unified formula library and on-demand matching against retained OEIS exports."""
import csv
import hashlib
from html import escape as e
from urllib.parse import quote,urlencode
import io
import json
from pathlib import Path
import shutil
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
from sequence_formula_catalogue import expanded_catalogue, formula_variants, formula_block, REGISTRY_PATH
from sequence_archive import records, plot_section
from sequence_research_tables import cell_coordinates, triangle_section
from sequence_research_notes import entry_details, research_connections
from sequence_generalized import catalogue as generalized_catalogue, build_pages as generalized_pages, sections as generalized_sections


def source_degree(entry,n):
    if entry.get('linear_addition'):return n
    if entry.get('triangle'):
        row,_=cell_coordinates(entry,n);return row*entry['triangle']['degree_multiplier']
    if 'source_shift' in entry:return entry['N']*n+entry['source_shift']
    if entry['kind']=='logarithmic companion':return entry['N']*(n+1)-1
    if entry['kind'].startswith('Appell '):return n
    return entry['N']*n+(entry.get('j',0) if entry['kind']=='classical multisection' else 0)


CALCULATOR_PARAMETERS={
    'sparse':('p','q','r','u','v'),
    'jet':('d','lambda','c'),
    'hankel':('d','c'),
    'meixner':('s','twox'),
}
CALCULATOR_BOUNDS={'sparse':96,'jet':80,'hankel':12,'meixner':96}


def calculator_link(entry,path='sequence-library.html'):
    """Canonical exact calculator handoff from a source record.

    Parameters are recorded by the exact generator, not parsed from a title.
    Links contain no stored coefficients and leave the original record intact.
    """
    spec=entry.get('calculator')
    if not spec:return None
    mode=spec['mode']
    if mode not in CALCULATOR_PARAMETERS:raise ValueError('Unrecognized exact calculation mode')
    keys=CALCULATOR_PARAMETERS[mode]
    if set(spec)!={'mode',*keys}:raise ValueError('Incomplete exact calculator parameters: '+entry['id'])
    index=entry['offset']
    count=min(12,len(entry['terms']),CALCULATOR_BOUNDS[mode]-index+1)
    if count<1:raise ValueError('Exact calculator cannot represent the source index')
    values={'cf-version':'1','cf-mode':mode,'cf-start':str(index),'cf-count':str(count)}
    for key in keys:values['cf-'+key]=str(spec[key])
    return path+'?'+urlencode(values)+'#closed-calculator-panel'


def library_entries(atlas):
    groups=[('atlas',atlas,'sequences/'),('recovered',records(atlas),'sequence-archive/'),('formulas',expanded_catalogue(),'sequence-families/')]
    entries=[]
    for collection,values,prefix in groups:
        for original in values:
            entry=dict(original,collection=collection,url=prefix+original['id']+'.html')
            entry.setdefault('source','https://komorebip.github.io/Operation-KOMOREBI/'+entry['url']+'#definition')
            entry.setdefault('index_symbol','n');entry.setdefault('classification','family' if collection=='formulas' else 'reference')
            if entry['id']=='KOM084':entry['tags']=[*entry['tags'],'triangle']
            entry['formulas']=formula_variants(entry)
            if entry.get('calculator'):entry['calculator_url']=calculator_link(entry)
            entries.append(entry)
    return entries


def exact_record_receipt(entry):
    """Digest the indexed integer data, never the rounded plot coordinates."""
    payload=[entry['id'],entry['collection'],entry['offset'],
             entry.get('index_symbol','n'),entry['terms'],
             entry.get('source_degrees')]
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()


def matches_block(entry):
    if entry.get('closed_form_collection'):
        stated=('<p>The source identifies <a href="https://oeis.org/'+e(entry['oeis'])+'">'+e(entry['oeis'])+'</a>. '
                'That identification has not yet been rechecked against the pinned local bulk snapshot.</p>') if entry.get('source_claimed_oeis') and entry.get('oeis') else ''
        return ('<section id="oeis-matches"><h2>OEIS comparisons</h2>'+stated+
                '<p>Not yet compared with the pinned OEIS snapshot. No negative matching result, '
                'historical novelty, or distinctness is inferred from this entry.</p></section>')
    hits=entry.get('matches',[]);total=entry.get('match_count',len(hits))
    return '<section id="oeis-matches"><h2>OEIS comparisons</h2><p>These finite matches begin at local index '+str(entry['offset'])+'. Positions in the bulk export start at zero and do not represent OEIS mathematical offsets. A finite match does not prove that two infinite sequences are identical.</p>'+(
        '<ol>'+''.join('<li><a href="https://oeis.org/'+x['id']+'">'+x['id']+'</a> — '+e(x['name'])+'<br>'+str(x['matched_terms'])+' matching terms · OEIS excerpt position '+str(x['position'])+'</li>' for x in hits[:8])+'</ol><p>Showing '+str(min(8,len(hits)))+' of '+str(total)+' recorded matches. Up to 50 ranked matches are retained in the entry JSON.</p>' if hits else '<p>No contiguous match of eight terms was found in the recorded export. This does not establish novelty.</p>')+'<p>Reference names and terms: <a href="https://oeis.org/">The Online Encyclopedia of Integer Sequences</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Matching and presentation are adaptations.</p></section>'


def build(site,atlas):
    entries=library_entries(atlas)
    snapshot=json.loads((site.root/'manifests/sequence-library-oeis.json').read_text(encoding='utf-8'))
    # The historical OEIS manifest attests only the original records. New
    # closed-form windows have their own exact generator and independent checks.
    snapshot_entries=[x for x in entries if not x.get('closed_form_collection')]
    signature=hashlib.sha256(json.dumps([(x['id'],x['terms']) for x in snapshot_entries],separators=(',',':')).encode()).hexdigest()
    if signature!=snapshot['catalogue_terms_sha256']:raise ValueError('Regenerate the full-library OEIS comparison after term changes')
    # Use the same audited index map as each record's exact data table.
    # These are source degrees, not inferred from the flattened display index.
    for entry in entries:
        if entry['collection']=='formulas':
            entry['source_degrees']=[source_degree(entry,entry['offset']+i) for i in range(len(entry['terms']))]
    for entry in entries:
        entry['oeis_checked']=not bool(entry.get('closed_form_collection'))
        entry['record_sha256']=exact_record_receipt(entry)
        entry['matches']=snapshot['matches'].get(entry['id'],[]);entry['match_count']=snapshot['total_matches'].get(entry['id'],0)
        entry['oeis_snapshot']=dict(attribution=snapshot['attribution'],license=snapshot['license'],source_urls=snapshot['source_urls'],downloaded_at=snapshot['snapshot']['downloaded_at'],stripped_sha256=snapshot['stripped_sha256'],names_sha256=snapshot['names_sha256'],scope='Finite contiguous comparisons; export positions are not mathematical offsets and matches do not prove infinite identity.')
    source=site.root/'research/oeis-snapshot'
    target=site.output/'assets/oeis';target.mkdir(parents=True,exist_ok=True)
    for file in snapshot['snapshot']['files']:
        raw=(source/file['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=file['sha256']:raise ValueError('OEIS snapshot hash differs: '+file['file'])
        shutil.copyfile(source/file['file'],target/file['file'])
    site.write('assets/oeis/snapshot.json',json.dumps(snapshot['snapshot'],indent=2)+'\n')
    data=dict(schema=1,entries=entries,snapshot={key:value for key,value in snapshot.items() if key not in ('matches','total_matches')})
    site.write('assets/sequence-library-data.json',json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    site.write('assets/sequence-oeis-meta.json',json.dumps({'stripped_sha256':snapshot['stripped_sha256']},separators=(',',':'))+'\n')
    site.write('assets/sequence-formulas.json',json.dumps({x['id']:x['formulas'] for x in entries},ensure_ascii=False,separators=(',',':'))+'\n')
    out=io.StringIO(newline='');writer=csv.writer(out);writer.writerow(['id','title','collection','family','offset','stored_terms','representations','entry_url'])
    for x in entries:writer.writerow([x['id'],x['title'],x['collection'],x['kind'],x['offset'],len(x['terms']),len(x['formulas']),x['url']])
    site.write('assets/sequence-library-index.csv',out.getvalue())
    source_files=['tools/'+name+'.py' for name in ['sequence_formula_catalogue','sequence_closed_forms','sequence_closed_forms_extended','sequence_research_tables','sequence_linear_research','sequence_research_notes','sequence_generalized','sequence_archive_families','sequence_atlas','sequence_atlas_reference','sequence_atlas_reading','sequence_atlas_study','sequence_atlas_index']]+[REGISTRY_PATH,'manifests/sequence-generalized-sources.json','research/sequence-connections/IDENTITIES.md','research/sequence-connections/sources/komorebi-math-families.py','research/sequence-closed-forms/IDENTITIES.md','research/sequence-closed-forms/COLLECTION_II_ADDITIONS.md']
    with ZipFile(site.output/'assets/sequence-formula-source.zip','w',ZIP_DEFLATED) as bundle:
        for name in source_files:
            info=ZipInfo(name,date_time=(2026,11,15,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16;bundle.writestr(info,(site.root/name).read_text(encoding='utf-8').encode('utf-8'))
        info=ZipInfo('README.txt',date_time=(2026,11,15,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
        bundle.writestr(info,'Exact formula catalogue. Python 3.10+ standard library. Text sources use UTF-8/LF for portable reproduction.\nRun: python tools/sequence_formula_catalogue.py --id KFOR-S-catalan-03-01\nExport all records: python tools/sequence_formula_catalogue.py --output records.json\nScalar records store 24 terms beginning at their explicit offsets, except standard k-bonacci records, which store 48. Coefficient triangles store complete rows n=0..12, including zeros. Triangle j is a flat cell index. Its row and column are n and k. Parameter records are not claims of novelty or pairwise distinctness.\n')
    generalized=generalized_catalogue(entries)
    site.write('assets/sequence-generalized-data.json',json.dumps(generalized,ensure_ascii=False,separators=(',',':'))+'\n')
    scripts=['math-display.mjs','sequence-research-ui.mjs','sequence-reading-theme.mjs','sequence-oeis-core.mjs','sequence-family-core.mjs','sequence-transfer-core.mjs','sequence-math.mjs','sequence-graph-core.mjs','sequence-modular-core.mjs','sequence-discovery-core.mjs','sequence-notebook-core.mjs','sequence-research-worker.mjs','sequence-research-common.mjs','sequence-oeis-worker.mjs','sequence-oeis-client.mjs','sequence-comparison-chart.mjs','sequence-chart-labels.mjs','sequence-workbench-core.mjs','sequence-comparison-certificate.mjs','sequence-certificate-inspection.mjs','sequence-workbench.mjs','sequence-triangle-core.mjs','sequence-triangle.mjs','sequence-transfers.mjs','sequence-families-ui.mjs','sequence-connections-ui.mjs','sequence-identification-ui.mjs','sequence-modular-ui.mjs','sequence-notebooks-ui.mjs','sequence-library-membership.mjs','sequence-research-studio.mjs','sequence-library-search.mjs','sequence-inspection-links.mjs','sequence-closed-forms-core.mjs','sequence-closed-forms-ui.mjs','sequence-library.js']
    for name in scripts:
        content=(site.root/'website/assets'/name).read_text(encoding='utf-8')
        content=content.replace('__OEIS_TERMS_SHA256__',snapshot['stripped_sha256']).replace('__OEIS_NAMES_SHA256__',snapshot['names_sha256'])
        for dep in scripts+['sequence-atlas-search.mjs','sequence-archive-core.mjs','sequence-archive-plot.mjs','sequence-atlas-core.mjs','sequence-atlas-saved.mjs','sequence-plot-options.mjs','sequence-library-data.json','sequence-generalized-data.json','sequence-oeis-meta.json']:
            path=site.output/'assets'/dep
            if path.exists():content=content.replace("'./"+dep+"'","'./"+dep+'?v='+hashlib.sha256(path.read_bytes()).hexdigest()[:12]+"'")
        site.write('assets/'+name,content)
    site.write('assets/sequence-library.css',(site.root/'website/assets/sequence-library.css').read_text(encoding='utf-8'))
    site.write('assets/sequence-research.css',(site.root/'website/assets/sequence-research.css').read_text(encoding='utf-8'))
    site.write('assets/sequence-closed-forms.css',(site.root/'website/assets/sequence-closed-forms.css').read_text(encoding='utf-8'))
    def wrap(body,prefix='',entry=None,family=None,page_kind=None):
        attrs=' data-entry="'+e(entry['id'])+'.json"' if entry else (' data-family="'+e(family)+'"' if family else '')
        if page_kind:attrs+=' data-page="'+e(page_kind,quote=True)+'"'
        return ''.join('<link rel="stylesheet" href="'+prefix+'assets/'+name+'?v='+hashlib.sha256((site.output/'assets'/name).read_bytes()).hexdigest()[:12]+'">' for name in ['sequence-archive.css','sequence-plot-options.css','sequence-library.css','sequence-reading.css','sequence-research.css'])+'<div class="sar sl-library" data-library'+attrs+'>'+body+'</div><script type="module" src="'+prefix+'assets/sequence-library.js?v='+hashlib.sha256((site.output/'assets/sequence-library.js').read_bytes()).hexdigest()[:12]+'"></script>'
    site.write('assets/sequence-research-connections.json',json.dumps(research_connections(),ensure_ascii=False,separators=(',',':'))+'\n')
    generalized_pages(site,generalized,wrap)
    total=len(entries);representations=sum(len(x['formulas']) for x in entries)
    kinds=sorted({x['kind'] for x in entries});types=sorted({f['kind'] for x in entries for f in x['formulas']});statuses=sorted({x['status'] for x in entries})
    collections=[('', 'All records',total)]+[(key,label,sum(x['collection']==key for x in entries)) for key,label in [('formulas','Formula families'),('atlas','Curated sequences'),('recovered','Research archive')]]
    collection_buttons='<div class="sl-collections" role="group" aria-label="Search collections">'+''.join('<button type="button" data-collection="'+key+'" aria-pressed="'+('true' if not key else 'false')+'">'+label+' <span>'+f'{count:,}'+'</span></button>' for key,label,count in collections)+'</div>'
    def page_nav(active):
        pages=[('Search','sequence-library.html','search'),('Transfer','sequence-transfers.html#transfers','transfer'),('Compare','sequence-compare.html#comparison','compare'),('Research','sequence-research.html#research-families','research'),('OEIS','sequence-oeis.html#oeis','oeis')]
        return '<nav class="sl-page-tabs" aria-label="Sequence Library pages">'+''.join('<a href="'+url+'"'+(' aria-current="page"' if active==key else '')+'>'+label+'</a>' for label,url,key in pages)+'</nav>'
    def page_heading(title,description,active,anchor):
        return ('<a class="sl-skip" href="#'+anchor+'">Skip to '+e(title)+'</a>'
                '<header class="sl-section-head"><p class="sar-kicker">Komorebi / Sequence Library</p>'
                '<h1>'+e(title)+'</h1><p class="sl-section-lede">'+e(description)+'</p>'
                +page_nav(active)+'</header>')
    header=('<a class="sl-skip" href="#library-search">Skip to sequence search</a>'
            '<header class="sl-hero"><p class="sar-kicker">Komorebi / Sequence Library</p>'
            '<h1>Sequence Library</h1>'
            '<p class="sar-lede">Find exact sequences, calculate coefficients, and follow their derivations, relationships, and verification from one research workspace.</p>'
            '<p class="sl-figures"><strong>'+f'{total:,}'+'</strong> records · <strong>'+f'{representations:,}'+'</strong> representations · <strong>'+f'{snapshot["sequence_count"]:,}'+'</strong> OEIS references</p>'
            +page_nav('search')+'</header>')
    research_entries=[item for item in entries if 'research-derived' in item['tags']]
    research_count=len(research_entries)
    triangle_count=sum('triangle' in item['tags'] for item in entries)
    research_groups=[
        ('Secancy parameter polynomials',
         'Polynomial coefficients and their complete triangular tables.',
         [('Coefficient columns','secancy parameter column'),
          ('Complete coefficient triangles','secancy coefficient triangle')],
         ('Read an N=3 triangle','sequence-families/KFOR-TRI-P-03.html#triangle')),
        ('Euler-transfer theta',
         'Integer evaluations, polynomial columns and the complete theta triangle.',
         [('Integer specializations','Euler-transfer theta'),
          ('Polynomial coefficient columns','theta polynomial column'),
          ('Theta coefficient triangle','theta coefficient triangle')],
         ('Read the x=2 specialization','sequence-families/KFOR-H-02.html')),
        ('Block-Appell polynomials',
         'Complete polynomial tables and nonzero supported columns.',
         [('Coefficient triangles','block-Appell coefficient triangle'),
          ('Supported coefficient columns','block-Appell coefficient column')],
         ('Read an N=3 Appell triangle','sequence-families/KFOR-TRI-A-03-01.html#triangle')),
        ('Linear recurrences',
         'Weighted k-step coefficients and standard zero-seeded k-bonacci sequences.',
         [('Weighted k-step families','k-step reciprocal power'),
          ('Standard k-bonacci sequences','k-bonacci')],
         ('Read a weighted recurrence','sequence-families/KFOR-LR-03-02-01.html'))
    ]
    named_kinds={kind for _,_,kinds,_ in research_groups for _,kind in kinds}
    remaining_kinds=sorted({item['kind'] for item in research_entries if item['kind'] not in named_kinds})
    if remaining_kinds:
        research_groups.append(('Additional indexed families',
                                'Other research records retained in this library.',
                                [(kind,kind) for kind in remaining_kinds],None))
    def research_link(query,label):
        href='sequence-library.html?q='+quote(query,safe='')+'#library-search'
        return '<a href="'+e(href,quote=True)+'">'+e(label)+'</a>'
    family_cards=[]
    for title,description,category_pairs,example in research_groups:
        counts=[(label,kind,sum(item['kind']==kind for item in research_entries)) for label,kind in category_pairs]
        total_group=sum(count for _,_,count in counts)
        if not total_group:continue
        links=''.join('<li>'+research_link('kind:"'+kind+'"',label+' ('+str(count)+')')+'</li>' for label,kind,count in counts if count)
        example_link=('<p class="sl-research-example">Example: <a href="'+e(example[1],quote=True)+'">'+e(example[0])+'</a></p>') if example else ''
        family_cards.append('<article class="sl-research-group"><h3>'+e(title)+' <span>'+str(total_group)+' records</span></h3><p>'+e(description)+'</p><ul>'+links+'</ul>'+example_link+'</article>')
    research=('<section id="research-families" class="sl-optional-section"><h2>Research families</h2>'
              '<p class="sl-research-intro">'+str(research_count)+' indexed research records. '
              'Explore each family below or '+research_link('tag:research-derived','browse all research records')+'. '
              'Records retain their definitions, exact coefficients, source links and review status. '
              'An indexed family is not a claim of historical novelty.</p>'
              '<details class="sl-topic-disclosure"><summary>Explore research families by type</summary>'
              '<div class="sl-research-index">'+''.join(family_cards)+'</div>'
              '<p class="sl-research-scope">Some parameter choices produce the same integer sequence. '
              'The links search all matching records, not just the examples. '
              'Filtered search requires JavaScript. Without it, open the '
              '<a href="sequence-library/index.html">complete static sequence index</a>.</p>'
              '</details></section>')
    controls='''<section id="library-search"><h2>Find a sequence or formula</h2><p><a href="generalized-families/index.html">Generalized family definitions and source papers</a></p><form id="sl-search" role="search" hidden><div class="sl-scope-buttons sp-actions" role="group" aria-label="Search scope"><button type="button" data-scope="records" aria-pressed="true">Integer records</button><button type="button" data-scope="families" aria-pressed="false">Generalized families</button></div>'''+collection_buttons+'''<label id="sl-query-label" for="sl-query">Name, formula, identifier, or exact terms</label><div class="sl-query"><input id="sl-query" type="search" maxlength="20000" placeholder="Try hypergeometric, j:1 r:2, or 1, 1, 69" aria-describedby="sl-help sl-error"><button type="submit">Search</button><button id="sl-clear" type="button">Clear</button></div><details><summary>Filters and search options</summary><div class="sar-controls"><label for="sl-scope">Search scope<select id="sl-scope"><option value="records">Integer records</option><option value="families">Generalized families</option></select></label><label for="sl-collection">Collection<select id="sl-collection"><option value="">All collections</option><option value="formulas">Formula families</option><option value="atlas">Curated sequences</option><option value="recovered">Research archive</option></select></label><label for="sl-kind">Family<select id="sl-kind"><option value="">All families</option>'''+''.join('<option>'+e(k)+'</option>' for k in kinds)+'''</select></label><label for="sl-representation">Formula type<select id="sl-representation"><option value="">All representations</option>'''+''.join('<option>'+e(k)+'</option>' for k in types)+'''</select></label><label for="sl-status">Review status<select id="sl-status"><option value="">All review statuses</option>'''+''.join('<option>'+e(status)+'</option>' for status in statuses)+'''</select></label><label for="sl-match">Term matching<select id="sl-match"><option value="any">Anywhere in stored terms</option><option value="start">At the first stored index</option></select></label><label for="sl-sort">Order<select id="sl-sort"><option value="relevance">Best match</option><option value="name">Name</option><option value="id">Identifier</option></select></label><label for="sl-hits">OEIS comparisons<select id="sl-hits"><option value="">All records</option><option value="matched">Has an eight-term reference match</option><option value="unmatched">No recorded eight-term match</option></select></label></div></details><div class="sp-actions"><button id="sl-generalized" type="button">Browse generalized families</button><button id="sl-research" type="button" hidden>Browse research families</button><button id="sl-triangles" type="button" hidden>Browse coefficient triangles ('''+str(triangle_count)+''')</button><button id="sl-share" type="button">Copy search link</button><button id="sl-export" type="button">Export results CSV</button></div><label id="sl-link-wrap" hidden for="sl-link">Copy this search link<input id="sl-link" readonly></label><p id="sl-error" role="alert" hidden></p><p id="sl-action-status" role="status" aria-live="polite"></p><div id="sl-active-filters" class="sl-active-filters" aria-label="Active search filters"></div></form><p id="sl-family-summary" class="sl-family-summary" hidden></p><p id="sl-family-help" hidden>Search constructions by name, formula, family ID, or source. Try <code>Hankel</code>, <code>id:GF-SMITH-POLYNOMIALS</code>, or <code>paper:SF-VI</code>. Use the construction type and source filters to narrow the list. Open an integer record to inspect exact terms and offsets.</p><p id="sl-help">Search by name, identifier, formula or exact terms. See the optional syntax guide for filters and advanced operators.</p><details class="sl-search-guide"><summary>Search tips and field reference</summary>
<p>Search a name, record ID, formula, or comma-separated integer terms. Term matches keep the original stored index.</p>
<div class="sl-search-examples" aria-label="Search examples">
<div><strong>By name</strong><a href="sequence-library.html?q=theta#library-search"><code>theta</code></a></div>
<div><strong>By record ID</strong><a href="sequence-library.html?q=id%3AKFOR-P-03-02#library-search"><code>id:KFOR-P-03-02</code></a></div>
<div><strong>By exact terms</strong><a href="sequence-library.html?q=1%2C1%2C2%2C5%2C14#library-search"><code>1,1,2,5,14</code></a></div>
</div>
<h3>Combine search terms</h3>
<dl class="sl-search-rules">
<div><dt>Both (AND)</dt><dd><code>theta x:2</code></dd></div>
<div><dt>Either (OR)</dt><dd><code>theta | secancy</code></dd></div>
<div><dt>Exclude</dt><dd><code>theta -triangle</code></dd></div>
<div><dt>Exact phrase</dt><dd><code>name:"Euler-transfer theta"</code></dd></div>
<div><dt>Unknown integer</dt><dd><code>terms:1,?,2,3</code></dd></div>
</dl>
<h3>Search fields</h3>
<p><strong>Record details:</strong> <code>id:</code>, <code>name:</code>, <code>kind:</code>, <code>tag:</code>, <code>formula:</code>, <code>representation:</code>, <code>collection:</code> and <code>oeis:</code>.</p>
<p><strong>Parameters:</strong> <code>n:</code> (spacing N), <code>j:</code> (residue), <code>r:</code> (power), <code>x:</code> (specialization), <code>k:</code> (polynomial column), <code>order:</code> (recurrence order) and <code>weight:</code>.</p>
<p><strong>Relationships:</strong> <code>parent:</code>, <code>family:</code>, <code>paper:</code> (for example <code>paper:SF-VI</code>) and <code>terms:</code> (exact integer patterns).</p>
<p>Words separated by spaces must all match unless joined with <code>|</code>. Quoted phrases stay together. A question mark represents one unknown integer in a term pattern. All stored formula variants are searchable.</p>
</details><p id="sl-count" role="status" aria-live="polite">Browse the <a href="sequence-library/index.html">complete static index</a> without JavaScript.</p><div id="sl-result-layout" class="sl-layout-controls" role="group" aria-label="Sequence result layout" hidden><span>Results view</span><button type="button" data-layout="compact" aria-pressed="true">Compact rows</button><button type="button" data-layout="cards" aria-pressed="false">Cards</button></div><div id="sl-empty" class="sl-empty" hidden><h3>No matches in this view</h3><p>Try a shorter query or remove a filter. Clearing the search keeps your current view.</p><button id="sl-reset" type="button">Clear search and filters</button></div><ol id="sl-results" class="sl-results" tabindex="-1" aria-label="Sequence search results"></ol><div id="sl-pages" class="sp-actions" hidden><button id="sl-previous" type="button">Previous results</button><span id="sl-page"></span><button id="sl-next" type="button">Next results</button></div></section>'''
    mb=sum(x['bytes'] for x in snapshot['snapshot']['files'])/1048576
    reference='''<section id="oeis" class="sl-reference sl-optional-section"><h2>Compare with OEIS</h2><details class="sl-topic-disclosure"><summary>Open OEIS lookup and reference downloads</summary><p class="sar-kicker">Reference matching</p><p>Search an OEIS A-number, a name or at least three exact integer terms. Use ? for one unknown integer. This local snapshot uses the official names and terms exports from '''+e(snapshot['snapshot']['downloaded_at'][:10])+'''. Export positions are not mathematical offsets.</p><form id="sl-oeis-form" hidden><label for="sl-oeis-query">OEIS ID, name, or integer pattern</label><div class="sl-query"><input id="sl-oeis-query" maxlength="20000" placeholder="A000108 or 1,1,2,5,14,42,132,429"><button id="sl-oeis-search" type="submit">Search OEIS data</button><button id="sl-oeis-cancel" type="button" disabled>Cancel</button></div></form><details class="sl-oeis-info"><summary>Reference size and search limits</summary><p>The first search downloads about '''+f'{mb:.1f}'+''' MiB of reference data. Searches run in your browser, and queries are not sent to OEIS. Up to 50 results are displayed, with the total reported. The bulk files contain terms and names. Open an OEIS entry for its full formulas, comments and index offset.</p></details><p id="sl-oeis-status" role="status" aria-live="polite">Ready to search OEIS reference data.</p><ol id="sl-oeis-results"></ol><details class="sl-oeis-info"><summary>Source files and attribution</summary><p>Downloads: <a download href="assets/oeis/stripped.gz">OEIS terms</a> · <a download href="assets/oeis/names.gz">OEIS names</a> · <a href="assets/oeis/snapshot.json">Dates, sizes, and SHA-256 hashes</a></p><p>OEIS data © The OEIS Foundation Inc., <a href="https://oeis.org/">The Online Encyclopedia of Integer Sequences</a>, available under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Reference matching and presentation are adaptations. <a href="https://oeis.org/wiki/Download">Official download guidance</a>.</p></details></details></section>'''
    transfers=r'''<section id="transfers" class="sr-transfer-reading">
 <p class="sar-kicker">Exact coefficient transport</p>
 <h2>Transfer between sequences</h2>
 <p>Compare two stored scalar sequences through an exact forward and inverse convolution. Every coefficient is checked over the selected finite window. The calculation does not imply that the sequences share a recurrence.</p>
 <div id="sr-transfer-tool"></div>
 <p class="sr-transfer-static">Enable JavaScript to calculate and export other transfers. The worked example and sources remain available without it.</p>
 <details class="sr-transfer-method"><summary>How the transfer is calculated</summary>
 <div class="sr-transfer-overview">
 <div><h3>How to use this workbench</h3>
 <ol><li>Choose a source sequence and a target by name or record ID.</li><li>Select the number of coefficients, beginning at each sequence's first stored nonzero value.</li><li>Inspect the transfer kernel, inverse, coefficient residuals, and index shifts. Export the exact certificate to reproduce the comparison.</li></ol>
 <p>Only scalar records are eligible. For a coefficient triangle, first choose a scalar column or specialization.</p></div>
 <div class="sr-transfer-algebra"><h3>What is being calculated?</h3>
 <p>Remove each stored leading-zero prefix, retaining its original index separately. Write the resulting ordinary generating polynomials as</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="A(z)=\sum_{j=0}^{L-1}a_j z^j,\qquad B(z)=\sum_{j=0}^{L-1}b_j z^j">A(z) = sum_(j=0)^(L-1) a_j z^j; B(z) = sum_(j=0)^(L-1) b_j z^j</p>
 <p>Since <code>a_0</code> and <code>b_0</code> are nonzero, both series are invertible in the truncated rational power-series ring, and formal division over the rationals defines</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}H(z)&amp;\equiv B(z)A(z)^{-1}\pmod{z^L}\\K(z)&amp;\equiv A(z)B(z)^{-1}\pmod{z^L}\end{aligned}">H(z) = B(z)/A(z) (mod z^L); K(z) = A(z)/B(z) (mod z^L)</p>
 <p>Equivalently, the coefficient transport and its inverse are</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}b_j&amp;=\sum_{i=0}^{j}h_i a_{j-i}\\a_j&amp;=\sum_{i=0}^{j}k_i b_{j-i}\end{aligned}">b_j = sum_(i=0)^j h_i*a_(j-i); a_j = sum_(i=0)^j k_i*b_(j-i)</p>
 <p>The certificate verifies all three identities, modulo <code>z^L</code>:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="H(z)A(z)\equiv B(z),\quad K(z)B(z)\equiv A(z),\quad H(z)K(z)\equiv1\pmod{z^L}">H*A = B; K*B = A; H*K = 1 (mod z^L)</p>
 <p>Original sequence indices, leading-zero prefixes, and shifts are reported separately. The map acts on anchored tails, not on the original index domains without accounting for those shifts.</p></div>
 </div>
 </details>
 <details class="sr-transfer-example"><summary>Worked example: Euler values to shifted Fibonacci values</summary>
 <p>Use signed even Euler values <code>1, −1, 5, −61</code> and Fibonacci values <code>0, 1, 1, 2, 3</code>. The Fibonacci tail begins at original index 1. The anchored ordinary series, through four coefficients, are</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}A(z)&amp;\equiv 1-z+5z^2-61z^3\\B(z)&amp;\equiv 1+z+2z^2+3z^3\end{aligned}\pmod{z^4}">A(z) = 1 - z + 5z^2 - 61z^3; B(z) = 1 + z + 2z^2 + 3z^3 (mod z^4)</p>
 <p>Exact formal division gives the forward and inverse kernels</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}H(z)&amp;\equiv 1+2z-z^2+53z^3\\K(z)&amp;\equiv 1-2z+5z^2-65z^3\end{aligned}\pmod{z^4}">H(z) = 1 + 2z - z^2 + 53z^3; K(z) = 1 - 2z + 5z^2 - 65z^3 (mod z^4)</p>
 <p>For example, at tail position 2, convolution recovers the target coefficient:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}b_2&amp;=h_0a_2+h_1a_1+h_2a_0\\&amp;=(1)(5)+(2)(-1)+(-1)(1)=2.\end{aligned}">b_2 = h_0*a_2 + h_1*a_1 + h_2*a_0 = 1*5 + 2*(-1) + (-1)*1 = 2</p>
 <p>The corresponding leading four-by-four convolution matrices are</p>
 <div class="sr-transfer-static-matrices">
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(H)=\begin{pmatrix}1&amp;0&amp;0&amp;0\\2&amp;1&amp;0&amp;0\\-1&amp;2&amp;1&amp;0\\53&amp;-1&amp;2&amp;1\end{pmatrix}">L(H) = [[1,0,0,0], [2,1,0,0], [-1,2,1,0], [53,-1,2,1]]</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(K)=\begin{pmatrix}1&amp;0&amp;0&amp;0\\-2&amp;1&amp;0&amp;0\\5&amp;-2&amp;1&amp;0\\-65&amp;5&amp;-2&amp;1\end{pmatrix}">L(K) = [[1,0,0,0], [-2,1,0,0], [5,-2,1,0], [-65,5,-2,1]]</p>
 </div>
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(H)L(K)=L(K)L(H)=I_4">L(H)*L(K) = L(K)*L(H) = I_4</p>
 <p>For local row n and column k, the product has the exact Toeplitz convolution formula</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\bigl(L(H)L(K)\bigr)_{n,k}=\sum_{\ell=k}^{n}h_{n-\ell}k_{\ell-k}=\delta_{n,k},\qquad 0\le k\le n<4">(L(H)*L(K))[n,k] = sum_(ell=k)^n h_(n-ell)*k_(ell-k) = delta(n,k), 0<=k<=n<4</p>
 <p>For example, the bottom-left entry cancels exactly:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\bigl(L(H)L(K)\bigr)_{3,0}=(53)(1)+(-1)(-2)+(2)(5)+(1)(-65)=0">(L(H)*L(K))[3,0] = (53)*(1) + (-1)*(-2) + (2)*(5) + (1)*(-65) = 0</p>

 <p>Here is the corresponding action on the anchored sequence coefficients:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(H)\begin{pmatrix}1\\-1\\5\\-61\end{pmatrix}=\begin{pmatrix}1\\1\\2\\3\end{pmatrix}">L(H) [1, -1, 5, -61] = [1, 1, 2, 3]</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(K)\begin{pmatrix}1\\1\\2\\3\end{pmatrix}=\begin{pmatrix}1\\-1\\5\\-61\end{pmatrix}">L(K) [1, 1, 2, 3] = [1, -1, 5, -61]</p>
 <p>Matrix rows and columns use anchored tail positions. The displayed four-by-four matrices are exact inverses, with the original Euler and Fibonacci indices tracked separately.</p>
 <p>Only four coefficients are verified here. The cited derivation addresses the separate infinite formal relation and the boundary term required to transport a recurrence.</p>
 </details>
 <details class="sr-transfer-sources"><summary>Sources and derivations</summary><p class="sr-transfer-links"><a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-connections/IDENTITIES.md">Recurrence and transfer derivations</a> · <a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-connections/AUDIT.md">Research audit</a> · <a href="collection/demonstrations/EULER_PACKETS.html#transfer-the-euler-sequence-to-fibonacci-values">Euler and Fibonacci worked derivation</a> · <a download href="assets/sequence-research-connections.json">Related connections JSON</a></p></details>
 <details class="sr-transfer-compose-details"><summary>Composition through a third sequence</summary><div class="sr-transfer-compose-static">
 <h3>Composition through an intermediate sequence</h3>
 <p>For three anchored series with nonzero constant coefficients, formal division gives the following finite composition:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="H_{AC}(z)\equiv H_{BC}(z)H_{AB}(z)\pmod{z^L},\qquad L(H_{AC})=L(H_{BC})L(H_{AB})">H_AC(z) = H_BC(z)*H_AB(z) (mod z^L); L(H_AC) = L(H_BC)*L(H_AB)</p>
 <p>The original index shifts add: <code>Δ_AC = Δ_AB + Δ_BC</code>. This is an algebraic consequence of invertible anchored series, not evidence of a shared recurrence or agreement beyond stored coefficients. The interactive composition panel checks each coefficient and exports its exact certificate.</p>
 </div></details>
 </section>'''
    about='<section id="library-sources" class="sl-optional-section"><h2>Definitions, scope, and downloads</h2><details class="sl-topic-disclosure"><summary>Read catalogue scope and download exact source files</summary><p>The '+str(len(expanded_catalogue()))+' parameter records cover reciprocal powers (N=2–16, r=1–8, complementing the curated sequences), transfer tangents (N=2–16), congruential coefficient components (N=2–12, 1≤j&lt;N, r=1–4), Appell components (N=2–6, 0≤j&lt;N, r=1–2, x=1 or 2), and classical multisections (N=2–12, 0≤j&lt;N).</p><p>Research families include secancy parameter columns (N=2–12, k=1–8), theta specializations (x=1–12), and theta polynomial columns (k=1–12). Ordinary k-step families add 120 instances with order 2–16, power 1–4, and weight 1–2. Ten k-bonacci records with zero initial seeds use orders 7–16 and store 48 terms.</p><p>Other scalar records store 24 terms at their stated offsets. Polynomial columns begin at their first nonzero n. The coefficient triangles preserve complete rows n=0–12, with separate row, column, and flat indices. The supported Appell columns retain their polynomial row map Nn+k. Other parameter records use n=0–23. Each rational coefficient is reduced before its signed numerator or positive denominator is recorded. Every entry links to its definition and states its normalization.</p><p>Different parameter choices can yield the same sequence. Finite comparisons alone do not prove an identity or establish novelty. Hypergeometric labels distinguish term formulas, generating functions, and coefficient extraction.</p><p><a download href="assets/sequence-library-index.csv">Complete index CSV</a> · <a download href="assets/sequence-formulas.json">All formula representations JSON</a> · <a download href="assets/sequence-formula-source.zip">Exact Python generator and defining source</a> · <a href="sequence-archive.html">Research archive and generator</a></p></details></section>'
    # Keep older hash links functional. With JavaScript they redirect to focused
    # pages; without JavaScript the targeted gateway provides a usable link.
    legacy_routes=[
        ('transfers','sequence-transfers.html#transfers','Transfer workbench'),
        ('comparison','sequence-compare.html#comparison','Sequence comparison'),
        ('research-families','sequence-research.html#research-families','Research families'),
        ('generalized','sequence-research.html#generalized','Generalized families'),
        ('family-explorer','sequence-research.html#generalized','Generalized family explorer'),
        ('research-graph','sequence-connections.html#research-graph','Connection graph'),
        ('identify','sequence-identify.html#identify','Sequence identification'),
        ('modular-dynamics','sequence-modular.html#modular-dynamics','Modular dynamics'),
        ('research-notebooks','sequence-workspace.html#research-notebooks','Research notebooks and older workspaces'),
        ('oeis','sequence-oeis.html#oeis','OEIS reference lookup')]
    legacy=''.join('<section class="sl-legacy-gateway" id="'+key+'"><h2>'+label+'</h2><p>This tool now has its own page. <a href="'+url+'">Open '+label+'</a>.</p></section>'
                   for key,url,label in legacy_routes)
    closed_theorems=('''<section id="closed-theorems" class="sl-optional-section">
      <h2>Closed forms and proved identities</h2>
      <p>Choose a result to read its precise domain and normalization.
      For complete derivations, use the mathematical source linked below.</p>
      <details><summary>Universal Hankel 4F3 and real-zero theorem</summary>
      <p>The A163865 Hankel determinant is independent of the binomial-shift parameter.
      The empty determinant equals 1. For N at least 1 and arbitrary complex c:</p>
      <pre tabindex="0" role="region" aria-label="Hankel hypergeometric expression">H_N(c) = 2^(N-1) 4F3(-N/2, (1-N)/2, (N-1)/2, N/2;
                           -1/2, -1/4, 1/4; -c^2/16)</pre>
      <p>The series terminates. Its zeros as a polynomial in c are real and nonzero
      for N at least 2. The generating-function denominator divides
      ((1-2z)^4 + 4c^2 z^2)^3.</p>
      <p><a href="sequence-families/KFOR-CF-W-0-1.html">Inspect the exact c=1 determinants</a>.</p>
      </details>
      <details><summary>Arbitrary two-delay residue-class formulas</summary>
      <p>For C_n = [z^n](1-u z^p-v z^q)^(-r), p and q are positive integers.
      Removing their gcd and enumerating pi+qj=n gives one terminating
      QF(Q-1) for each admissible residue. The exact finite sum handles zero weights
      and negative integral r without undefined divisions.</p>
      <p><a href="sequence-families/KFOR-CF-S-2-5-1-1-1.html">Read the 2,5 delay example and its 5F4 subsequence</a>.</p>
      </details>
      <details><summary>Weighted A163865 and all polynomially weighted jets</summary>
      <p>For d at least 0, u_n = J_(n,d)(1)+n J_(n-1,d)(1), where
      J_(n,d)(lambda) = sum binom(n,2m) falling(m,d) binom(2m,m) lambda^(n-2m).
      Every polynomial weight decomposes into finitely many of these cases.</p>
      <pre tabindex="0" role="region" aria-label="Weighted jet generating function">sum u_n z^n =
      ((2d)!/d!) z^(2d) (1+(2d-1)z-(2d+4)z^2)
      / (1-2z-3z^2)^(d+3/2)</pre>
      <p>The d=0 case is identified as A163865 in the supplied source.
      <a href="sequence-families/KFOR-CF-JET-01.html">Read the d=1 exact sequence</a>.</p>
      </details>
      <details><summary>Fixed-size Chebyshev formula for weighted Hankel transforms</summary>
      <p>The Hankel transform of u_n at weight d is W_N^[d](1). Collection III
      proves a root-free formula using the remainders of two Chebyshev polynomials
      modulo x^2+(2d+1)cx-4. It works at repeated roots and the initial zero block.
      The generic minimal eventual recurrence order is 4(d+1)(d+2)+4.
      At c=1 the exact orders for d=0,1,2 are 12, 28, 52.</p>
      <p>The first d=1 quartic is W_4(c) = 48(27c^4+6c^2+2). It has no real zeros, unlike the unweighted family.</p>
      <p><a href="sequence-families/KFOR-CF-W-2-1.html">Read the d=2 determinant sequence</a>.</p>
      </details>
      <details><summary>Six formulas recovered from source papers</summary>
      <p>The documented reductions cover Bernoulli four-block tangents, four-block
      Euler convolutions, integer Meixner–Pollaczek polynomials, beta-moment
      determinants, beta-binomial splitter polynomials, and the squarefree
      zeta-ratio identity already proved in Paper III. Their normalization,
      source locations and historical scope are in the full source note.</p>
      <p><a href="generalized-families/GF-CF-MEIXNER.html">Read the Meixner–Pollaczek family</a>.</p>
      </details>
    </section>''')
    closed_calculator=(
        '<details id="closed-calculator-panel" class="sl-topic-disclosure">'
        '<summary>Calculate exact coefficients and determinants</summary>'
        '<div id="closed-calculator-root">'
        '<p>The optional worksheet calculates finite integer windows for two-delay coefficients, '
        'weighted binomial transforms, weighted Hankel determinants and integer Meixner–Pollaczek polynomials. '
        'It does not claim that finite agreement proves an infinite identity.</p>'
        '</div><noscript><p>JavaScript is not required to read the definitions and exact record tables above. '
        'Open any record for its complete static 24-term table.</p></noscript></details>')
    closed_css='<link rel="stylesheet" href="assets/sequence-closed-forms.css?v='+hashlib.sha256(
        (site.output/'assets/sequence-closed-forms.css').read_bytes()).hexdigest()[:12]+'">'
    # One central entry point. Specialized pages stay as focused views, not
    # separate catalogues. Expensive tools mount only when opened.
    workflow_nav=(
        '<nav id="sequence-research-desk" class="sl-workflow-nav" aria-label="Sequence research workflow">'
        '<a href="#library-search"><strong>1. Find</strong><span>Records and formulas</span></a>'
        '<a href="#closed-calculator-panel"><strong>2. Calculate</strong><span>Exact integer values</span></a>'
        '<a href="#sequence-research-hub"><strong>3. Investigate</strong><span>Connections and comparisons</span></a>'
        '<a href="#sequence-proof-path"><strong>4. Verify</strong><span>Proofs and evidence</span></a></nav>')
    research_hub=(
        '<section id="sequence-research-hub" class="sl-optional-section sl-research-hub">'
        '<h2>Continue your research</h2>'
        '<p>All '+f'{total:,}'+' integer records and their '+f'{representations:,}'+' formula representations share one index. '
        'The views below use those same records and retain their exact indices and review boundaries.</p>'
        '<div class="sl-workflow-choices">'
        '<article><h3>Compare and transfer</h3>'
        '<p>Compare exact prefixes, inspect finite disagreements, or build algebraic transfer certificates.</p>'
        '<p><a href="sequence-compare.html#comparison">Compare sequences</a> · '
        '<a href="sequence-transfers.html#transfers">Transfer workbench</a></p></article>'
        '<article><h3>Explore constructions</h3>'
        '<p>Browse all '+str(len(generalized['families']))+' generalized definitions, their source papers and member records.</p>'
        '<p><a href="sequence-research.html#research-families">Research families</a> · '
        '<a href="generalized-families/index.html">Complete family index</a></p></article>'
        '<article><h3>Cross-check and reproduce</h3>'
        '<p>Inspect the retained OEIS reference data, source notes, and reproducible exact generators.</p>'
        '<p><a href="sequence-oeis.html#oeis">OEIS reference lookup</a> · '
        '<a href="#sequence-proof-path">Proof and verification records</a></p></article>'
        '</div></section>'
        '<section id="sequence-proof-path" class="sl-optional-section sl-proof-path">'
        '<h2>Definitions, derivations, and verification</h2>'
        '<p>Formula records retain their original source and review status. The mathematical proofs, '
        'finite exact tests, and OEIS comparisons are separate forms of evidence.</p>'
        '<details class="sl-topic-disclosure" id="sl-theorem-disclosure"><summary>Read the main closed-form theorem summaries</summary>'
        +closed_theorems+'</details>'
        '<details class="sl-topic-disclosure"><summary>Open source notes and exact verification programs</summary>'
        '<p><a href="sequence-closed-forms.html#closed-theorems">Full Closed Forms reading page</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/COLLECTION_II_ADDITIONS.md">'
        'Complete mathematical supplement</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_closed_forms_extended.py">'
        'Independent Python regression tests</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_closed_forms_core.mjs">'
        'Exact browser arithmetic tests</a></p>'
        '<p>The pinned historical OEIS comparison covers its original 2,292 records. '
        'New closed-form records are labeled as not yet checked against that bulk snapshot. '
        'Finite agreement is not a proof of infinite equality or historical novelty.</p></details>'
        '</section>')
    site.page('sequence-library.html','Sequence Library · Search',
              wrap(closed_css+header+workflow_nav+controls+closed_calculator+research_hub+about+legacy,page_kind='search'))
    site.page('sequence-transfers.html','Sequence Library · Transfer',
              wrap(page_heading('Transfer between sequences',
                  'Calculate exact forward and inverse convolution maps between stored scalar prefixes. All certificates refer to the selected finite window.',
                  'transfer','transfers')+transfers,page_kind='transfer'))
    site.page('sequence-compare.html','Sequence Library · Compare',
              wrap(page_heading('Compare sequences',
                  'Compare up to four stored sequences or OEIS excerpts. Exact values remain in the data table while plots show finite windows.',
                  'compare','comparison')+
                  '<section id="comparison"><h2>Comparison workbench</h2><p>Enable JavaScript to compare records. You can browse the <a href="sequence-library.html#library-search">sequence search</a> without it.</p></section>',
                  page_kind='compare'))
    research_nav=('<nav class="sl-research-nav" aria-label="Research and tool pages">'
                  '<a href="#research-families">Research families</a><a href="#generalized">Generalized families</a>'
                  '<a href="sequence-closed-forms.html#closed-forms">Closed forms II–III</a>'
                  '<a href="sequence-connections.html#research-graph">Connections</a>'
                  '<a href="sequence-identify.html#identify">Identify terms</a>'
                  '<a href="sequence-modular.html#modular-dynamics">Modular dynamics</a>'
                  '<a href="sequence-workspace.html#research-notebooks">Combined notebooks</a></nav>')
    research_choices=('<div class="sl-research-choices" aria-label="Specialized research tools">'
                      '<article><h3><a href="sequence-closed-forms.html#closed-forms">Closed forms II–III</a></h3>'
                      '<p>Read six exact construction families, 24 curated integer records and their source derivations.</p></article>'
                      '<article><h3><a href="sequence-connections.html#research-graph">Connection graph</a></h3>'
                      '<p>Inspect documented sequence relationships, directed paths and exact transfer compositions.</p></article>'
                      '<article><h3><a href="sequence-identify.html#identify">Identify terms</a></h3>'
                      '<p>Test integer patterns and transformations against local records or retained OEIS excerpts.</p></article>'
                      '<article><h3><a href="sequence-modular.html#modular-dynamics">Modular dynamics</a></h3>'
                      '<p>Explore recurrence states and verify a finite modular cycle certificate.</p></article>'
                      '<article><h3><a href="sequence-workspace.html#research-notebooks">Research notebooks</a></h3>'
                      '<p>Save settings across several tools in the combined compatibility workspace.</p></article></div>')
    research_legacy=''.join(
        '<section class="sl-legacy-gateway" id="'+key+'"><h2>'+label+'</h2>'
        '<p>Open the <a href="'+url+'">'+label.lower()+' page</a>.</p></section>'
        for key,url,label in [
            ('research-graph','sequence-connections.html#research-graph','Connection graph'),
            ('identify','sequence-identify.html#identify','Sequence identification'),
            ('modular-dynamics','sequence-modular.html#modular-dynamics','Modular dynamics'),
            ('research-notebooks','sequence-workspace.html#research-notebooks','Research notebooks')])
    site.page('sequence-research.html','Sequence Library · Research',
              wrap(page_heading('Research families',
                  'Browse exact research records and generalized family definitions. Each interactive research tool has its own page.',
                  'research','research-families')+research_nav+research.replace('<details class="sl-topic-disclosure">','<details class="sl-topic-disclosure" open>',1)+generalized_sections(only=['generalized'])+
                   '<h2 class="sl-tool-heading">Research workbenches</h2>'+research_choices+research_legacy,
                   page_kind='research'))
    # The closed-form supplement is a focused reading page, not a sixth tool
    # crowded into Search. Its exact records also appear in the unified index.
    closed_entries=[item for item in entries if item.get('closed_form_collection')]
    closed_families=[item for item in generalized['families'] if item['id'].startswith('GF-CF-')]
    closed_cards=''.join(
        '<article class="sar-card"><h3><a href="'+e(family['url'])+'">'+e(family['title'])+'</a></h3>'
        '<p>'+e(family['note'])+'</p><p>'+str(len(family['record_ids']))+' indexed integer records.</p></article>'
        for family in closed_families)
    closed_rows=''.join(
        '<tr><th scope="row"><a href="'+e(item['url'])+'">'+e(item['id'])+'</a></th>'
        '<td>'+e(item['title'])+'</td><td>'+str(item['offset'])+'</td>'
        '<td>'+e(', '.join(item['terms'][:5]))+'</td><td>'+('Source-supplied '+e(item['oeis'])+' · bulk comparison pending' if item.get('source_claimed_oeis') else 'Not yet compared')+'</td></tr>'
        for item in closed_entries)
    active_closed_families=sum(bool(family['record_ids']) for family in closed_families)
    closed_body=(
        closed_css+
        page_heading('Closed forms: Collections II and III',
            'Exact integer records, source derivations and explicit review boundaries.',
            'research','closed-forms')+
        '<section id="closed-forms"><h2>What is in the collection?</h2><p>'+str(len(closed_entries))+' exact integer records across '+str(active_closed_families)+' constructions, '
        'plus '+str(len(closed_families)-active_closed_families)+' definition-only families. Every record has '
        '24 exact values, at least two formula representations, a stated index convention, and CSV/JSON downloads. '
        'The historical pinned OEIS comparison has not been run on these additions.</p>'
        '<p><a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/IDENTITIES.md">'
        'Read definitions, proofs and reproduction notes</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_closed_forms.py">'
        'Review the exact independent tests</a> · '
        '<a href="sequence-library.html#library-search">Search the full library</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/COLLECTION_II_ADDITIONS.md">Read the complete theorem supplement</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_closed_forms_extended.py">Review the extended exact tests</a></p></section>'+closed_theorems+
        closed_calculator+
        '<section><h2>'+str(len(closed_families))+' source-linked families</h2><div class="sar-grid">'+closed_cards+'</div></section>'+
        '<section><h2>'+str(len(closed_entries))+' integer records</h2><p>Displayed prefixes retain their original offsets. '
        'The four-block rows start at m=1 and refer to analytic exponent 4m-1; beta-binomial '
        'records contain explicitly unnormalized integer values. Follow each record for full tables, '
        'plots and exports.</p><div class="sar-scroll" tabindex="0" role="region" '
        'aria-label="Closed-form sequence records"><table><thead><tr><th scope="col">Record</th>'
        '<th scope="col">Construction</th><th scope="col">First index</th>'
        '<th scope="col">First five exact terms</th><th scope="col">OEIS</th></tr></thead>'
        '<tbody>'+closed_rows+'</tbody></table></div></section>')
    site.page('sequence-closed-forms.html','Sequence Library · Closed forms II and III',
              wrap(closed_body,page_kind='closed-forms'))

    for filename,title,description,section_id,page_kind in [
        ('sequence-connections.html','Sequence connections',
         'Inspect documented relationships, directed paths and exact scalar transfer compositions.',
         'research-graph','connections'),
        ('sequence-identify.html','Identify a sequence',
         'Check finite integer patterns and their transforms against local records or the retained OEIS data.',
         'identify','identify'),
        ('sequence-modular.html','Modular dynamics',
         'Explore recurrence states modulo m and check exact finite cycle certificates.',
         'modular-dynamics','modular')]:
        site.page(filename,'Sequence Library · '+title,
                  wrap(page_heading(title,description,'research',section_id)+
                       '<nav class="sl-tool-back"><a href="sequence-research.html#research-families">Research families and other tools</a>'
                       ' · <a href="sequence-workspace.html#research-notebooks">Combined workspace</a></nav>'+
                       generalized_sections(only=[section_id]).replace('<details>','<details open>',1),page_kind=page_kind))
    standalone_reference=reference.replace('<details class="sl-topic-disclosure">',
                                           '<details class="sl-topic-disclosure" open>',1)
    site.page('sequence-oeis.html','Sequence Library · OEIS',
              wrap(page_heading('OEIS reference lookup',
                  'Search the retained OEIS terms and names in your browser. Reference excerpts do not include mathematical offsets.',
                  'oeis','oeis')+standalone_reference,page_kind='oeis'))
    # Optional compatibility workspace supports notebooks spanning several tools.
    site.page('sequence-workspace.html','Sequence Library · Combined workspace',
              wrap(page_heading('Combined research workspace',
                  'Advanced compatibility view for saved notebooks and links that use several tools together.',
                  'research','library-search')+controls+transfers+research+generalized_sections()+
                  '<section id="comparison"></section>'+reference+about,
                  page_kind='workspace'))

    rows=''.join('<tr><th scope="row"><a href="../'+x['url']+'">'+e(x['id'])+'</a></th><td>'+e(x['title'])+'</td><td>'+e(x['kind'])+'</td><td>'+str(len(x['formulas']))+'</td><td>'+str(x['offset'])+'</td></tr>' for x in entries)
    site.page('sequence-library/index.html','Complete sequence index',wrap('<nav><a href="../sequence-library.html">Search the library</a></nav><h1>Complete sequence index</h1><p>This index lists all '+str(total)+' local records. Definitions and exact tables remain available without JavaScript.</p><div class="sar-scroll" tabindex="0" role="region" aria-label="Complete sequence index"><table><thead><tr><th scope="col">ID</th><th scope="col">Name</th><th scope="col">Family</th><th scope="col">Formulas</th><th scope="col">Offset</th></tr></thead><tbody>'+rows+'</tbody></table></div>','../'))
    urls={item['id']:item['url'] for item in entries}
    for entry in entries:
        if entry['collection']!='formulas':continue
        identifier=entry['id'];start=entry['offset'];end=start+len(entry['terms'])-1
        site.write('sequence-families/'+identifier+'.json',json.dumps(entry,ensure_ascii=False,separators=(',',':'))+'\n')
        if entry.get('triangle'):
            site.write('sequence-families/'+identifier+'.csv','j,row_n,column_k,source_degree,value\n'+''.join(f'{j},{cell_coordinates(entry,j)[0]},{cell_coordinates(entry,j)[1]},{source_degree(entry,j)},{v}\n' for j,v in enumerate(entry['terms'])))
        else:site.write('sequence-families/'+identifier+'.csv','n,a(n)\n'+''.join(f'{n},{v}\n' for n,v in enumerate(entry['terms'],start=start)))
        site.write('sequence-families/'+identifier+'.txt','# '+identifier+' '+entry['title']+'\n'+''.join(f'{n} {v}\n' for n,v in enumerate(entry['terms'],start=start)))
        rational=entry.get('rational_terms')
        related=''.join('<p>Related local definition: <a href="../'+e(urls[x['id']])+'#definition">'+e(x['id'])+'</a>. '+e(x['note'])+'</p>' for x in entry.get('related_records',[]))
        coordinates=lambda n:('<td>'+str(cell_coordinates(entry,n)[0])+'</td><td>'+str(cell_coordinates(entry,n)[1])+'</td>') if entry.get('triangle') else ''
        index_label='Flat j' if entry.get('triangle') else 'Local n'
        value_label='a(j)' if entry.get('triangle') else 'a(n)'
        index_note=('The stored flat index is j='+str(start)+'–'+str(end)+'. Each row n contains columns k in increasing order. The source degree is computed from the row, not from j. ' if entry.get('triangle') else 'The local index is n='+str(start)+'–'+str(end)+'. The source degree/index map is '+e(entry['degree'])+'. ')+'The table contains exact integers. Plots use only stored values. '+e(entry['explanation'])
        rows=''.join('<tr id="n-'+str(n)+'"><th scope="row">'+str(n)+'</th>'+coordinates(n)+'<td>'+str(source_degree(entry,n))+'</td><td>'+value+'</td>'+('<td>'+e(rational[n-start])+'</td>' if rational else '')+'</tr>' for n,value in enumerate(entry['terms'],start=start))
        body='<nav aria-label="Breadcrumb"><a href="../sequence-library.html">Sequence library</a> / '+e(identifier)+'</nav><header class="sar-header"><p class="sar-kicker">'+e(identifier)+' / Parameter record</p><h1>'+e(entry['title'])+'</h1><p>'+e(entry['status'])+'</p><nav aria-label="Entry sections"><a href="#definition">Definition</a><a href="#formulas">Formula representations</a>'+('<a href="#triangle">Coefficient triangle</a>' if entry.get('triangle') else '')+'<a href="#plot">Plot</a><a href="#exact-data">Exact data</a><a href="#oeis-matches">OEIS comparisons</a></nav></header><section id="definition"><h2>Definition and indexing</h2><p class="sar-formula">'+e(entry['formula'])+'</p><p>'+index_note+'</p>'+related+'</section><section id="formulas"><h2>Equivalent representations</h2>'+formula_block(entry)+'</section>'+triangle_section(entry)+plot_section(entry)+'<section id="exact-data"><h2>Exact indexed data</h2><p><a download href="'+identifier+'.csv">CSV</a> · <a download href="'+identifier+'.txt">Indexed text</a> · <a download href="'+identifier+'.json">Entry JSON with all formulas and comparisons</a></p><div class="sar-scroll" tabindex="0" role="region" aria-label="Exact stored values"><table><thead><tr><th scope="col">'+index_label+'</th>'+('<th scope="col">Row n</th><th scope="col">Column k</th>' if entry.get('triangle') else '')+'<th scope="col">Source degree/index</th><th scope="col">'+value_label+'</th>'+('<th scope="col">Original rational q(n)</th>' if rational else '')+'</tr></thead><tbody>'+rows+'</tbody></table></div></section>'+matches_block(entry)+'<section id="sources"><h2>Sources and reproduction</h2><p><a href="'+e(entry['source'])+'">Published construction source</a></p><p>The terms and formulas use the parameters listed above. KFOR identifiers are local to this library. OEIS entries use A-numbers.</p><details><summary>Reproduce this sequence</summary><p>Source: <code>'+REGISTRY_PATH+'</code>. Parameter grids and exact reproduction are implemented in <code>tools/sequence_formula_catalogue.py</code>. Run the generator with the listed parameters to reproduce the stored terms.</p><p><a download href="../assets/sequence-formula-source.zip">Download the exact Python generator and source</a>. Extract the bundle, then run <code>python tools/sequence_formula_catalogue.py --id '+identifier+'</code>.</p></details></section>'
        body=body.replace('<section id="plot"',entry_details(entry)+'<section id="plot"',1)
        if entry.get('calculator_url'):
            handoff='<p class="sl-record-calculator"><a href="../'+e(entry['calculator_url'],quote=True)+'">Recalculate this sequence in the unified exact workspace</a>. The original indexed data and source formulas remain available here.</p>'
            body=body.replace('</section><section id="formulas">',handoff+'</section><section id="formulas">',1)
        if entry.get('linear_addition'):body=body.replace(REGISTRY_PATH,'research/sequence-connections/IDENTITIES.md')
        site.page(entry['url'],entry['title']+' · '+identifier,wrap(body,'../',entry))
        site.search.append(dict(title=entry['title']+' · '+identifier,group='Collection',kind='Examples',work_ids=[],url=entry['url'],text=' '.join(f['expression'] for f in entry['formulas'])))
    site.search.append(dict(title='Sequence Library · Search',group='Collection',kind='Examples',work_ids=[],url='sequence-library.html',text=f'{total} indexed records and {representations} exact formula representations.'))
    for title,url in [('Transfer between sequences','sequence-transfers.html'),('Compare sequences','sequence-compare.html'),('Research families and sequence tools','sequence-research.html'),('Connection graph','sequence-connections.html'),('Identify a sequence','sequence-identify.html'),('Modular dynamics','sequence-modular.html'),('OEIS reference lookup','sequence-oeis.html')]:
        site.search.append(dict(title=title,group='Collection',kind='Examples',work_ids=[],url=url,text='Sequence Library exact arithmetic and research tools.'))
    return dict(entries=total,new_entries=len(expanded_catalogue()),formulas=representations,oeis_sequences=snapshot['sequence_count'],oeis_bytes=sum(x['bytes'] for x in snapshot['snapshot']['files']),generalized_families=len(generalized['families']),generalized_sources=len(generalized['sources']))
