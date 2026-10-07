#!/usr/bin/env python3
"""Dry-run by default. Create/upload only an empty private repository owned by KomorebiP.

Never publishes, changes visibility, force-pushes, chooses a license, or pushes tags.
The CLI-authenticated account is checked before any remote write. No token is printed.
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'KomorebiP'
OWNER_ID = 52508850
AUTHOR = 'Komorebi P.'
EMAIL = '52508850+KomorebiP@users.noreply.github.com'
DEFAULT_REPOSITORY = 'KomorebiP/komorebi-math'
DESCRIPTION = 'Representations, obstructions, and verified computation. Research Preview 1.'

class PreparationError(RuntimeError):
    """A safety gate or execution step did not pass."""

def validate_destination(name: str) -> str:
    parts = name.split('/')
    if len(parts) != 2 or parts[0] != OWNER:
        raise PreparationError(f'Destination must belong to {OWNER}; received {name!r}.')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', parts[1]):
        raise PreparationError('Repository name contains an unsupported character or length.')
    if parts[1] in {'.', '..'} or parts[1].endswith('.git'):
        raise PreparationError('Use an owner/repository name, not a Git URL or path.')
    return name

def require_owner(profile: dict[str, Any]) -> None:
    if profile.get('login') != OWNER or profile.get('id') != OWNER_ID:
        raise PreparationError(f'GitHub CLI must be authenticated as the verified account {OWNER}.')

def require_private_repository(meta: dict[str, Any], destination: str) -> None:
    require_owner(meta.get('owner', {}))
    if meta.get('full_name') != destination or meta.get('private') is not True:
        raise PreparationError('Refusing a different destination or a nonprivate repository.')
    if meta.get('archived') or meta.get('disabled') or meta.get('fork'):
        raise PreparationError('Refusing an archived, disabled, or forked destination.')

def require_empty(branches: Any) -> None:
    if not isinstance(branches, list) or branches:
        raise PreparationError('Destination has existing branch history or an invalid listing; nothing will be overwritten.')

def require_identity_history(raw: str) -> None:
    lines = raw.splitlines()
    if not lines:
        raise PreparationError('No local commits are available.')
    for line in lines:
        if line.split('\x00') != [AUTHOR, EMAIL, AUTHOR, EMAIL]:
            raise PreparationError('Commit history contains author/committer metadata outside the approved pseudonym.')

def private_create_command(destination: str) -> list[str]:
    validate_destination(destination)
    return ['gh', 'repo', 'create', destination, '--private', '--disable-wiki',
            '--description', DESCRIPTION]

def push_command() -> list[str]:
    return ['git', '-c', 'credential.helper=', '-c',
            'credential.helper=!gh auth git-credential', 'push', 'origin',
            'HEAD:refs/heads/main']

def invoke(argv: list[str], *, allow_failure: bool = False, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(argv, cwd=ROOT, text=True, encoding='utf-8',
                                errors='replace', capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PreparationError(f'Could not finish {argv[0]} {argv[1]}: {exc}') from exc
    if result.returncode and not allow_failure:
        # No environment variables or auth-token values are ever requested or printed.
        detail = (result.stderr or result.stdout).strip()[-1800:]
        raise PreparationError(f'{argv[0]} {argv[1]} failed ({result.returncode}): {detail}')
    return result

def decode_json(result: subprocess.CompletedProcess[str]) -> Any:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise PreparationError('GitHub CLI returned invalid JSON; refusing to infer repository state.') from exc

def execute(destination: str) -> dict[str, Any]:
    validate_destination(destination)
    for name in ('git', 'gh'):
        if shutil.which(name) is None:
            raise PreparationError(f'{name} is unavailable. Install/use it locally; no remote operation was attempted.')
    top = Path(invoke(['git', 'rev-parse', '--show-toplevel']).stdout.strip()).resolve()
    if top != ROOT:
        raise PreparationError('Run from a clone of the supplied clean Git bundle, not inside an older parent repository.')
    if invoke(['git', 'symbolic-ref', '--short', 'HEAD']).stdout.strip() != 'main':
        raise PreparationError('The upload helper accepts only the reviewed main branch.')
    if invoke(['git', 'status', '--porcelain', '--untracked-files=all']).stdout.strip():
        raise PreparationError('The local worktree must be clean; review and commit intended changes first.')
    invoke([sys.executable, '-B', 'tools/check_github_ready.py', '--check-git'])
    require_identity_history(invoke(['git', 'log', '--all', '--format=%an%x00%ae%x00%cn%x00%ce']).stdout)
    require_owner(decode_json(invoke(['gh', 'api', 'user'])))
    expected_url = f'https://github.com/{destination}.git'
    remotes = invoke(['git', 'remote']).stdout.split()
    if any(name != 'origin' for name in remotes):
        raise PreparationError('Unexpected additional remotes exist. Review them before this first upload.')
    if 'origin' in remotes:
        fetch_url = invoke(['git', 'remote', 'get-url', 'origin']).stdout.strip()
        push_urls = invoke(['git', 'remote', 'get-url', '--push', '--all', 'origin']).stdout.splitlines()
        if fetch_url != expected_url or push_urls != [expected_url]:
            raise PreparationError('origin is not the intended HTTPS destination. Remove the local bundle origin first.')
    local_head = invoke(['git', 'rev-parse', 'HEAD']).stdout.strip()
    result = invoke(['gh', 'api', f'repos/{destination}'], allow_failure=True)
    created = False
    if result.returncode:
        if '(HTTP 404)' not in result.stderr:
            raise PreparationError('Repository lookup failed without an unambiguous HTTP 404. No creation attempted.')
        # A 404 can mean inaccessible, not nonexistent. Creation may fail safely;
        # this script never changes another repository to make creation succeed.
        invoke(private_create_command(destination))
        created = True
        result = invoke(['gh', 'api', f'repos/{destination}'])
    require_private_repository(decode_json(result), destination)
    require_empty(decode_json(invoke(['gh', 'api', f'repos/{destination}/branches?per_page=1'])))
    # Recheck visibility immediately before installing the source.
    require_private_repository(decode_json(invoke(['gh', 'api', f'repos/{destination}'])), destination)
    if 'origin' not in remotes:
        invoke(['git', 'remote', 'add', 'origin', expected_url])
    invoke(push_command(), timeout=300)
    remote_ref = decode_json(invoke(['gh', 'api', f'repos/{destination}/git/ref/heads/main']))
    if remote_ref.get('object', {}).get('sha') != local_head:
        raise PreparationError('Push returned but the remote main commit does not match; inspect the remote before retrying.')
    invoke(['gh', 'api', '--method', 'PATCH', f'repos/{destination}', '-f', 'default_branch=main'])
    require_private_repository(decode_json(invoke(['gh', 'api', f'repos/{destination}'])), destination)
    return {'status': 'PRIVATE_PUSH_VERIFIED', 'repository': destination,
            'created_this_run': created, 'branch': 'main', 'commit': local_head,
            'visibility': 'private', 'public_release_published': False,
            'workflow_results_verified': False}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default=DEFAULT_REPOSITORY)
    parser.add_argument('--execute', action='store_true', help='Perform the private create/push after all checks. Default is a dry run.')
    args = parser.parse_args()
    try:
        destination = validate_destination(args.repo)
        if not args.execute:
            print(json.dumps({'status': 'DRY_RUN_NO_CHANGES', 'repository': destination,
                 'visibility': 'private', 'branch': 'main', 'create_command': private_create_command(destination),
                 'push_command': push_command(), 'requires': ['git', 'authenticated gh as KomorebiP',
                 'clean sanitized bundle clone', 'empty private remote'],
                 'does_not': ['change visibility', 'choose a license', 'force push', 'push tags', 'publish a release']}, indent=2))
            return 0
        print(json.dumps(execute(destination), indent=2))
        return 0
    except PreparationError as exc:
        print(json.dumps({'status': 'BLOCKED_OR_INCOMPLETE', 'reason': str(exc),
                         'note': 'No force push, deletion, visibility change, or public release is performed. A newly created private remote may remain if a later step failed.'}, indent=2), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
