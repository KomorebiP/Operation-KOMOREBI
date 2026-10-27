#!/usr/bin/env python3
"""Compare protected spans and inventory contextual rhythm candidates."""
from pathlib import Path
from collections import Counter
import difflib
import hashlib
import json
import re

ROOT = Path('/dev/shm/komorebi_core_monograph_fbc994080222')
OUT = ROOT / 'editorial/rhythm_review'
FILES = json.loads((OUT / 'i_ii_companions_files.json').read_text())
JOURNAL = json.loads((OUT / 'i_ii_companions_journal.json').read_text())
LITERAL_ENVS = re.compile(r'\\begin\{(lstlisting|verbatim|Verbatim|minted)\}.*?\\end\{\1\}', re.S)
MATH = re.compile(r'(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$|\\\[.*?\\\]|\\\(.*?\\\)|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}', re.S)
MACRO = re.compile(r'\\(code|nolinkurl|texttt|source|excerpt|input|include|VerbatimInput|label|ref|eqref|pageref|cite|hyperref)\*?')

def balanced(s, start, opening, closing):
    depth = 0
    for i in range(start, len(s)):
        if s[i] == opening and (i == 0 or s[i-1] != '\\'):
            depth += 1
        elif s[i] == closing and (i == 0 or s[i-1] != '\\'):
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError(f'unclosed {opening}: {s[start:start+60]!r}')

def macro_spans(s):
    spans = []
    for m in MACRO.finditer(s):
        pos = m.end()
        while pos < len(s) and s[pos].isspace(): pos += 1
        if pos < len(s) and s[pos] == '[':
            pos = balanced(s, pos, '[', ']')
        for _ in range(2 if m.group(1) == 'excerpt' else 1):
            while pos < len(s) and s[pos].isspace(): pos += 1
            if pos < len(s) and s[pos] == '{':
                pos = balanced(s, pos, '{', '}')
        spans.append((m.start(), pos))
    return spans

def strip_literals(s):
    return LITERAL_ENVS.sub(lambda m: ' ' * len(m.group()), s)

def protected(s, is_machine):
    nolit = strip_literals(s)
    result = {
        'preamble': [s.split('\\begin{document}', 1)[0]],
        'literal_environments': [m.group() for m in LITERAL_ENVS.finditer(s)],
        'mathematical_spans': [m.group() for m in MATH.finditer(nolit)],
        'literal_and_reference_macros': [s[a:b] for a, b in macro_spans(s)],
        'control_sequences': re.findall(r'\\(?:[A-Za-z@]+|[^A-Za-z\s])', s),
        'braces': re.findall('[{}]', s),
        'environments': re.findall(r'\\(?:begin|end)\{[^}]+\}', s),
        'numbers': re.findall(r'\d+(?:[.,]\d+)*', s),
        'comments': re.findall(r'(?<!\\)%[^\n]*', s),
    }
    if is_machine:
        result['exact_typed_signatures'] = [s[s.index('\\clearpage\\section{Typed core signatures}'):s.index('\\clearpage\\section{Complete action registry}')]]
        result['exact_action_registry'] = [s[s.index('\\clearpage\\section{Complete action registry}'):s.index('\\clearpage\\section{Operation and hypothesis vocabulary}')]]
        result['exact_ontology'] = [s[s.index('\\clearpage\\section{Operation and hypothesis vocabulary}'):s.index('\\clearpage\\section{Historical Lean record map}')]]
        result['exact_historical_map'] = [s[s.index('\\clearpage\\section{Historical Lean record map}'):s.index('\\clearpage\\section{Preserved verification receipt}')]]
    return result

def mask_protected(s, is_machine):
    spans = [(0, s.index('\\begin{document}') + len('\\begin{document}'))]
    spans += [(m.start(), m.end()) for m in LITERAL_ENVS.finditer(s)]
    spans += [(m.start(), m.end()) for m in MATH.finditer(strip_literals(s))]
    spans += macro_spans(s)
    spans += [(m.start(), m.end()) for m in re.finditer(r'(?<!\\)%[^\n]*', s)]
    if is_machine:
        spans += [(s.index('\\clearpage\\section{Typed core signatures}'), s.index('\\clearpage\\section{Operation and hypothesis vocabulary}'))]
        spans += [(s.index('\\begin{longtable}', s.index('\\section{Operation and hypothesis vocabulary}')), s.index('\\clearpage\\section{Preserved verification receipt}'))]
    chars = list(s)
    for a, b in spans:
        chars[a:b] = ['\n' if c == '\n' else ' ' for c in s[a:b]]
    return ''.join(chars)

validation = []
inventory = []
diffs = []
for info in FILES:
    name = info['file']
    before = (ROOT / info['backup']).read_text()
    after = (ROOT / name).read_text()
    is_machine = '/machine/' in name
    pre, post = protected(before, is_machine), protected(after, is_machine)
    checks = {k: {'equal': pre[k] == post[k], 'before_count': len(pre[k]), 'after_count': len(post[k])} for k in pre}
    assert all(x['equal'] for x in checks.values()), (name, checks)
    masked = mask_protected(before, is_machine)
    candidates = []
    for category, pattern in [('semicolon', r';'), ('dash_or_range', r'---+|--|[—–]'), ('hyphen_compound', r'\b[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+\b')]:
        for match in re.finditer(pattern, masked):
            start, end = match.span()
            line = before[:start].count('\n') + 1
            changed = any(e['file'] == name and e['before_line'] == line
                          and e['old'].count(match.group()) > e['new'].count(match.group())
                          and (category == e['category'] or category == 'hyphen_compound' and e['category'] in ['hyphen','formulaic'])
                          for e in JOURNAL)
            candidates.append({'category': category, 'line': line, 'text': match.group(),
                               'paragraph_line': before.splitlines()[line-1],
                               'decision': 'changed' if changed else 'retained',
                               'rationale': ('Individually reviewed change in exact journal.' if changed else
                                             'Section or row range; retain its range punctuation.' if category == 'dash_or_range' else
                                             'Technical compound, precise scope modifier, number word, version, or established interface term; retain for meaning/readability.')})
    counts = Counter(c['category'] for c in candidates)
    decisions = Counter((c['category'], c['decision']) for c in candidates)
    # An exact, reproducible word proxy, not a claim about rendered word count.
    words = re.findall(r"\b[A-Za-z]+(?:'[A-Za-z]+)?\b", re.sub(r'\\[A-Za-z@]+', ' ', masked))
    entry = {'file': name, 'lines_read': len(before.splitlines()), 'raw_whitespace_words': len(before.split()),
             'masked_prose_word_proxy': len(words), 'raw_semicolons_before': before.count(';'),
             'raw_semicolons_after': after.count(';'), 'candidate_counts': dict(counts),
             'decisions': {f'{cat}:{decision}': n for (cat, decision), n in decisions.items()},
             'candidates': candidates}
    inventory.append(entry)
    validation.append({'file': name, 'checks': checks, 'before_sha256': hashlib.sha256(before.encode()).hexdigest(),
                       'after_sha256': hashlib.sha256(after.encode()).hexdigest(), 'all_protected_checks_equal': True})
    diffs.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=info['backup'], tofile=name))

(OUT / 'i_ii_companions_candidates.json').write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + '\n')
(OUT / 'i_ii_companions_preservation.json').write_text(json.dumps(validation, indent=2) + '\n')
(OUT / 'i_ii_companions_changes.patch').write_text(''.join(diffs))
print(json.dumps([{k:v for k,v in item.items() if k != 'candidates'} for item in inventory], indent=2))
print('Protected checks: all equal')
