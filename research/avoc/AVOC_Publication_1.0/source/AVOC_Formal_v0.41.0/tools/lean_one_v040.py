#!/usr/bin/env python3
"""Bounded warnings-as-errors Lean check with current source/import/output evidence."""
import argparse, os, signal, subprocess, time
from pathlib import Path
from release_common_v040 import ROOT, RD, kit_path, sha, write_json, import_hashes

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source'); parser.add_argument('--seconds', type=int, default=180)
    parser.add_argument('--no-output', action='store_true'); parser.add_argument('--log')
    args = parser.parse_args()
    if args.seconds <= 0: parser.error('--seconds must be positive')
    source = (ROOT/args.source).resolve()
    if not source.is_relative_to(ROOT) or not source.is_file(): parser.error('source must be a current project file')
    relative = source.relative_to(ROOT).as_posix(); kit = kit_path()
    build = ROOT/'.lake/build/lib/lean'; build.mkdir(parents=True, exist_ok=True)
    output = build/Path(relative).with_suffix('.olean'); output.parent.mkdir(parents=True, exist_ok=True)
    paths = [build] + [p/'.lake/build/lib/lean' for p in sorted((kit/'workspace/.lake/packages').iterdir()) if p.is_dir()]
    env = os.environ.copy(); env['LEAN_PATH'] = ':'.join(map(str, paths))
    env['PATH'] = str(kit/'toolchain/bin') + ':' + env.get('PATH', '')
    executable = kit/'toolchain/bin/lean'; command = [str(executable), '-j1', '-DwarningAsError=true']
    if not args.no_output: command += ['-o', str(output)]
    command += [str(source)]
    log = ROOT/(args.log or ('results/v0.40.0/' + source.stem + '.log')); log.parent.mkdir(parents=True, exist_ok=True)
    before = sha(source); imports_before = import_hashes(relative); started = time.monotonic(); timeout = False
    with log.open('w') as stream:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try: code = process.wait(timeout=args.seconds)
        except subprocess.TimeoutExpired:
            timeout = True; os.killpg(process.pid, signal.SIGKILL); code = process.wait()
    record = dict(source=relative, command=command, returncode=code, timed_out=timeout,
                  seconds=round(time.monotonic()-started, 3), warning_as_error=True,
                  lean_executable_sha256=sha(executable), source_before_sha256=before,
                  source_sha256=sha(source), source_unchanged=before==sha(source),
                  import_outputs=imports_before, imports_unchanged=imports_before==import_hashes(relative),
                  log=log.relative_to(ROOT).as_posix(), log_sha256=sha(log),
                  output_sha256=sha(output) if not args.no_output and code==0 and output.is_file() else None)
    write_json(log.with_suffix('.json'), record)
    print(log.read_text(), end='')
    print(f"{relative}: returncode={code}, timed_out={timeout}, seconds={record['seconds']}")
    return code if not timeout else 124
if __name__ == '__main__': raise SystemExit(main())
