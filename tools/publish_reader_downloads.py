"""Publish verified, revision-bound exports before the matching Pages deploy.

Only used by the trusted main-branch reader workflow. Retries reconcile existing
release assets by size and digest; they never replace a different asset.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from reader_delivery import REPOSITORY, verify


def request(url, token, *, data=None, content_type='application/json'):
    headers = {'Authorization': 'Bearer '+token, 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': content_type,
               'User-Agent': 'Operation-KOMOREBI-reader-publication'}
    with urlopen(Request(url, data=data, headers=headers), timeout=120) as response:
        return json.load(response)


def confirm_asset(asset, path):
    raw = path.read_bytes()
    expected = 'sha256:'+hashlib.sha256(raw).hexdigest()
    if asset['size'] != len(raw):
        raise ValueError('An existing release asset has a different size: '+path.name)
    if asset.get('digest'):
        if asset['digest'] != expected:
            raise ValueError('An existing release asset has a different digest: '+path.name)
    else:
        # Old GitHub assets may not have an API digest. Check the public bytes.
        with urlopen(asset['browser_download_url'], timeout=120) as response:
            if response.read() != raw:
                raise ValueError('An existing release asset has different bytes: '+path.name)


def publish(site, artifacts, token):
    manifest = verify(site, artifacts)
    if os.environ.get('GITHUB_REPOSITORY') != REPOSITORY or os.environ.get('GITHUB_SHA') != manifest['revision']:
        raise ValueError('Release publication must match this repository and workflow revision')
    api = 'https://api.github.com/repos/'+REPOSITORY
    try:
        release = request(api+'/releases/tags/'+manifest['tag'], token)
    except HTTPError as error:
        if error.code != 404:
            raise
        payload = dict(tag_name=manifest['tag'], target_commitish=manifest['revision'],
                       name='Reader downloads '+manifest['revision'][:12], make_latest='false',
                       body=(artifacts/'RELEASE.md').read_text(encoding='utf-8'))
        release = request(api+'/releases', token, data=json.dumps(payload).encode())
    existing = {}
    page = 1
    while True:
        rows = request(api+'/releases/'+str(release['id'])+'/assets?per_page=100&page='+str(page), token)
        existing.update({asset['name']: asset for asset in rows})
        if len(rows) < 100:
            break
        page += 1
    names = sorted(record['asset'] for record in manifest['files'].values())
    names += ['delivery-manifest.json', 'SHA256SUMS.txt', 'RELEASE.md']
    for number, name in enumerate(names, 1):
        path = artifacts/name
        if name in existing:
            confirm_asset(existing[name], path)
        else:
            url = 'https://uploads.github.com/repos/'+REPOSITORY+'/releases/'+str(release['id'])+'/assets?name='+quote(name)
            content_type = 'application/zip' if name.endswith('.zip') else 'application/octet-stream'
            result = request(url, token, data=path.read_bytes(), content_type=content_type)
            confirm_asset(result, path)
        if number % 25 == 0 or number == len(names):
            print('Verified release exports: '+str(number)+'/'+str(len(names)), flush=True)
    print('Reader download release: '+release['html_url'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--artifacts', type=Path, required=True)
    args = parser.parse_args()
    publish(args.site.resolve(), args.artifacts.resolve(), os.environ['GITHUB_TOKEN'])
