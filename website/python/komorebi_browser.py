"""Display plots and offer result downloads in the Komorebi browser playground.

This module is supplied by the playground. It is not part of Komorebi Math.
"""
import base64
import io
import json
import re

_counts = {}
_total_bytes = 0
_sink = None


def _reset():
    global _counts, _total_bytes
    _counts = {}
    _total_bytes = 0


def _plain(value):
    if hasattr(value, 'tolist'):
        return _plain(value.tolist())
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _post(kind, **values):
    global _total_bytes
    count = _counts.get(kind, 0)+1
    if count > (6 if kind in {'plot', 'image'} else 8):
        raise ValueError('Too many figures or exports. Use a smaller run.')
    payload = json.dumps(dict(kind=kind, **values), allow_nan=False)
    size = len(payload.encode('utf-8'))
    if size > 2_000_000 or _total_bytes+size > 8_000_000:
        raise ValueError('Figure or export size limit reached. Use fewer samples.')
    _counts[kind] = count
    _total_bytes += size
    if _sink is not None:
        _sink(payload)
    else:
        from komorebi_host import emit
        emit(payload)


def show_plot(data, layout=None, *, description):
    """Show Plotly-style traces with a plain-language description.

    Supported traces: scatter, bar, heatmap, surface and scatter3d.
    NumPy arrays are converted to ordinary lists. All values must be finite.
    """
    data = _plain(data)
    if not isinstance(data, list) or not 1 <= len(data) <= 12:
        raise ValueError('Provide between 1 and 12 plot traces.')
    if any(t.get('type', 'scatter') not in {'scatter', 'bar', 'heatmap', 'surface', 'scatter3d'} for t in data):
        raise ValueError('Use scatter, bar, heatmap, surface or scatter3d traces.')
    points = 0
    for trace in data:
        kind = trace.get('type', 'scatter')
        if kind in {'surface', 'heatmap'}:
            z = trace.get('z', [])
            if not z or not isinstance(z[0], list) or not z[0] or any(len(row) != len(z[0]) for row in z):
                raise ValueError('Surface and heatmap z values must form a rectangular grid.')
            if len(trace.get('x', z[0])) != len(z[0]) or len(trace.get('y', z)) != len(z):
                raise ValueError('The x and y coordinates must match the grid dimensions.')
            points += len(z)*len(z[0])
        else:
            y = trace.get('y', [])
            if not isinstance(y, list) or not y or len(trace.get('x', y)) != len(y):
                raise ValueError('Provide matching, nonempty x and y coordinate lists.')
            if kind == 'scatter3d' and len(trace.get('z', [])) != len(y):
                raise ValueError('A 3D curve needs matching x, y and z coordinate lists.')
            points += len(y)
    if points > 50000:
        raise ValueError('Use at most 50,000 plotted samples per figure.')
    if not isinstance(description, str) or not description.strip():
        raise ValueError('Give the plot a short text description.')
    _post('plot', data=data, layout=_plain(layout or {}), description=description)


def show_matplotlib(figure=None, *, description='Matplotlib figure. Inspect the code and downloaded data for its values.'):
    """Show a Matplotlib figure as a downloadable PNG."""
    import matplotlib.pyplot as plt
    figure = figure or plt.gcf()
    buffer = io.BytesIO()
    figure.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
    _post('image', png=base64.b64encode(buffer.getvalue()).decode('ascii'), description=description)
    plt.close(figure)


def _show_all(*args, **kwargs):
    import matplotlib.pyplot as plt
    for number in list(plt.get_fignums()):
        show_matplotlib(plt.figure(number))


def export_file(name, content):
    """Offer UTF-8 CSV, JSON or text as a browser download."""
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,100}\.(csv|json|txt)', name):
        raise ValueError('Use a simple filename ending in .csv, .json or .txt.')
    if not isinstance(content, str):
        raise TypeError('Export content must be text. Use json.dumps for JSON.')
    _post('file', name=name, content=content)
