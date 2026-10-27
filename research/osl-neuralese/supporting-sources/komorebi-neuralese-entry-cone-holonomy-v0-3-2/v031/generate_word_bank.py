from pathlib import Path
import resource
import time

from matched_controls import write_word_bank


if __name__ == "__main__":
    started = time.perf_counter()
    destination = Path(__file__).with_name("MATCHED_CONTROL_WORD_BANK.json")
    bank = write_word_bank(destination)
    elapsed = time.perf_counter() - started
    print(f"WORD_BANK={destination}")
    print(f"RECORDS={bank['record_count']}")
    print(f"CONTROLS={bank['control_word_count']}")
    print(f"CONTENT_SHA256={bank['content_sha256_without_this_field']}")
    print(f"ELAPSED_SECONDS={elapsed:.6f}")
    print(f"PEAK_RSS_KIB={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}")
