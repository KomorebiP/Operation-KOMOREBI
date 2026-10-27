"""Separate synchronous compiler-boundary diagnostic; no main scan writes."""
import datetime
import functools
import json
import resource
import sys
import time
from pathlib import Path

WORKSPACE = Path('/workspace/scratch/40dd7e475149')
SOURCE = WORKSPACE / 'arc-fullbank/block17'
EVIDENCE = WORKSPACE / 'arc-evidence/later-source-audit'
TASK_ID = '3e6067c3'
sys.path.insert(0, str(SOURCE))
import engine


def main():
    task = engine.sanitize(engine.read(
        WORKSPACE / 'arc-offline-data/arc-agi_evaluation_challenges.json')[TASK_ID])
    assert all(set(test) == {'input'} for test in task['test'])
    engine.initialize()
    report = {
        'task_id_for_external_diagnostic_only': TASK_ID,
        'task_id_passed_to_compiler': False,
        'task_semantic_hash': engine.contract.digest(task),
        'code_hash': engine.code_hash(),
        'bank_hash': engine.bank_hash(),
        'compile_call': 'engine.compile_record(sanitized_task, True)',
        'instrumentation': 'synchronous transparent wrappers around legacy.compile_old and contract._compile_one',
        'instrumentation_preserves_arguments_returns_and_exceptions': True,
        'no_faulthandler': True,
        'no_debugger_memory_reads_trace_profile_or_timer_signal': True,
        'separate_compile_process': True,
        'main_worker_or_checkpoint_changes': False,
        'query_solutions_opened': False,
        'extra_temporary_cpu_use': True,
        'attribution_limit': 'Only this separate instrumented reproduction is observed, not the existing live workers.',
        'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    report_path = EVIDENCE / 'boundary_compile_stage_diagnostic_report.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    started = time.monotonic()
    cpu_started = time.process_time()
    original_old = engine.legacy.compile_old
    original_one = engine.contract._compile_one
    boundary_log = (EVIDENCE / 'boundary_compile_stage_diagnostic_boundaries.jsonl').open('w')

    def log(phase, compiler_name, exception_type=None):
        entry = {'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'elapsed_seconds': time.monotonic() - started,
                 'phase': phase, 'compiler_name': compiler_name}
        if exception_type is not None:
            entry['exception_type'] = exception_type
        boundary_log.write(json.dumps(entry, sort_keys=True) + '\n')
        boundary_log.flush()

    def call_logged(original, compiler_name, args, kwargs):
        log('before', compiler_name)
        try:
            value = original(*args, **kwargs)
        except BaseException as error:
            log('after_exception', compiler_name, type(error).__name__)
            raise
        log('after_return', compiler_name)
        return value

    @functools.wraps(original_old)
    def logged_old(*args, **kwargs):
        return call_logged(original_old, 'legacy.compile_old', args, kwargs)

    @functools.wraps(original_one)
    def logged_one(*args, **kwargs):
        entrant = args[0] if args else kwargs['entrant']
        return call_logged(original_one, 'contract._compile_one:' + entrant.name, args, kwargs)

    engine.legacy.compile_old = logged_old
    engine.contract._compile_one = logged_one
    exit_code = 0
    try:
        record = engine.compile_record(task, True)
        engine.verify(record)
        report.update(outcome='completed', diagnostic_record_hash=record['content_hash'],
                      diagnostic_candidate_count=len(record['candidates']),
                      diagnostic_receipt_count=len(record['receipts']),
                      record_admitted_to_main_census=False, record_payload_written=False)
    except KeyboardInterrupt:
        report.update(outcome='interrupted_by_owned_session_ctrl_c',
                      diagnostic_record_hash=None, record_admitted_to_main_census=False)
        exit_code = 130
    except BaseException as error:
        report.update(outcome='diagnostic_exception', exception_type=type(error).__name__,
                      diagnostic_record_hash=None, record_admitted_to_main_census=False)
        exit_code = 1
    finally:
        engine.legacy.compile_old = original_old
        engine.contract._compile_one = original_one
        boundary_log.close()
        report.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      wall_seconds=time.monotonic() - started,
                      own_process_cpu_seconds=time.process_time() - cpu_started,
                      own_process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'outcome': report['outcome'], 'report_path': str(report_path),
                      'wall_seconds': report['wall_seconds']}, sort_keys=True), flush=True)
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
