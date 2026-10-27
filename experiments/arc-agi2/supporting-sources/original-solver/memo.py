"""Task-local memoization of pure inherited feature computations.
No model, task identity, prediction selection or persistent state is cached here.
Author: Komorebi P.
"""
from contextlib import contextmanager

@contextmanager
def feature_cache(module):
    original_maps=module._cell_feature_maps
    original_rows=module._feature_rows
    maps_cache={};rows_cache={};columns_cache={}
    def key(array):return (array.dtype.str,array.shape,array.tobytes())
    def maps(array):
        k=key(array)
        if k not in maps_cache:maps_cache[k]=original_maps(array)
        return maps_cache[k]
    def rows(array,names):
        array_key=key(array)
        k=(array_key,tuple(names))
        if k not in rows_cache:
            values=maps(array)
            columns=[]
            for name in names:
                column_key=(array_key,name)
                if column_key not in columns_cache:
                    columns_cache[column_key]=tuple(module._hashable(values[name][r,c])
                        for r in range(array.shape[0]) for c in range(array.shape[1]))
                columns.append(columns_cache[column_key])
            rows_cache[k]=list(zip(*columns)) if columns else [() for _ in range(array.size)]
        return rows_cache[k]
    module._cell_feature_maps=maps;module._feature_rows=rows
    try:yield
    finally:
        module._cell_feature_maps=original_maps;module._feature_rows=original_rows
        maps_cache.clear();rows_cache.clear();columns_cache.clear()
