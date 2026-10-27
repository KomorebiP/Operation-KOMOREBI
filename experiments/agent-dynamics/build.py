"""Regenerate the exact model, 14-plate PDF/SVG/PNG atlas, GIF, and offline player.
Run: python build.py
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
from visuals import render_atlas, render_animation
if __name__ == '__main__':
    print(render_atlas())
    print(render_animation())
