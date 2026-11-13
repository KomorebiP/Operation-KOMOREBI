"""A local lookup over the glossary's maintained definitions and subject groups."""
import html
import re


def glossary_return_links(content, config):
    """Add a return route after each complete entry, retaining its original HTML."""
    inserts = []
    for term in config['glossary']:
        marker = '<p><a id="'+html.escape(term['id'], quote=True)+'"></a></p>'
        if content.count(marker) != 1:
            raise ValueError('Glossary entry anchor changed: '+term['id'])
        start = content.index(marker)+len(marker)
        boundary = re.search(r'<p><a id=|<h2\b', content[start:])
        inserts.append(start+boundary.start() if boundary else len(content))
    link = '<p class="glossary-return"><a href="#glossary-lookup">Back to glossary lookup</a></p>'
    for end in sorted(inserts, reverse=True):
        content = content[:end]+link+content[end:]
    return content


def glossary_lookup(config):
    e = html.escape
    sections = {s['id']: s['title'] for s in config['glossary_sections']}
    terms = sorted(config['glossary'], key=lambda t: t['term'].casefold())
    body = ('<section id="glossary-lookup" class="glossary-lookup" aria-labelledby="glossary-lookup-title">'
            '<h2 id="glossary-lookup-title">Find a glossary term</h2>'
            '<p id="glossary-help">Search a name, abbreviation or words in a definition or example. Try “nullspace”, “projection” or “CRT”. Matches link to the full entry, '
            'with fuller explanations, examples and related terms. Select a term name to read its complete entry. You can also browse the subjects and alphabetical index below.</p>'
            '<noscript><p>Quick lookup needs JavaScript. Use the subject links and alphabetical index below, or your browser’s Find command.</p></noscript>'
            '<form id="glossary-form" role="search" aria-label="Glossary" aria-describedby="glossary-help" hidden>'
            '<label for="glossary-query">Term, abbreviation or words to find</label>'
            '<input id="glossary-query" type="search" name="q" autocomplete="off">'
            '<label for="glossary-subject">Subject</label><select id="glossary-subject" name="subject">'
            '<option value="">All subjects</option>')
    body += ''.join('<option value="'+e(key, quote=True)+'">'+e(title)+'</option>' for key, title in sections.items())
    body += ('</select><div class="glossary-actions"><button type="submit">Find terms</button>'
             '<button type="reset">Clear lookup</button></div></form>'
             '<p id="glossary-status" role="status" aria-atomic="true" hidden></p>'
             '<div id="glossary-matches" hidden><h3 id="glossary-results-title" tabindex="-1">Matching terms</h3>'
             '<ul id="glossary-results">')
    for term in terms:
        subject = sections[term['section']]
        aliases = term.get('aliases', [])
        search = glossary_search_text(term)
        body += ('<li data-glossary-entry data-subject="'+e(term['section'], quote=True)+'" '
                 'data-aliases="'+e('\n'.join(aliases), quote=True)+'" '
                 'data-term="'+e(term['term'], quote=True)+'" data-search="'+e(search, quote=True)+'">'
                 '<h4><a href="#'+e(term['id'], quote=True)+'">'+e(term['term'])+'</a></h4>'
                 '<p class="glossary-subject">'+e(subject)+'</p><p>'+e(term['definition'])+'</p>')
        if term.get('explanation'):
            body += '<p>'+e(term['explanation'][0])+'</p>'
        if aliases:
            body += '<p class="glossary-aliases"><strong>Also called:</strong> '+e(', '.join(aliases))+'.</p>'
        if term.get('quick_example'):
            body += '<p class="glossary-example"><strong>Quick example:</strong> '+e(term['quick_example'])+'</p>'
        if term.get('example_text'):
            body += '<p class="glossary-example"><strong>In the worked example:</strong> '+e(term['example_text'])+'</p>'
        if term.get('note'):
            body += '<p><strong>Keep in mind:</strong> '+e(term['note'])+'</p>'
        body += '</li>'
    return body+'</ul></div></section>'


def glossary_search_text(term):
    """Use the same vocabulary in local lookup and the collection search."""
    return ' '.join([term['term'], *term.get('aliases', []), term['definition'],
                     *term.get('explanation', []),
                     term.get('example_text', ''), term.get('quick_example', ''), term.get('note', '')])


def glossary_reader_page(content, config):
    """Arrange the unchanged reference into subjects and complete term slides.

    All content remains readable without JavaScript. Enhancement selects among
    these original nodes, so a term has one canonical anchor in either view.
    """
    e = html.escape
    content = glossary_return_links(content, config)
    heading = re.search(r'<h1\b[^>]*>.*?</h1>', content, re.S)
    if not heading:
        raise ValueError('Glossary heading missing')
    sections = config['glossary_sections']
    def marker(key):
        return '<p><a id="'+e(key, quote=True)+'"></a></p>'
    starts = [content.index(marker(section['id'])) for section in sections]
    last_term = [term for term in config['glossary'] if term['section'] == sections[-1]['id']][-1]
    last_start = content.index(marker(last_term['id'])) + len(marker(last_term['id']))
    tail = re.search(r'<h2\b', content[last_start:])
    if not tail:
        raise ValueError('Glossary reference index missing')
    end = last_start + tail.start()
    preface = content[heading.end():starts[0]]
    guide = preface + content[end:]
    body = (content[:heading.end()] +
        '<p class="glossary-intro">Choose a section, then read it continuously in <strong>Long</strong> view '
        'or explore one complete term at a time in <strong>Slides</strong>.</p>' +
        '<details id="glossary-search" class="glossary-search"><summary>Find a term</summary>' +
        glossary_lookup(config) + '</details>' +
        '<div id="glossary-browser" class="glossary-browser">'
        '<div id="glossary-controls" class="glossary-controls" hidden>'
        '<div class="glossary-section-picker"><label for="glossary-section">Section</label>'
        '<select id="glossary-section"><option value="">All sections</option>')
    for section in sections:
        body += '<option value="'+e(section['id'], quote=True)+'">'+e(section['title'])+'</option>'
    body += ('</select></div><fieldset class="glossary-view"><legend>Reading view</legend>'
        '<button type="button" id="glossary-view-long" aria-pressed="true">Long</button>'
        '<button type="button" id="glossary-view-slides" aria-pressed="false">Slides</button>'
        '</fieldset></div>'
        '<div id="glossary-overview"><h2 id="glossary-sections-title">Choose a section</h2>'
        '<nav id="glossary-sections" class="glossary-section-grid" aria-labelledby="glossary-sections-title" tabindex="-1">')
    for number, section in enumerate(sections, 1):
        count = sum(term['section'] == section['id'] for term in config['glossary'])
        body += ('<a class="glossary-section-card" href="#'+e(section['id'], quote=True)+'">'
            '<span class="glossary-section-number">'+str(number).zfill(2)+' · '+str(count)+' terms</span>'
            '<strong>'+e(section['title'])+'</strong><span>'+e(section['description'])+'</span></a>')
    body += ('</nav></div><div id="glossary-reading-controls" class="glossary-reading-controls" hidden>'
        '<a href="#glossary-sections">All sections</a>'
        '<div class="glossary-term-picker"><label for="glossary-term">Jump to a term</label>'
        '<select id="glossary-term"></select></div>'
        '<p id="glossary-position" role="status" aria-atomic="true"></p></div>')
    def navigation():
        return ('<nav class="glossary-step-controls" aria-label="Glossary reading navigation" hidden>'
            '<button type="button" data-glossary-previous>Previous</button>'
            '<button type="button" data-glossary-next>Next</button></nav>')
    body += navigation() + '<div id="glossary-panels" class="glossary-panels">'
    for index, section in enumerate(sections):
        group = [term for term in config['glossary'] if term['section'] == section['id']]
        chunk = content[starts[index]:starts[index+1] if index+1 < len(starts) else end]
        first = chunk.index(marker(group[0]['id']))
        intro = chunk[:first]
        # Keep the original term links in an optional section index.
        nav_start = intro.rfind('<p>')
        if nav_start >= 0:
            intro = intro[:nav_start] + '<details class="glossary-term-index"><summary>Terms in this section</summary>' + intro[nav_start:] + '</details>'
        body += ('<section class="glossary-panel" data-glossary-panel="'+e(section['id'], quote=True)+'" '
            'data-title="'+e(section['title'], quote=True)+'" aria-label="'+e(section['title'], quote=True)+'">'+intro)
        for term_index, term in enumerate(group):
            start = chunk.index(marker(term['id']))
            finish = chunk.index(marker(group[term_index+1]['id'])) if term_index+1 < len(group) else len(chunk)
            body += ('<section class="glossary-term" data-glossary-term="'+e(term['id'], quote=True)+'" '
                'data-title="'+e(term['term'], quote=True)+'" aria-label="'+e(term['term'], quote=True)+'">'+
                chunk[start:finish]+'</section>')
        body += '</section>'
    body += ('</div>'+navigation()+'</div><details id="glossary-guide" class="glossary-guide">'
        '<summary>Reading routes, comparisons and A–Z index</summary>'+guide+'</details>')
    return body
