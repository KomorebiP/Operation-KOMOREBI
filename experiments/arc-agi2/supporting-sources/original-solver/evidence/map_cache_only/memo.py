"""Task-local memoization of pure inherited feature computations.
No model, task identity, prediction selection or persistent state is cached here.
Author: Komorebi P.
"""
from contextlib import contextmanager

@contextmanager
def feature_cache(module):
    original_maps=module._cell_feature_maps
    original_rows=module._feature_rows
    maps_cache={};rows_cache={}
    def key(array):return (array.dtype.str,array.shape,array.tobytes())
    def maps(array):
        k=key(array)
        if k not in maps_cache:maps_cache[k]=original_maps(array)
        return maps_cache[k]
    def rows(array,names):
        k=(key(array),tuple(names))
        if k not in rows_cache:rows_cache[k]=original_rows(array,names)
        return rows_cache[k]
    module._cell_feature_maps=maps;module._feature_rows=rows
    try:yield
    finally:
        module._cell_feature_maps=original_maps;module._feature_rows=original_rows
        maps_cache.clear();rows_cache.clear()
