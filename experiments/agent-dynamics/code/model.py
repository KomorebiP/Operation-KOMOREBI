"""Exact, inspectable two-agent dynamics. No neural model or external service.

A source is at j in {0,...,7}. A bit sensor reports ((j >> q) & 1) XOR theta.
The agents receive reports, never j. The renderer alone displays world truth.
A scripted regime change is followed by an explicitly supplied reset rule.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from fractions import Fraction
from math import log2
from typing import Iterable
import json

Case = tuple[int, int]  # (source location, sensor orientation)
ALL_CASES: frozenset[Case] = frozenset((j, theta) for j in range(8) for theta in range(2))


def report(case: Case, kind: str, bit: int | None = None) -> int:
    j, theta = case
    if kind == 'calibration':
        return theta
    if kind != 'bit' or bit not in (0, 1, 2):
        raise ValueError('A bit observation requires bit=0, 1, or 2.')
    return ((j >> bit) & 1) ^ theta


@dataclass(frozen=True)
class Receipt:
    uid: str
    epoch: int
    kind: str
    bit: int | None
    value: int
    issuer: str

    def __post_init__(self) -> None:
        if self.value not in (0, 1) or self.epoch < 0:
            raise ValueError('Receipt values must be binary and epochs nonnegative.')
        report((0, 0), self.kind, self.bit)

    def compatible(self, case: Case) -> bool:
        return report(case, self.kind, self.bit) == self.value


@dataclass
class Agent:
    name: str
    epoch: int = 0
    cases: frozenset[Case] = field(default_factory=lambda: frozenset((j, 0) for j in range(8)))
    receipts: dict[str, Receipt] = field(default_factory=dict)
    archive: list[Receipt] = field(default_factory=list)
    resets: int = 0

    def reset(self, epoch: int) -> None:
        if epoch <= self.epoch:
            raise ValueError('A reset must advance the episode identifier.')
        self.archive.extend(self.receipts.values())
        self.receipts = {}
        self.cases = ALL_CASES
        self.epoch = epoch
        self.resets += 1

    def probability_one(self, kind: str, bit: int | None = None) -> Fraction:
        return Fraction(sum(report(c, kind, bit) for c in self.cases), len(self.cases))

    def observe(self, uid: str, kind: str, value: int, bit: int | None = None) -> dict:
        p_one = self.probability_one(kind, bit)
        r = Receipt(uid, self.epoch, kind, bit, value, self.name)
        candidates = frozenset(c for c in self.cases if r.compatible(c))
        surprise = not candidates
        if surprise:
            # Supplied failure response, not a learned policy. Both location and
            # sensor convention may have changed. Old evidence is archived.
            self.reset(self.epoch + 1)
            r = Receipt(uid, self.epoch, kind, bit, value, self.name)
            candidates = frozenset(c for c in self.cases if r.compatible(c))
        if not candidates:
            raise ValueError('Report lies outside even the expanded model family.')
        self.cases = candidates
        self.receipts[r.uid] = r
        return {'predicted_one': float(p_one), 'predicted_one_exact': str(p_one),
                'observed': value, 'surprise': surprise, 'receipt': asdict(r)}

    def receive(self, incoming: Iterable[Receipt], announced_epoch: int) -> None:
        """Reliable, honest transport is assumed, not inferred from a signature."""
        if announced_epoch < self.epoch:
            return
        if announced_epoch > self.epoch:
            self.reset(announced_epoch)
        for r in incoming:
            if r.epoch != self.epoch:
                continue
            if r.uid in self.receipts:
                if r != self.receipts[r.uid]:
                    raise ValueError('Conflicting contents for an existing receipt ID.')
                continue
            candidates = frozenset(c for c in self.cases if r.compatible(c))
            if not candidates:
                raise ValueError('Received evidence contradicts the active model.')
            self.cases = candidates
            self.receipts[r.uid] = r

    def snapshot(self) -> dict:
        n = len(self.cases)
        p = [Fraction(sum(c[0] == j for c in self.cases), n) for j in range(8)]
        locations = sorted({c[0] for c in self.cases})
        return {'name': self.name, 'epoch': self.epoch,
                'cases': [list(c) for c in sorted(self.cases)],
                'p': [float(v) for v in p], 'p_exact': [str(v) for v in p],
                'entropy': max(0.0, -sum(float(v) * log2(float(v)) for v in p if v)),
                'locations': locations, 'n_cases': n,
                'ready': len(locations) == 1, 'action': locations[0] if len(locations) == 1 else None,
                'receipt_ids': sorted(self.receipts), 'archive_size': len(self.archive),
                'resets': self.resets}


def run_story(target: int = 5) -> list[dict]:
    if target not in range(8):
        raise ValueError('Target must be in 0,...,7.')
    agents = {'A': Agent('A'), 'B': Agent('B')}
    theta = 0
    story: list[dict] = []
    spent = {'ordinary_queries': 0, 'calibration_queries': 0, 'message_bundles': 0, 'external_actions': 0}

    def save(title: str, detail: str, channel: str, active: str = '', observation: dict | None = None) -> None:
        story.append({'t': len(story), 'title': title, 'detail': detail,
                      'channel': channel, 'active': active, 'truth': {'target': target, 'theta': theta},
                      'A': agents['A'].snapshot(), 'B': agents['B'].snapshot(),
                      'observation': observation, 'events': dict(spent)})

    def see(who: str, bit: int | None, title: str, detail: str, kind: str = 'bit') -> None:
        value = report((target, theta), kind, bit)
        result = agents[who].observe(f'r{len(story):02d}', kind, value, bit)
        spent['ordinary_queries' if kind == 'bit' else 'calibration_queries'] += 1
        save(title.replace('{value}', str(value)), detail, 'observation', who, result)

    def send(src: str, dst: str, title: str, detail: str) -> None:
        agents[dst].receive(tuple(agents[src].receipts.values()), agents[src].epoch)
        spent['message_bundles'] += 1
        save(title, detail, 'message', src + '>' + dst)

    save('Two agents, one partially observed world',
         'Eight possible source locations. Each agent initially assumes the sensor orientation is zero.', 'start')
    see('A', 2, 'A reads the high bit: {value}',
        'An external sensor report filters A\'s internal possibilities. B has not received it.')
    see('B', 0, 'B reads the low bit: {value}',
        'Private observations produce different internal beliefs, even with the same reasoning rule.')
    # Exchange immutable snapshots so forwarding cannot manufacture new evidence.
    ar, br = tuple(agents['A'].receipts.values()), tuple(agents['B'].receipts.values())
    agents['A'].receive(br, 0)
    agents['B'].receive(ar, 0)
    spent['message_bundles'] += 2
    save('Exchange the receipts, not just the answers',
         'Both agents combine distinct evidence. Repeated receipt IDs are counted only once.', 'message', 'A<>B')
    see('A', 1, 'A reads the middle bit: {value}',
        'A now identifies the source under the current sensor model. B still has two candidates.')
    send('A', 'B', 'The final distinguishing report reaches B',
         'Both agents identify the same source. No change to their learning algorithm has occurred.')
    theta = 1
    save('The world changes before a new service request',
         'The sensor orientation flips. The agents receive no direct notification and still retain the old model.',
         'world', 'world')
    see('A', 2, 'A encounters an impossible report: {value}',
        'The old model assigned this report probability zero. A archives stale evidence and expands its candidate model.')
    send('A', 'B', 'A sends a model-reset notice and its new receipt',
         'B adopts the new episode boundary through an explicit trusted message, not hidden access to world truth.')
    see('B', 0, 'B reads the low bit in the changed world: {value}',
        'The new reading constrains source and orientation together; it does not identify either completely.')
    send('B', 'A', 'B shares the new low-bit evidence',
         'The message changes A\'s private state. It does not count as an additional independent sensor sample.')
    see('A', 1, 'A reads the middle bit: {value}',
        'All three ordinary bit reports still allow two source/orientation explanations.')
    send('A', 'B', 'Two coherent explanations remain for both agents',
         'The two locations require different actions. The action gate must wait despite complete ordinary bit coverage.')
    see('A', 2, 'Repeating a known reading does not resolve the ambiguity',
        'The deterministic repeat is predicted by both surviving models. More of this same evidence adds no distinction.')
    see('B', None, 'B uses the calibration channel: {value}',
        'A separately supplied reference reveals the sensor orientation. It costs two observation units.', 'calibration')
    send('B', 'A', 'Calibration evidence reaches A',
         'Both agents now have one compatible source. The new distinction arrived through a real information channel.')
    save('Check the action against every remaining possibility',
         'The supplied decision gate permits a command only when all compatible cases name the same location.',
         'check', 'A')
    if not agents['A'].snapshot()['ready']:
        raise RuntimeError('The final command lacks a unique supported location.')
    action = agents['A'].snapshot()['action']
    if action != target:
        raise RuntimeError('The verified action does not match world truth.')
    spent['external_actions'] += 1
    save(f'Command bay {action}; the world confirms service',
         'An internal decision crosses the boundary as an external action. The destination is correct in this finite model.',
         'action', 'A>world')
    return story


def controlled_access_cases(target: int = 5) -> dict:
    """Matched post-change evidence sets, not a claim about retrained agents."""
    theta = 1
    obs = {q: report((target, theta), 'bit', q) for q in range(3)}
    def filt(bits: tuple[int, ...], calibrated: bool) -> list[list[int]]:
        return [list(c) for c in sorted(ALL_CASES)
                if all(report(c, 'bit', q) == obs[q] for q in bits)
                and (not calibrated or c[1] == theta)]
    return {'All receipts shared': {'A': filt((0,1,2), True), 'B': filt((0,1,2), True)},
            'No messages': {'A': filt((1,2), False), 'B': filt((0,), True)},
            'No calibration': {'A': filt((0,1,2), False), 'B': filt((0,1,2), False)}}


def validate() -> dict:
    checks: list[dict] = []
    def check(label: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append({'check': label, 'passed': True})
    for target in range(8):
        story = run_story(target)
        check(f'{target}: 18 recorded states', len(story) == 18)
        for agent in ('A', 'B'):
            for s in story:
                p = [Fraction(v) for v in s[agent]['p_exact']]
                check(f'{target}/{agent}/{s["t"]}: exact normalized belief', sum(p) == 1)
                check(f'{target}/{agent}/{s["t"]}: nonnegative belief', all(v >= 0 for v in p))
            check(f'{target}/{agent}: first identification', story[5][agent]['locations'] == [target])
            check(f'{target}/{agent}: both post-change explanations',
                  {tuple(c) for c in story[12][agent]['cases']} == {(target,1), (target ^ 7,0)})
            check(f'{target}/{agent}: calibrated identification', story[15][agent]['locations'] == [target])
        check(f'{target}: contradiction localized at A', story[7]['observation']['surprise'])
        check(f'{target}: repeat leaves A unchanged', story[12]['A']['cases'] == story[13]['A']['cases'])
        check(f'{target}: exactly one issued action', story[-1]['events']['external_actions'] == 1)
        controls = controlled_access_cases(target)
        check(f'{target}: intact access gives one case each', all(len(c)==1 for c in controls['All receipts shared'].values()))
        check(f'{target}: no messages leaves four cases each', all(len(c)==4 for c in controls['No messages'].values()))
        check(f'{target}: no calibration leaves two cases each', all(len(c)==2 for c in controls['No calibration'].values()))
    a = Agent('A'); a.observe('test','bit',1,2)
    b = Agent('B'); b.receive(a.receipts.values(),0); before=b.snapshot()
    b.receive(a.receipts.values(),0)
    check('Forwarding the same receipt is idempotent', before == b.snapshot())
    x = run_story(5)
    check('Target-5 joint ambiguity is (2,0) or (5,1)', x[12]['A']['cases'] == [[2,0],[5,1]])
    check('A and B do not receive hidden flip immediately', x[6]['A']['epoch']==x[6]['B']['epoch']==0)
    check('Measured final event counts', x[-1]['events'] == {
        'ordinary_queries':7,'calibration_queries':1,'message_bundles':7,'external_actions':1})
    return {'status':'PASS', 'assertions':len(checks), 'checks':checks,
            'arithmetic':'exact finite sets and rational normalized probabilities; entropy rendered as floating point',
            'scope':'all eight source locations for this fixed 18-stage schedule and three controlled access contracts',
            'non_claims':['No neural activations or empirical AI introspection.',
                          'No learned acquisition policy or recursive optimizer.',
                          'No guarantee for arbitrary drift or corrupted communications.']}

if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
