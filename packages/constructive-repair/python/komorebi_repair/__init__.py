"""Stable exact-rational repair interface; Python validity is not kernel acceptance.

This distribution is standalone. It does not modify the wider Komorebi library.
Only names listed in __all__ are included in the proposed 1.0 API contract.
"""
from .api import Outcome, solve, verify, load, free_problem, menu_problem
from repair_certificates import Mat as ExactMatrix, InvalidData

__version__ = '1.0.0rc3'
__all__ = ['ExactMatrix', 'InvalidData', 'Outcome', 'free_problem',
           'menu_problem', 'load', 'solve', 'verify', '__version__']
