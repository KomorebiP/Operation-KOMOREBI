#!/usr/bin/env python3
"""Fetch Mozilla's pinned PDF.js viewer and retain its license and file hashes."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import urllib.request
import zipfile

VERSION = '6.4.299'
URL = 'https://github.com/mozilla/pdf.js/releases/download/v6.4.299/pdfjs-6.4.299-dist.zip'
SHA256 = 'f2245eb7ef3f674c872fe568a177bfec15874f5c034613e55d8e307f93ebd86d'
CONFIG = '''"use strict";
// Configure the viewer before it opens a document, including when embedded.
const eventDocument = window.parent.document;
eventDocument.addEventListener("webviewerloaded", event => {
  if (event.detail.source !== window) return;
  const options = window.PDFViewerApplicationOptions;
  options.set("disablePreferences", true);
  options.set("enableScripting", false);
  options.set("externalLinkTarget", 2);
  options.set("defaultUrl", "");
  const work = new URLSearchParams(location.search).get("work");
  if (work) {
    const target = new URL(work, location.href);
    if (target.origin === location.origin && /\\/collection\\/works\\/[a-z0-9-]+\\.html$/.test(target.pathname)) {
      const link = document.createElement("a");
      link.href = target.href;
      link.textContent = "Back to work";
      link.className = "toolbarButton komorebi-return";
      link.target = "_top";
      document.getElementById("toolbarViewerLeft").prepend(link);
    }
  }
});
'''
CSS = '.komorebi-return{display:inline-flex!important;align-items:center;width:auto!important;padding:0 8px!important;color:var(--main-color);text-decoration:underline;white-space:nowrap;font:12px system-ui,sans-serif}.komorebi-return::before{display:none!important}\n'


def extract(raw, output):
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError('PDF.js release integrity mismatch')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use a new empty PDF.js runtime directory')
    output.mkdir(parents=True, exist_ok=True)
    files = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            path = PurePosixPath(member.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in member.filename or ':' in member.filename:
                raise ValueError('Unsafe PDF.js archive path')
            data = archive.read(member)
            if member.filename == 'web/viewer.html':
                marker = b'<script src="viewer.mjs" type="module"></script>'
                if data.count(marker) != 1:
                    raise ValueError('PDF.js configuration insertion point changed')
                data = data.replace(marker, b'<link rel="stylesheet" href="komorebi-config.css">\n  <script src="komorebi-config.js"></script>\n  '+marker)
            target = output/path.as_posix()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            files[path.as_posix()] = hashlib.sha256(data).hexdigest()
    (output/'web/komorebi-config.js').write_text(CONFIG, encoding='utf-8', newline='\n')
    files['web/komorebi-config.js'] = hashlib.sha256(CONFIG.encode()).hexdigest()
    (output/'web/komorebi-config.css').write_text(CSS, encoding='utf-8', newline='\n')
    files['web/komorebi-config.css'] = hashlib.sha256(CSS.encode()).hexdigest()
    record = dict(runtime='PDF.js', version=VERSION, url=URL, archive_sha256=SHA256,
                  customization='Load Komorebi settings and return-link styles before viewer.mjs. Disable PDF scripting and saved preference overrides. Add a validated return link to the work page.',
                  files=files)
    (output/'SOURCE.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    return record


def verify(root):
    record = json.loads((root/'SOURCE.json').read_bytes())
    if record['archive_sha256'] != SHA256 or record['version'] != VERSION:
        raise ValueError('Unexpected PDF.js runtime')
    required = {'LICENSE', 'web/viewer.html', 'web/viewer.mjs', 'web/viewer.css',
                'web/komorebi-config.js', 'web/komorebi-config.css', 'build/pdf.mjs', 'build/pdf.worker.mjs'}
    if not required <= record['files'].keys():
        raise ValueError('Incomplete PDF.js runtime')
    for path, expected in record['files'].items():
        p = PurePosixPath(path)
        if p.is_absolute() or '..' in p.parts or '\\' in path or ':' in path:
            raise ValueError('Unsafe runtime manifest path')
        if hashlib.sha256((root/path).read_bytes()).hexdigest() != expected:
            raise ValueError('PDF.js file integrity mismatch: '+path)
    if (root/'web/komorebi-config.js').read_text(encoding='utf-8') != CONFIG:
        raise ValueError('PDF.js reader settings mismatch')
    if (root/'web/komorebi-config.css').read_text(encoding='utf-8') != CSS:
        raise ValueError('PDF.js reader styles mismatch')
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--archive', type=Path, help='Use an already downloaded release ZIP')
    args = p.parse_args()
    if args.archive:
        raw = args.archive.read_bytes()
    else:
        with urllib.request.urlopen(URL, timeout=60) as response:
            raw = response.read(20*1024*1024)
    record = extract(raw, args.output)
    verify(args.output)
    print(json.dumps(dict(runtime=record['runtime'], version=VERSION, files=len(record['files']), verified=True)))


if __name__ == '__main__':
    main()
