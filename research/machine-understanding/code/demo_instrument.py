#!/usr/bin/env python3
"""Print the complete analytical trace from Appendix A. No model/API is used."""
from __future__ import annotations
from finite_checks import step, total

def main() -> None:
    state=(1,3,2)
    print('Arithmetic: modulo 5. State is (a,b,c). Display is a+b.')
    print(f'Initial state: {state}; display={total(state)}; base record={(total(state),state[1])}')
    for u in ('H','W'):
        state=step(state,u)
        print(f'After {u}: state={state}; display={total(state)}; base record={(total(state),state[1])}')
    old_display=total(state); b=state[1]
    print('The base record does not determine the next J display: c was not retained.')
    state=step(state,'J');new_display=total(state)
    recovered=((new_display-b)%5,b,(new_display-old_display)%5)
    if recovered!=state:raise AssertionError('Post-intervention reconstruction failed')
    print(f'After J: display={new_display}; recovered post-operation state={recovered}')
    print(f'Extended record (s,b,c)={(new_display,b,recovered[2])}')
if __name__=='__main__':main()
