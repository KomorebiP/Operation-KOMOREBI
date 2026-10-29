"""Validate inline Markdown navigation against a case-sensitive committed tree.

This checks the maintained documentation's inline-link and ATX-heading syntax,
not arbitrary Markdown or remote HTTP availability. Original-source fragments
are reported separately because their documents are not rendered here.
"""
import html
import posixpath
import re
from urllib.parse import unquote, urlsplit


def prose(text):
    """Discard fenced examples so they cannot supply real links or anchors."""
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
        else:
            lines.append(line)
    return '\n'.join(lines)


def anchors(text):
    text = prose(text)
    explicit = re.findall(r'<a\s+[^>]*?id=[\"\']([^\"\']+)[\"\']', text)
    assert len(explicit) == len(set(explicit)), 'Duplicate explicit navigation anchor'
    automatic = set()
    for heading in re.findall(r'^ {0,3}#{1,6}\s+(.+?)\s*$', text, re.M):
        heading = re.sub(r'\s+#+$', '', heading)
        heading = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', heading)
        heading = html.unescape(re.sub(r'<[^>]*>', '', heading)).lower()
        slug = re.sub(r'[^\w\- ]', '', heading).replace(' ', '-')
        candidate = slug
        index = 0
        while candidate in automatic:
            index += 1
            candidate = slug+'-'+str(index)
        automatic.add(candidate)
    return set(explicit) | automatic


def inline_targets(text):
    text = prose(text)
    # Inline code is an example, not a rendered link. Heading code text is kept
    # separately by anchors(), since it still contributes to a heading slug.
    text = re.sub(r'(`+)(?!`)(.*?)\1(?!`)', '', text)
    # Coefficient/evaluation notation such as \bigl[Sa\bigr](0) is math,
    # not an inline Markdown link to a file named "0".
    text = re.sub(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', '', text, flags=re.S)
    pattern = r'\]\(\s*(<[^>\n]+>|(?:[^\s()\\]|\\.|\([^()]*\))+)(?:\s+[\"\'][^\n]*?[\"\'])?\s*\)'
    for match in re.finditer(pattern, text):
        target = match[1]
        if target.startswith('<'):
            target = target[1:-1]
        yield re.sub(r'\\([() ])', r'\1', html.unescape(target))


def check_links(documents, known_files):
    files = set(known_files) | set(documents)
    directories = set()
    for path in files:
        parent = posixpath.dirname(path)
        while parent:
            directories.add(parent)
            parent = posixpath.dirname(parent)
    directory_root = '.'
    directories.add(directory_root)
    ids = {path: anchors(content) for path, content in documents.items()}
    counts = dict(relative_links=0, directory_links=0, checked_fragments=0,
                  external_links_not_checked=0, source_fragments_not_checked=0)
    for path, content in documents.items():
        for target in inline_targets(content):
            parts = urlsplit(target)
            if parts.scheme or parts.netloc:
                counts['external_links_not_checked'] += 1
                continue
            relative = unquote(parts.path)
            assert '\\' not in relative and not relative.startswith('/'), (path, target, 'Non-relative repository path')
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), relative)) if relative else path
            assert resolved != '..' and not resolved.startswith('../'), (path, target, 'Escapes repository')
            if relative.endswith('/'):
                assert resolved in directories, (path, target, 'Missing directory')
            else:
                assert resolved in files or resolved in directories, (path, target, 'Missing file or directory; paths are case-sensitive')
            counts['relative_links'] += 1
            if resolved in directories:
                counts['directory_links'] += 1
            if parts.fragment:
                anchor = unquote(parts.fragment)
                if resolved in documents:
                    assert anchor in ids[resolved], (path, target, 'Missing navigation anchor')
                    counts['checked_fragments'] += 1
                else:
                    counts['source_fragments_not_checked'] += 1
    return counts
