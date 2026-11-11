"""Readable, source-bound diagrams for the Smith research reading.

Coordinates describe presentation only. Component connections and values follow
the retained archive; displayed decimal component values are rounded labels.
"""
from __future__ import annotations

import html
import math
import re

INK = '#183831'
MUTED = '#4c625b'
GREEN = '#126f61'
BLUE = '#315f99'
RED = '#a63c48'
LINE = '#dbe5e0'
PALE = '#edf5f1'

PAIR_MINORS = [
    ('1–2', '12397', '1036800'),
    ('1–3', '53067', '2560000'),
    ('2–3', '343', '320000'),
]
FULL_DETERMINANT = ('−3981887', '82944000000')


def esc(value):
    return html.escape(str(value), quote=True)


def label(x, y, value, size=24, *, color=INK, weight=400, anchor='start'):
    markup = re.sub(r'([Rz])_([ABGH])',
                    lambda match: match[1]+'<tspan baseline-shift="sub" font-size="75%">'+match[2]+'</tspan>',
                    esc(value))
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
            f'style="font-size:{size}px;font-weight:{weight};fill:{color}">{markup}</text>')


def wire(x1, y1, x2, y2, color=INK, width=2.6):
    return f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="{width}"/>'


def route(points, color=INK, width=2.6):
    return (f'<polyline points="{" ".join(f"{x},{y}" for x, y in points)}" '
            f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')


def box(x, y, width, height, fill='white', stroke=LINE, radius=8):
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{radius}" fill="{fill}" stroke="{stroke}"/>')


def node(x, y, number, *, port=False):
    body = (f'<circle cx="{x}" cy="{y}" r="{19 if port else 17}" fill="white" '
            f'stroke="{INK}" stroke-width="2.4"/>')
    body += label(x, y + 7, number, 22, weight=650, anchor='middle')
    return f'<g data-node="{number}" data-x="{x}" data-y="{y}">{body}</g>'


def part(x1, y1, x2, y2, kind, name, endpoints):
    """IEC resistor, coil or capacitor; electrical endpoints are explicit."""
    length = math.hypot(x2 - x1, y2 - y1)
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    mid = length / 2
    color = {'R': MUTED, 'L': GREEN, 'C': BLUE}[kind]
    body = wire(0, 0, mid - 25, 0, color) + wire(mid + 25, 0, length, 0, color)
    if kind == 'R':
        body += f'<rect x="{mid-25}" y="-9" width="50" height="18" fill="white" stroke="{color}" stroke-width="2.6"/>'
    elif kind == 'L':
        body += f'<path d="M{mid-25},0 ' + ' '.join('a6.25,10 0 0 1 12.5,0' for _ in range(4)) + f'" fill="none" stroke="{color}" stroke-width="2.8"/>'
    else:
        body += wire(mid - 25, 0, mid - 6, 0, color) + wire(mid + 6, 0, mid + 25, 0, color)
        body += wire(mid - 6, -19, mid - 6, 19, color, 3) + wire(mid + 6, -19, mid + 6, 19, color, 3)
    return (f'<g data-component="{esc(name)}" data-kind="{kind}" data-endpoints="{esc(endpoints)}">'
            f'<g transform="translate({x1},{y1}) rotate({angle})">{body}</g></g>')


def fraction(x, y, numerator, denominator, *, size=25, color=INK):
    width = max(len(numerator), len(denominator)) * size * .62 + 14
    return (label(x, y, numerator, size, color=color, anchor='middle')
            + wire(x - width / 2, y + 9, x + width / 2, y + 9, color, 1.3)
            + label(x, y + size + 16, denominator, size, color=color, anchor='middle'))


def values_table(x, y, width, rows, *, row_height=48, size=23):
    body = ''
    for index, (name, value) in enumerate(rows):
        top = y + index * row_height
        body += wire(x, top, x + width, top, LINE, 1)
        body += label(x + 4, top + 32, name, size, weight=600)
        body += label(x + width - 4, top + 32, value, size, anchor='end')
    return body


def document(title, description, content, width, height):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{esc(title)}</title><desc id="desc">{esc(description)}</desc>'
            '<style>text{font-family:Arial,Helvetica,sans-serif;font-variant-numeric:tabular-nums}'
            'path,polyline{stroke-linecap:round;stroke-linejoin:round}</style>'
            '<rect width="100%" height="100%" fill="white"/>' + content + '</svg>\n')


def header(kicker, title, mobile=False, second_line=None):
    x = 24 if mobile else 36
    body = label(x, 36, kicker, 21 if mobile else 16, color=GREEN, weight=700)
    body += label(x, 77, title, 29 if mobile else 30, weight=650)
    if second_line:
        body += label(x, 114, second_line, 29 if mobile else 25, weight=650)
    return body


def pairwise_obstruction(mobile=False):
    """All three edges are distinct, rather than superimposed on one line."""
    if mobile:
        body = header('GLOBAL PICK COMPATIBILITY', 'Three passing pairs.', True, 'One incompatible triple.')
        positions = {1: (200, 185), 2: (62, 384), 3: (338, 384)}
        chips = {(1, 2): (116, 285), (1, 3): (284, 285), (2, 3): (200, 384)}
    else:
        body = header('GLOBAL PICK COMPATIBILITY', 'Pairwise tests pass. The joint test fails.')
        positions = {1: (246, 164), 2: (82, 402), 3: (410, 402)}
        chips = {(1, 2): (148, 281), (1, 3): (344, 281), (2, 3): (246, 402)}
    for u, v in [(1, 2), (1, 3), (2, 3)]:
        body += f'<g data-pair="{u},{v}">' + wire(*positions[u], *positions[v], GREEN, 3.4) + '</g>'
        cx, cy = chips[(u, v)]
        body += box(cx - 39, cy - 20, 78, 40, PALE, '#c3d9ce', 20)
        body += label(cx, cy + 8, f'{u}–{v}', 24, color=GREEN, weight=650, anchor='middle')
    for number, (x, y) in positions.items():
        body += f'<g data-node="{number}" data-x="{x}" data-y="{y}">'
        body += f'<circle cx="{x}" cy="{y}" r="23" fill="{GREEN}"/>'
        body += label(x, y + 9, number, 27, color='white', weight=650, anchor='middle') + '</g>'
    if mobile:
        body += label(200, 443, 'Measured frequencies: s = 1, 2, 3', 22, color=MUTED, anchor='middle')
        body += label(24, 496, 'PAIR TESTS · ALL POSITIVE', 20, color=GREEN, weight=700)
        for index, (pair, numerator, denominator) in enumerate(PAIR_MINORS):
            y = 525 + 80 * index
            body += wire(24, y - 10, 376, y - 10, LINE, 1)
            body += label(32, y + 28, pair, 26, weight=650)
            body += fraction(252, y + 5, numerator, denominator, size=25, color=GREEN)
        body += box(24, 783, 352, 176, '#fbf0f1', '#e5c6ca')
        body += label(200, 818, 'JOINT TEST · NEGATIVE', 20, color=RED, weight=700, anchor='middle')
        body += fraction(200, 864, *FULL_DETERMINANT, size=28, color=RED)
        body += label(24, 1003, 'No single passive interpolation', 23, weight=600)
        body += label(24, 1034, 'fits the complete triple.', 23, weight=600)
        body += label(24, 1080, 'Shown: positive coupling branch.', 20, color=MUTED)
        width, height = 400, 1104
    else:
        body += label(246, 465, 'Every pair is feasible', 25, color=GREEN, weight=600, anchor='middle')
        body += label(246, 497, 'Nodes: measured frequencies s = 1, 2, 3', 20, color=MUTED, anchor='middle')
        body += label(526, 137, 'PAIRWISE PRINCIPAL MINORS', 18, color=GREEN, weight=700)
        for index, (pair, numerator, denominator) in enumerate(PAIR_MINORS):
            y = 175 + 73 * index
            body += wire(526, y - 11, 958, y - 11, LINE, 1)
            body += label(542, y + 24, pair, 25, weight=650)
            body += fraction(806, y, numerator, denominator, size=24, color=GREEN)
        body += box(510, 400, 454, 142, '#fbf0f1', '#e5c6ca')
        body += label(737, 431, 'FULL 3 × 3 DETERMINANT < 0', 18, color=RED, weight=700, anchor='middle')
        body += fraction(737, 473, *FULL_DETERMINANT, size=26, color=RED)
        body += label(36, 587, 'No single passive interpolation fits all three measurements.', 23, weight=600)
        body += label(36, 622, 'The displayed determinants use the all-positive coupling branch.', 19, color=MUTED)
        width, height = 1000, 650
    return document('Pairwise feasibility does not imply joint Pick feasibility',
                    'Three distinct edges represent positive two-node principal minors. The full three-node Pick determinant is negative. Exact values are shown for the all-positive coupling branch.', body, width, height)


def series_realization(mobile=False, four_state=False):
    """Series-connected parallel networks; reflow preserves each connection."""
    title = 'Four-reactive rational circuit' if four_state else 'Three-reactive passive circuit'
    body = header('TRANSFORMER-FREE REALIZATION', title, mobile)
    if four_state:
        rows = [('Lₜ', '48 / 35'), ('Cₜ', '35 / 48'), ('Rₚ', '1'),
                ('Rₛ', '25 / 24'), ('Lₛ', '35 / 48'), ('Cₛ', '48 / 35')]
        first = [('L', 'Lₜ'), ('C', 'Cₜ')]
        second = [[('R', 'Rₚ')], [('R', 'Rₛ'), ('L', 'Lₛ'), ('C', 'Cₛ')]]
    else:
        rows = [('r₁', '≈ 8.3725'), ('ℓ₁', '≈ 1.4191'), ('rₛ', '≈ 0.6275'),
                ('rₚ', '≈ 0.3761'), ('rℓ', '≈ 0.0437'), ('ℓ₂', '≈ 0.8668'), ('c', '≈ 2.5321')]
        first = [('R', 'r₁'), ('L', 'ℓ₁')]
        second = [[('R', 'rₚ')], [('R', 'rℓ'), ('L', 'ℓ₂')], [('C', 'c')]]
    if mobile:
        center, top, bottom = 220, 151, 344
        body += label(220, 127, '+', 25, weight=650, anchor='middle')
        for x, (kind, name) in zip([125, 315], first):
            body += wire(center, top, x, top) + wire(x, bottom, center, bottom)
            body += part(x, top, x, bottom, kind, name, 'input,A')
            body += label(x - 27 if x < center else x + 27, 255, name, 24, anchor='end' if x < center else 'start')
        body += label(24, 386, 'Parallel LC tank' if four_state else 'Block A: r₁ ∥ ℓ₁', 23, weight=600)
        next_top = 468 if four_state else 528
        if four_state:
            body += wire(center, bottom, center, next_top)
        else:
            body += part(center, bottom, center, next_top, 'R', 'rₛ', 'A,B')
            body += label(center + 35, 446, 'rₛ', 24)
        end = next_top + (328 if four_state else 270)
        xs = [112, 328] if four_state else [80, 220, 360]
        for branch_index, (x, branch) in enumerate(zip(xs, second)):
            body += wire(center, next_top, x, next_top) + wire(x, end, center, end)
            for index, (kind, name) in enumerate(branch):
                a = next_top + (end-next_top) * index / len(branch)
                b = next_top + (end-next_top) * (index+1) / len(branch)
                left = 'B' if index == 0 else f'B{branch_index}_{index}'
                right = 'return' if index == len(branch)-1 else f'B{branch_index}_{index+1}'
                body += part(x, a, x, b, kind, name, left+','+right)
                body += label(x + (31 if x <= center else -31), (a+b)/2+8, name, 23,
                              anchor='start' if x <= center else 'end')
        body += wire(center, end, center, end + 36)
        body += label(center, end + 68, '−', 25, weight=650, anchor='middle')
        body += label(24, end + 108, 'Normalized component values', 23, weight=600)
        table_y = end + 128
        body += values_table(24, table_y, 392, rows, size=24)
        foot = table_y + 48 * len(rows) + 30
        if four_state:
            body += label(24, foot, 'z_H(s) = 1 + 48s/[35(s²+1)]', 22)
            body += label(24, foot+34, '− 48s/[7(5s²+14s+5)]', 22)
            body += label(24, foot+79, 'Exact rationals; normalized to Z₀.', 21, color=MUTED)
        else:
            body += label(24, foot, 'r = R/Z₀,  ℓ = L/(Z₀τ)', 22)
            body += label(24, foot+34, 'c = C Z₀/τ', 22)
            body += label(24, foot+79, 'Decimal labels are rounded.', 21, color=MUTED)
        body += label(24, foot+110, 'Blocks connect in series.', 21, color=MUTED)
        width, height = 440, foot+138
    else:
        x0, x1, yc = 85, 370, 260
        for y, (kind, name) in zip([173, 347], first):
            body += wire(x0, yc, x0, y) + wire(x1, y, x1, yc)
            body += part(x0, y, x1, y, kind, name, 'input,A')
            body += label((x0+x1)/2, y-25 if y<yc else y+42, name, 25, anchor='middle')
        x2, x3 = 535, 920
        body += wire(40, yc, x0, yc) + wire(x3, yc, 965, yc)
        body += label(39, yc-24, '+', 27, weight=650) + label(952, yc-24, '−', 27, weight=650)
        if four_state:
            body += wire(x1, yc, x2, yc)
        else:
            body += part(x1, yc, x2, yc, 'R', 'rₛ', 'A,B')
            body += label((x1+x2)/2, yc-29, 'rₛ', 25, anchor='middle')
        ys = [173, 347] if four_state else [145, 260, 375]
        for branch_index, (y, branch) in enumerate(zip(ys, second)):
            body += wire(x2, yc, x2, y) + wire(x3, y, x3, yc)
            for index, (kind, name) in enumerate(branch):
                a = x2 + (x3-x2)*index/len(branch)
                b = x2 + (x3-x2)*(index+1)/len(branch)
                left = 'B' if index == 0 else f'B{branch_index}_{index}'
                right = 'return' if index == len(branch)-1 else f'B{branch_index}_{index+1}'
                body += part(a, y, b, y, kind, name, left+','+right)
                body += label((a+b)/2, y-26 if y<yc else y+42, name, 25, anchor='middle')
        body += label(227, 443, 'Parallel LC tank' if four_state else 'Block A: r₁ ∥ ℓ₁', 23, weight=600, anchor='middle')
        body += label(727, 443, 'Rₚ ∥ (Rₛ + Lₛ + Cₛ)' if four_state else 'Block B: rₚ ∥ (rℓ + ℓ₂) ∥ c', 23, weight=600, anchor='middle')
        for index, (name, value) in enumerate(rows):
            x = 40 + (index % 4)*243
            y = 508 + (index // 4)*46
            body += label(x, y, name + '  ' + value, 22)
        body += wire(36, 470, 964, 470, LINE, 1)
        if four_state:
            body += label(36, 607, 'z_H(s) = 1 + 48s/[35(s²+1)] − 48s/[7(5s²+14s+5)]', 23)
            body += label(36, 649, 'Normalized to Z₀. All component values are exact positive rationals.', 20, color=MUTED)
        else:
            body += label(36, 607, 'r = R/Z₀  ·  ℓ = L/(Z₀τ)  ·  c = C Z₀/τ', 23)
            body += label(36, 649, 'Decimal labels are rounded. Blocks A, rₛ and B connect in series.', 20, color=MUTED)
        width, height = 1000, 679
    return document(title, 'Series connection of the indicated parallel component groups. Component symbols and normalized values are listed explicitly.', body, width, height)


def triangle_diagram(capacitor_at_input=False):
    """Three nodes, with parallel branches separated by routing."""
    body = ''
    if capacitor_at_input:
        ytop, ybottom = 142, 492
        body += part(80, ytop, 340, ytop, 'R', 'R_A', '1,2')
        body += label(210, ytop-28, 'R_A', 24, anchor='middle')
        branches = [(45, 'R', 'R_G', '1,0'), (145, 'C', 'C', '1,0'),
                    (285, 'R', 'R_B', '2,0'), (385, 'L', 'L', '2,0')]
        for x, kind, name, endpoints in branches:
            source = 80 if endpoints.startswith('1') else 340
            body += wire(source, ytop, x, ytop)
            body += part(x, ytop, x, ybottom, kind, name, endpoints)
            label_x, label_y = {'R_G':(80,302), 'C':(174,353), 'R_B':(320,302), 'L':(408,353)}[name]
            body += label(label_x,label_y,name,24)
        body += wire(45, ybottom, 385, ybottom)
        body += node(80, ytop, 1, port=True) + node(340, ytop, 2) + node(220, ybottom, 0)
    else:
        ytop, ybottom = 280, 546
        for y, kind, name in [(112, 'R', 'R_A'), (201, 'L', 'L')]:
            body += wire(80, ytop, 80, y) + wire(340, y, 340, ytop)
            body += part(80, y, 340, y, kind, name, '1,2')
            body += label(210, y-26, name, 24, anchor='middle')
        body += part(80, ytop, 80, ybottom, 'R', 'R_G', '1,0')
        body += label(113, 423, 'R_G', 24)
        for x, kind, name in [(278, 'R', 'R_B'), (390, 'C', 'C')]:
            body += wire(340, ytop, x, ytop) + part(x, ytop, x, ybottom, kind, name, '2,0')
            body += label(x-27, 423, name, 24, anchor='end')
        body += wire(80, ybottom, 390, ybottom)
        body += node(80, ytop, 1, port=True) + node(340, ytop, 2) + node(220, ybottom, 0)
    return body, ybottom


def exact_triangle(mobile=False, middle=False):
    title = 'The complex-pole-pair circuit' if middle else 'The exact two-reactive circuit'
    rows = ([('R_G', '1'), ('R_A', '≈ 0.09556'), ('R_B', '≈ 0.05027'), ('L', '≈ 0.075328'), ('C', '≈ 9.50264')]
            if middle else [('R_A', '≈ 2.4584'), ('R_G', '≈ 20.9333'), ('R_B', '≈ 3.2330'), ('L', '≈ 0.64517'), ('C', '≈ 5.25071')])
    diagram, end = triangle_diagram(middle)
    body = header('THREE RESISTORS · ONE L · ONE C',
                  ('Complex-pole-pair circuit' if middle else 'One L. One C. Three R.') if mobile else title, mobile)
    if mobile:
        body += '<g transform="translate(0,80)">' + diagram + '</g>'
        table = end+170
        body += label(24, table-30, 'Normalized values', 24, weight=600)
        body += values_table(24, table, 392, rows, size=24)
        body += label(24, table+48*len(rows)+40, '1: input · 0: return', 22, color=MUTED)
        body += label(24, table+48*len(rows)+72, 'Decimal labels are rounded.', 21, color=MUTED)
        width, height = 440, table+48*len(rows)+98
    else:
        body += '<g transform="translate(30,65) scale(1.06)">' + diagram + '</g>'
        body += label(600, 173, 'NORMALIZED VALUES', 18, color=GREEN, weight=700)
        body += values_table(600, 199, 350, rows, row_height=61, size=25)
        body += label(600, 559, '1: input · 0: return', 22, color=MUTED)
        body += label(600, 594, 'Decimal labels are rounded.', 20, color=MUTED)
        width, height = 1000, max(680, int(end*1.06+120))
    return document(title, 'An explicitly connected three-node circuit, with one inductor, one capacitor and three resistors. Parallel branches are separated and normalized component values are listed.', body, width, height)


def endpoint_graph_panel(survives=False):
    """Same six reactive branches as the source, including isolated port 1."""
    body = ''
    # Paired branches are offset, with real L/C symbols instead of color-only arcs.
    for index, x in enumerate([75, 220, 365]):
        number = index+2
        body += part(x-23, 102, x-23, 310, 'L', f'L_0{number}', f'0,{number}')
        body += wire(x, 102, x-23, 102) + wire(x-23, 310, x-23, 370)
        if not (survives and number == 4):
            body += part(x+23, 102, x+23, 310, 'C', f'C_0{number}', f'0,{number}')
            body += wire(x, 102, x+23, 102) + wire(x+23, 310, x+23, 370)
        body += node(x, 102, number)
    body += wire(52, 370, 388, 370) + wire(220, 370, 220, 400)
    body += node(220, 400, 0)
    if survives:
        body += wire(365, 102, 416, 102) + wire(416, 102, 416, 225)
        body += part(416, 225, 416, 475, 'C', 'C_14', '1,4')
        body += wire(416, 475, 300, 475) + node(300, 475, 1, port=True)
    else:
        body += node(365, 475, 1, port=True)
    body += label(220, 444, 'ground', 22, color=MUTED, anchor='middle')
    body += label(300 if survives else 365, 519, 'port', 22, color=MUTED, anchor='middle')
    return body


def endpoint_graphs(mobile=False):
    body = header('DC ENDPOINT FILTER', 'Which capacitor voltages can survive?', mobile)
    if mobile:
        # Break the long title without shrinking the mathematical labels.
        body = header('DC ENDPOINT FILTER', 'Capacitor voltage', True, 'must survive the L short.')
        for y, survives, heading in [(158, False, 'REJECTED BY THIS FILTER'), (805, True, 'PASSES THIS FILTER ONLY')]:
            body += label(24, y, heading, 21, color=GREEN if survives else RED, weight=700)
            body += '<g transform="translate(0,'+str(y+10)+')">' + endpoint_graph_panel(survives) + '</g>'
        body += label(24, 1398, 'At DC, each inductor is a short.', 22)
        body += label(24, 1430, 'First: every capacitor is shorted.', 22)
        body += label(24, 1462, 'Second: C₁₄ can retain voltage.', 22)
        body += label(24, 1512, 'A necessary graph test only;', 21, color=MUTED)
        body += label(24, 1542, 'component feasibility remains.', 21, color=MUTED)
        body += label(24, 1590, 'Reactive branches only;', 21, color=MUTED)
        body += label(24, 1621, 'resistor placements are omitted.', 21, color=MUTED)
        width, height = 440, 1650
    else:
        for x, survives, heading in [(30, False, 'REJECTED BY THIS FILTER'), (530, True, 'PASSES THIS FILTER ONLY')]:
            body += label(x+4, 135, heading, 20, color=GREEN if survives else RED, weight=700)
            body += '<g transform="translate('+str(x)+',155)">' + endpoint_graph_panel(survives) + '</g>'
        body += wire(500, 120, 500, 691, LINE, 1)
        body += label(36, 731, 'At DC, inductors short. On the left, every capacitor is shorted by an inductor path.', 21)
        body += label(36, 769, 'On the right, C₁₄ can retain voltage. Passing this necessary test does not prove feasibility.', 20, color=MUTED)
        body += label(36, 810, 'Reactive branches only; resistor placements are omitted.', 20, color=MUTED)
        width, height = 1000, 840
    return document('Necessary capacitor-voltage endpoint test', 'Both graphs have inductors on 02, 03, 04. The rejected graph has capacitors on those same pairs; the other has capacitors on 02, 03, 14. Resistors are omitted from this reactive placement test.', body, width, height)


def split_status(mobile=False):
    body = header('SERIES POLE-PAIR EXTRACTION', 'Two realized sections. One unresolved section.', mobile)
    if mobile:
        body = header('SERIES POLE-PAIR EXTRACTION', 'Two realized sections.', True, 'One unresolved section.')
    cards = [
        ('01', 'Real pole pair', GREEN, 'REALIZED', ['1 inductor + 1 capacitor', '3 positive resistors']),
        ('02', 'Lower complex pair', GREEN, 'REALIZED', ['1 inductor + 1 capacitor', '3 positive resistors']),
        ('03', 'Upper complex pair', RED, 'UNRESOLVED', ['Positive-real, nonregular', 'No realization established']),
    ]
    for index, (number, name, color, state, details) in enumerate(cards):
        x = 24 if mobile else 36+index*321
        y = 155+index*274 if mobile else 142
        w = 392 if mobile else 286
        body += box(x, y, w, 230, PALE if color == GREEN else '#fbf0f1')
        body += label(x+20, y+35, number+' · '+state, 21 if mobile else 17, color=color, weight=700)
        body += label(x+20, y+83, name, 26 if mobile else 24, weight=650)
        body += label(x+20, y+137, details[0], 24 if mobile else 20)
        body += label(x+20, y+179, details[1], 24 if mobile else 20)
        if index < 2:
            body += label(220 if mobile else x+w+18, y+263 if mobile else y+124, '+', 30, color=MUTED, anchor='middle')
    if mobile:
        body += label(24, 1021, 'A six-reactive transformer-free', 23, weight=600)
        body += label(24, 1054, 'realization remains unresolved.', 23, weight=600)
        width, height = 440, 1085
    else:
        body += label(36, 434, 'A positive-real residual does not supply the missing circuit.', 25, weight=600)
        body += label(36, 479, 'The complete six-reactive transformer-free realization remains unresolved.', 22, color=MUTED)
        width, height = 1000, 516
    return document('Status of the three pole-pair sections', 'The real and lower complex pole-pair sections have exact two-reactive circuits. The upper complex section is positive-real and nonregular, with no realization established in this decomposition.', body, width, height)


def cubic_graph(mobile=False):
    body = header('ALGEBRAICALLY CERTIFIED CIRCUIT', 'A cubic with three reactive elements', mobile)
    if mobile:
        body = header('CERTIFIED CUBIC CIRCUIT', 'Three reactive elements.', True, 'Seven components in total.')
    # A planar diamond embedding of K4 minus the 0–1 edge. Parallel
    # inductors are routed outside the diamond, so no crossing is a junction.
    points = {0: (55, 253), 1: (385, 253), 2: (220, 105), 3: (220, 401)}
    diagram = ''
    for u, v, kind, name, lx, ly in [
        (0, 2, 'R', 'R₀₂', 108, 153), (0, 3, 'R', 'R₀₃', 153, 310),
        (1, 2, 'R', 'R₁₂', 319, 153), (2, 3, 'R', 'R₂₃', 275, 262),
        (1, 3, 'C', 'C₁₃', 345, 373),
    ]:
        diagram += part(*points[u], *points[v], kind, name, f'{u},{v}')
        diagram += label(lx, ly, name, 23, anchor='middle')
    diagram += wire(55,253,29,316,GREEN) + wire(112,456,220,401,GREEN)
    diagram += part(29,316,112,456,'L','L₀₃','0,3')
    diagram += label(27, 477, 'L₀₃', 23)
    diagram += wire(385,253,411,190,GREEN) + wire(328,50,220,105,GREEN)
    diagram += part(411,190,328,50,'L','L₁₂','1,2')
    diagram += label(350, 58, 'L₁₂', 23)
    for number, point in points.items():
        diagram += node(*point, number, port=number in (0,1))
    rows = [('R₀₂', '≈ 8.5046'), ('R₀₃', '≈ 2.9646'), ('R₁₂', '≈ 0.038845'),
            ('R₂₃', '≈ 0.075882'), ('L₀₃', '≈ 0.64514'), ('L₁₂', '≈ 0.06328'), ('C₁₃', '≈ 10.204')]
    if mobile:
        body += '<g transform="translate(0,135)">' + diagram + '</g>'
        body += label(24, 655, 'Normalized component values', 23, weight=600)
        body += values_table(24, 678, 392, rows, size=24)
        body += label(24, 1058, '0: ground · 1: input', 22, color=MUTED)
        body += label(24, 1091, 'Decimal labels are rounded.', 21, color=MUTED)
        width, height = 440, 1120
    else:
        body += '<g transform="translate(20,112) scale(1.22)">' + diagram + '</g>'
        body += label(609, 147, 'NORMALIZED COMPONENT VALUES', 18, color=GREEN, weight=700)
        body += values_table(609, 172, 340, rows, row_height=55, size=24)
        body += label(609, 605, '0: ground · 1: input', 22, color=MUTED)
        body += label(36, 735, 'Four resistors, two inductors and one capacitor. Exact values are algebraic; labels are rounded.', 20, color=MUTED)
        width, height = 1000, 764
    return document('Exact cubic extraction component graph', 'Resistors on 02, 03, 12, 23; inductors on 03, 12; capacitor on 13. A planar layout and separated parallel branches make every connection explicit.', body, width, height)


def drawings():
    return {
        '08_frequency_obstruction': (pairwise_obstruction, 'reproduction/earlier_core/smith_chart_extended.py'),
        '11_exact_passive_rlc_schematic': (series_realization, 'figures/11_exact_passive_rlc_schematic.svg'),
        '18_four_state_rlc_topology': (lambda mobile=False: series_realization(mobile, four_state=True), 'figures/18_four_state_rlc_topology.svg'),
        '26_reactive_endpoint_graph_examples': (endpoint_graphs, 'reproduction/six_state/smith_q6_invariant_figures.py'),
        '27_exact_two_state_triangle': (exact_triangle, 'figures/27_exact_two_state_triangle.svg'),
        '30_middle_pole_rlc_triangle': (lambda mobile=False: exact_triangle(mobile, middle=True), 'figures/30_middle_pole_rlc_triangle.svg'),
        '31_series_split_status': (split_status, 'figures/31_series_split_status.svg'),
        '37_cubic_transformerfree_schematic': (cubic_graph, 'reproduction/exact_cubic_continuation/make_cubic_figures.py'),
    }
