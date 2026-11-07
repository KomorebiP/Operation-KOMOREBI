"""Source and exact finite regression checks for the Smith chart laboratory."""
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Ids(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == 'id':
                self.ids.append(value)

class SmithChartSiteTest(unittest.TestCase):
    def test_source_and_selectors(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        css = (ROOT/'website/assets/smith-chart.css').read_text(encoding='utf-8')
        js = (ROOT/'website/assets/smith-chart.js').read_text(encoding='utf-8')
        self.assertIn('id="smith-studio"', body)
        self.assertIn('id="smith-chart"', body)
        self.assertIn('id="grid-mode"', body)
        self.assertIn('id="panel-verify"', body)
        self.assertIn('id="run-tests"', body)
        self.assertIn('@scope (.smith-lab)', css)
        self.assertIn("$('smith-studio').classList.add('js-ready')", js)
        self.assertIn('runChecks()', js)
        self.assertNotIn('Not yet published', body)
        ids = Ids()
        ids.feed(body)
        self.assertEqual(len(ids.ids), len(set(ids.ids)))
        self.assertEqual(len(re.findall(r'<h1\b', body)), 1)
        self.assertNotRegex(body, r'<main\b|<script\b')

    def test_each_input_has_an_accessible_name(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        controls = re.findall(r'<(?:input|select|textarea)[ >][^>]*>', body)
        self.assertGreaterEqual(len(controls), 16)
        for control in controls:
            self.assertRegex(control, r'aria-label="[^"]+"')

    def test_cleanup_navigation_and_optional_controls(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        js = (ROOT/'website/assets/smith-chart.js').read_text(encoding='utf-8')
        self.assertEqual(body.count('<h1'), 1)
        nav = body.split('<nav class="smith-section-nav"', 1)[1].split('</nav>', 1)[0]
        targets = re.findall(r'href="#([^"]+)"', nav)
        ids = set(re.findall(r'\bid="([^"]+)"', body))
        self.assertEqual(len(targets), 4)
        self.assertTrue(set(targets).issubset(ids))
        self.assertIn('<details class="overlay-options">', body)
        self.assertIn('<details class="advanced-values">', body)
        for key in ('show-rays', 'show-orbit'):
            tag = re.search(r'<input[^>]*id="'+key+r'"[^>]*>', body)
            self.assertIsNotNone(tag)
            self.assertNotIn('checked', tag.group(0))
        self.assertIn("for(const id of ['show-rays','show-orbit'])$(id).checked=false;", js)

    def test_chart_inspector_focus_and_mobile_navigation(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        css = (ROOT/'website/assets/smith-chart.css').read_text(encoding='utf-8')
        js = (ROOT/'website/assets/smith-chart.js').read_text(encoding='utf-8')
        self.assertIn('viewbox="70 37 760 730"', body)
        self.assertIn('id="focus-chart" aria-pressed="false"', body)
        self.assertIn('id="chart-inspect"', body)
        self.assertIn('id="copy-current"', body)
        self.assertIn('function setChartFocus(enabled)', js)
        self.assertIn('function updateInspection(g)', js)
        self.assertIn("if(mode!=='y')", js)
        self.assertIn("if(mode!=='z')", js)
        self.assertIn("e.key==='Escape'", js)
        self.assertIn(':scope.focus-chart .side', css)
        self.assertIn('.smith-section-nav{display:grid;grid-template-columns:repeat(2', css)

    def test_direct_gamma_editor_and_clickable_packets(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        css = (ROOT/'website/assets/smith-chart.css').read_text(encoding='utf-8')
        js = (ROOT/'website/assets/smith-chart.js').read_text(encoding='utf-8')
        for id_ in ('gamma-editor','gamma-re','gamma-im','gamma-apply','gamma-from-load','gamma-warning'):
            self.assertIn('id="'+id_+'"', body)
        self.assertIn('Enter Γ directly', body)
        self.assertIn('aria-describedby="gamma-help gamma-warning"', body)
        self.assertIn('Select a bar to change j', body)
        self.assertIn('function syncGammaEditor(force=false)', js)
        self.assertIn('setFromGamma(g,false)', js)
        self.assertIn('Outside the passive Smith disk', js)
        self.assertIn("const bar=document.createElement('button')", js)
        self.assertIn("bar.setAttribute('aria-pressed'", js)
        self.assertIn(".packet-bars .packet-bar:focus-visible", css)
        self.assertIn('.gamma-editor summary{min-height:44px', css)

    def test_comparison_uses_one_reference_impedance(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        js = (ROOT/'website/assets/smith-chart.js').read_text(encoding='utf-8')
        self.assertIn('id="swap-reference"', body)
        self.assertIn('id="comparison-note"', body)
        self.assertIn('function referenceGammaAt(z0)', js)
        self.assertIn('const commonReference=referenceGammaAt(states.z0)', js)
        self.assertIn("referencePin=pin?{...pin}:null;", js)
        self.assertNotIn('referencePin.gamma', js)
        self.assertIn("setAttribute('class','comparison-link')", js)
        self.assertIn("referencePin.special==='open'&&states.special==='open'?'0 Ω'", js)

        # Exact Cartesian form of (Z-Z0)/(Z+Z0), for real positive Z0.
        def gamma(r, x, z0):
            denominator = (r+z0)**2 + x**2
            return ((Fraction(r*r-z0*z0+x*x, denominator)),
                    Fraction(2*z0*x, denominator))

        a_at_50 = gamma(25, 25, 50)
        a_at_75 = gamma(25, 25, 75)
        b_at_75 = gamma(50, 0, 75)
        self.assertEqual(a_at_50, (Fraction(-1, 5), Fraction(2, 5)))
        self.assertEqual(a_at_75, (Fraction(-7, 17), Fraction(6, 17)))
        self.assertEqual(b_at_75, (Fraction(-1, 5), Fraction(0)))
        self.assertNotEqual(a_at_50, a_at_75)
        # Renormalization changes each Γ but preserves the physical A and B loads.
        self.assertNotEqual(a_at_75, b_at_75)

    def test_reversible_load_history_source_and_scope(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        css = (ROOT/'website/assets/smith-chart.css').read_text(encoding='utf-8')
        js = (ROOT/'website/assets/smith-chart.js').read_text(encoding='utf-8')
        for control in ('undo-load', 'redo-load'):
            self.assertIn('id="'+control+'"', body)
        self.assertIn('class="load-history"', body)
        self.assertIn('id="history-status"', body)
        self.assertIn('function loadHistorySnapshot()', js)
        self.assertIn('function recordLoadHistory(before)', js)
        self.assertIn('function undoLoad()', js)
        self.assertIn('function redoLoad()', js)
        self.assertIn('function cancelDrag()', js)
        self.assertIn('pointercancel', js)
        self.assertIn("event.target.closest?.('input,textarea,select", js)
        self.assertIn("clearLoadHistory();", js)
        self.assertIn('.smith-lab .load-history', css)
        self.assertIn('.smith-lab .history-status:empty', css)

    def test_chart_zoom_is_view_only_with_safe_drag_cancel(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        css = (ROOT/'website/assets/smith-chart.css').read_text(encoding='utf-8')
        js = (ROOT/'website/assets/smith-chart.js').read_text(encoding='utf-8')
        for id_ in ('chart-zoom-in', 'chart-zoom-out', 'chart-zoom-level',
                    'chart-view-center', 'chart-view-fit'):
            self.assertIn('id="'+id_+'"', body)
        self.assertIn('aria-label="Current chart magnification"', body)
        self.assertIn('const ZOOM_FACTORS=[1,1.5,2,3,4]', js)
        self.assertIn('function updateChartView()', js)
        self.assertIn('function resetChartView()', js)
        self.assertIn('function centerChartView()', js)
        self.assertIn("setAttribute('viewBox'", js)
        self.assertIn("if(e.key==='Escape'&&drag)cancelDrag();", js)
        self.assertIn("window.addEventListener('blur',cancelDrag);", js)
        self.assertEqual(js.count('cancelDrag();resetChartView();'), 2)
        self.assertIn('.smith-lab .chart-zoom-controls{display:none;', css)
        self.assertIn('.smith-lab.js-ready .chart-zoom-controls{display:flex}', css)
        # View magnification is intentionally excluded from portable RF settings.
        start = js.index('function serializeSession()')
        end = js.index('function validateSession(', start)
        self.assertNotIn('zoomIndex', js[start:end])
        self.assertNotIn('zoomCenter', js[start:end])

    def test_projector_impedance_identity_exactly(self):
        for t in (Fraction(0), Fraction(1,10), Fraction(-2,5), Fraction(3,4)):
            z = (1+t)/(1-t)
            for n in (2,3,4,5,6,8,12):
                packets = [(1+t**n)/(1-t**n)] + [
                    2*t**j/(1-t**n) for j in range(1,n)]
                self.assertEqual(sum(packets), z)
                K = 5
                for j in range(1,n):
                    finite = sum(2*t**(j+q*n) for q in range(K))
                    self.assertEqual(finite, 2*t**j*(1-t**(K*n))/(1-t**n))
                finite_zero = 1 + sum(2*t**(q*n) for q in range(1,K+1))
                self.assertEqual(finite_zero, 1+2*t**n*(1-t**(K*n))/(1-t**n))

    def test_admittance_parity_and_reconstruction(self):
        for t in (Fraction(1,2), Fraction(-1,3), Fraction(3,5)):
            z, y = (1+t)/(1-t), (1-t)/(1+t)
            for n in (2,3,4,5,6,8,12):
                zp = [(1+t**n)/(1-t**n)] + [
                    2*t**j/(1-t**n) for j in range(1,n)]
                if n % 2 == 0:
                    yp = [(-1)**j * zp[j] for j in range(n)]
                else:
                    yp = [(1-t**n)/(1+t**n)] + [
                        2*(-1)**j * t**j/(1+t**n) for j in range(1,n)]
                self.assertEqual(sum(zp), z)
                self.assertEqual(sum(yp), y)
                self.assertEqual(z*y, 1)

if __name__ == '__main__':
    unittest.main()
