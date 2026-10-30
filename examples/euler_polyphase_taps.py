#!/usr/bin/env python3
"""An exact forward-FIR example: split both the signal and the filter taps.

Run: python -B euler_polyphase_taps.py
Save the finite evidence: python -B euler_polyphase_taps.py --output results.json
Only complete windows of the supplied finite signal are returned. No padding,
periodic extension, floating arithmetic, or Fourier transform is used.
"""
import argparse
import json
from math import comb
from pathlib import Path


TAPS = (1, -2, 3, 1)
TEST_FILTERS = (TAPS, (1,), (0, 1), (1, 0, 0, 1), (0, -2, 0, 3), (1, -1, 2, -3, 4))


def signed_even_euler(count):
    values = []
    for n in range(count):
        values.append(1 if n == 0 else -sum(comb(2*n, 2*j)*values[j] for j in range(n)))
    return values


def direct_filter(signal, taps):
    if not taps:
        raise ValueError('A filter must have at least one tap')
    return [sum(h*signal[n+j] for j, h in enumerate(taps))
            for n in range(max(0, len(signal)-len(taps)+1))]


def split_filter(signal, taps):
    if not taps:
        raise ValueError('A filter must have at least one tap')
    a0, a1 = signal[::2], signal[1::2]
    h0, h1 = taps[::2], taps[1::2]
    count = max(0, len(signal)-len(taps)+1)
    even = [sum(h*a0[q+j] for j, h in enumerate(h0))
            + sum(h*a1[q+j] for j, h in enumerate(h1))
            for q in range((count+1)//2)]
    odd = [sum(h*a1[q+j] for j, h in enumerate(h0))
           + sum(h*a0[q+j+1] for j, h in enumerate(h1))
           for q in range(count//2)]
    return [even[n//2] if n % 2 == 0 else odd[n//2] for n in range(count)]


def compute():
    signal = signed_even_euler(16)
    assert signal[:8] == [1, -1, 5, -61, 1385, -50521, 2702765, -199360981]
    direct, split = direct_filter(signal, TAPS), split_filter(signal, TAPS)
    assert direct == split
    assert direct[:4] == [-43, 1191, -46239, 2548371]
    even, odd = signal[::2], signal[1::2]
    rows = []
    for q in range(2):
        even_part = even[q]+3*even[q+1]
        odd_part = -2*odd[q]+odd[q+1]
        assert even_part+odd_part == direct[2*q]
        rows.append(dict(index=2*q, phase='even', first=even_part, second=odd_part,
                         output=direct[2*q]))
        even_part = -2*even[q+1]+even[q+2]
        odd_part = odd[q]+3*odd[q+1]
        assert even_part+odd_part == direct[2*q+1]
        rows.append(dict(index=2*q+1, phase='odd', first=even_part, second=odd_part,
                         output=direct[2*q+1]))
    missing_advance = (-2*even[0]+even[1])+(odd[0]+3*odd[1])
    assert missing_advance == -181 and direct[1] == 1191
    comparisons = 0
    for length in range(25):
        signals = (signal[:length] if length <= 16 else signed_even_euler(length),
                   [1]*length, [(-1)**n for n in range(length)], list(range(length)))
        for values in signals:
            for taps in TEST_FILTERS:
                assert split_filter(values, taps) == direct_filter(values, taps), (length, taps)
                comparisons += 1
    impulse_comparisons = 0
    for length in range(1, 13):
        for position in range(length):
            values = [int(n == position) for n in range(length)]
            for taps in TEST_FILTERS:
                assert split_filter(values, taps) == direct_filter(values, taps), (length, position, taps)
                impulse_comparisons += 1
    for implementation in (direct_filter, split_filter):
        try:
            implementation([1, 2], ())
        except ValueError:
            pass
        else:
            raise AssertionError('An empty tap list was accepted')
    return dict(status='PASS', convention='Forward shift S a(n)=a(n+1); complete finite windows only',
                input=signal, taps=list(TAPS), even_taps=list(TAPS[::2]), odd_taps=list(TAPS[1::2]),
                direct=direct, polyphase=split, worked_rows=rows,
                missing_advance=dict(incorrect=missing_advance, correct=direct[1]),
                finite_checks=dict(signal_comparisons=comparisons, impulse_comparisons=impulse_comparisons,
                                   prefix_lengths=[0, 24], impulse_lengths=[1, 12],
                                   filters=[list(t) for t in TEST_FILTERS], empty_filter_rejected=True),
                scope='Exact finite comparisons and the displayed arithmetic. The general phase law is derived in the worked page; these tests are not its proof.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = compute()
    if args.output:
        if args.output.exists():
            raise FileExistsError('Choose a new result file')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Even taps: 1, 3')
    print('Odd taps: -2, 1')
    for label, key in (('Direct outputs', 'direct'), ('Polyphase outputs', 'polyphase')):
        print(label+': '+', '.join(map(str, report[key][:4])))
    print('Missing-advance control: -181 (correct: 1191)')
    print('Finite comparisons: 600 signal cases and 468 impulse cases')
    print('PASS: exact polyphase/tap split')


if __name__ == '__main__':
    main()
