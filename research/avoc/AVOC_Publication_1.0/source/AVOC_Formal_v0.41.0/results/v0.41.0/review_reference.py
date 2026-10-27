#!/usr/bin/env python3
"""Independent bounded dictionary-based lifecycle reference; not a universal proof."""
from pathlib import Path
import hashlib, itertools, json, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import observation_recorder as implementation

def reference(commands):
    registry = {}
    completion_order = []
    for index, command in enumerate(commands):
        tag, op, key, *outcome = command
        prior = registry.get(op)
        if tag == 'begin':
            if prior is None:
                registry[op] = (key, None)
            elif prior[0] != key:
                return dict(status='rejected', index=index, error='command_rejected')
        else:
            if prior is None or prior[0] != key:
                return dict(status='rejected', index=index, error='command_rejected')
            if prior[1] is None:
                registry[op] = (key, outcome[0])
                completion_order.append(op)
            elif prior[1] != outcome[0]:
                return dict(status='rejected', index=index, error='command_rejected')
    pending = [[op, key] for op, (key, outcome) in registry.items() if outcome is None]
    terminal = [[op, registry[op][0], registry[op][1]] for op in completion_order]
    return dict(status='recorded', pending=pending, log=terminal, ready=not pending)

def main():
    alphabet = [c for op in range(2) for key in range(2) for c in
        [['begin',op,key], ['finish',op,key,'success'],
         ['finish',op,key,'rejection'], ['finish',op,key,'fault']]]
    counts = {'words':0, 'recorded':0, 'rejected':0, 'ready':0}
    for length in range(5):
        for word in itertools.product(alphabet, repeat=length):
            commands = list(word)
            expected = reference(commands)
            actual = implementation.evaluate(['observation-recorder-v1', commands])
            if actual != expected:
                raise AssertionError({'commands':commands,'expected':expected,'actual':actual})
            counts['words'] += 1
            counts[actual['status']] += 1
            counts['ready'] += actual.get('ready') is True
    result = {'status':'passed','domain':{'ids':[0,1],'keys':[0,1],
        'terminal_outcomes':['success','rejection','fault'],'lengths':[0,1,2,3,4],
        'alphabet_size':16,'exhaustive':True},'counts':counts,
        'scope':'Independent dictionary model versus Python lifecycle reducer; bounded comparison only.',
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__),ROOT/'tools/observation_recorder.py']}}
    output = ROOT/'results/v0.41.0/review_reference.json'
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2))
if __name__ == '__main__':
    main()
