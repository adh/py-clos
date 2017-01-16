# -*- mode: python -*-

from .combinations import STANDARD_METHOD_COMBINATION
from .specializers import specializer, ROOT_SPECIALIZER
from . import util
from .cache import NoCachePolicy, LRU, TypeCachePolicy
import threading
import inspect
import warnings


class GenericFunction:
    def __init__(self, name):
        self._name = name
        
        self._method_combination = STANDARD_METHOD_COMBINATION
        self._methods = []
        self._specialized_on = []
        self._cache_policies = []
        self._lock = threading.Lock()

        self.clear_cache()

    def redefine(self, method_combination=None):
        if method_combination is not None:
            self._method_combination = method_combination
            self.clear_cache()
        
    def clear_cache(self):
        if self._cache_policies is None:
            self._cache = None
        else:
            for i in self._cache_policies:
                if i != TypeCachePolicy:
                    self._cache = LRU(len(self._methods) * 4)
                    return
            self._cache = {}
            # the idea is that number of possible types is clearly bounded
            # so limiting the cache size is unnecessary

    def rebuild_specialized_on(self):
        maxlen = max((len(i.specializers) for i in self._methods))
        bitmap = [False] * maxlen

        for i in self._methods:
            for j in i.specialized_on:
                bitmap[j] = True

        self._specialized_on = [idx for idx, i in enumerate(bitmap) if i]

    def rebuild_cache_policies(self):
        spec_count = len(self._specialized_on)
        cps = [[]] * spec_count
        
        for i in self._methods:
            for idx, j in enumerate(self._specialized_on):
                if j >= len(i.specializers):
                    continue
                spec = i.specializers[j]
                if spec is None:
                    continue
                cps[idx].append(spec.cache_policy)

        cps = [util.common_superclass(*i) for i in cps]
        for i in cps:
            if i is NoCachePolicy:
                self._cache_policies = None

        self._cache_policies = cps
        
    def add_method(self, method):
        with self._lock:
            self._methods.append(method)
            self.rebuild_specialized_on()
            self.rebuild_cache_policies()
            self.clear_cache()

    def get_cache_key(self, args):
        return tuple((cp.get_cache_key(args[self._specialized_on[idx]])
                      for idx, cp in enumerate(self._cache_policies)))

    def get_applicable_methods(self, args):
        return sorted((i for i in self._methods if i.matches(args)),
                      key=lambda i: i.sort_key(args))
    
    def __call__(self, *args, **kwargs):
        if self._cache is not None:
            ck = self.get_cache_key(args)
            if ck in self._cache:
                return self._cache[ck](*args, **kwargs)

        with self._lock:
            methods = self.get_applicable_methods(args)
            effective_method = self._method_combination.compute_effective_method(methods)
            if self._cache is not None:
                self._cache[ck] = effective_method

        return effective_method(*args, **kwargs)
        
class Method:
    __slots__ = ["proc", "specializers", "qualifiers", "next_method_arg"]
    
    def __init__(self, proc,
                 specializers=[],
                 qualifiers=[],
                 next_method_arg=None):
        self.proc = proc
        self.specializers = specializers
        self.qualifiers = qualifiers
        self.next_method_arg = next_method_arg

    @property
    def specialized_on(self):
        return [idx for idx, i in enumerate(self.specializers) if i != None]

    def matches(self, args):
        for idx, i in enumerate(self.specializers):
            if i is None:
                continue
            if not i.matches(args[idx]):
                return False
        return True

    def sort_key(self, args):
        res = []
        for idx, i in enumerate(self.specializers):
            if idx >= len(args):
                break
            if i is None:
                i = ROOT_SPECIALIZER
            res.append(i.sort_key(args[idx]))
        return res
    
    @classmethod
    def from_annotated_function(cls, proc, qualifiers=[]):
        argspec = inspect.getfullargspec(proc)
        arg_names = argspec.args[:len(argspec.args) - len(argspec.defaults or [])]
        anno = proc.__annotations__
        specializers = [(specializer(anno[i]) if i in anno else None)
                        for i in arg_names]
        return cls(proc,
                   specializers=specializers,
                   qualifiers=qualifiers,
                   next_method_arg=("next_method"
                                    if "next_method" in argspec.args else None))

    def __call__(self, *args, **kwargs):
        return self.callable(*args, **kwargs)

    @property
    def callable(self):
        return self.callable_with_next_method()

    def callable_with_next_method(self, next_method=None):
        if self.next_method_arg:
            def wrapper(*args, **kwargs):
                kw = {self.next_method_arg: next_method}
                kw.update(kwargs)
                return self.proc(*args, **kw)
            return wrapper
        else:
            return self.proc
        
        
    def call_method(self, args, kwargs, next_method=None):
        if self.next_method_arg:
            kw = {self.next_method_arg: next_method}
            kw.update(kwargs)
            return self.proc(*args, **kw)
        else:
            return self.proc(*args, **kwargs)
            
        
def defgeneric(name, **kwargs):
    gf = GenericFunction(name)
    gf.redefine(**kwargs)
    return gf

