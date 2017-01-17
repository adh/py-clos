# -*- mode: python -*-

from .decorators import generic, qualified_generic

def call_before_after(proc, before, after):
    def fun(*args, **kwargs):
        for i in before:
            i(*args, **kwargs)
        res = proc(*args, **kwargs)
        for i in after:
            i(*args, **kwargs)
    return fun

def call_chain(chain, last=None):
    if len(chain) == 1 and last is None:
        return chain[0].callable

    if len(chain) == 0:
        return last
    
    return chain[0].callable_with_next_method(next_method=call_chain(chain[1:],
                                                                     last=last))

class MethodCombinationMetaclass(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        result = type.__new__(cls, name, bases, dict(namespace))
        for i in result.__qualifiers__:
            setattr(generic, i, qualified_generic([i]))
        return result

class MethodCombination(metaclass=MethodCombinationMetaclass):
    __qualifiers__ = []
    
    @property
    def qualifiers(self):
        return self.__qualifiers__
    
    def bin_by_qualifiers(self, methods):
        res = {q: [] for q in self.qualifiers}
        res[None] = []
        
        for i in methods:
            for q in i.qualifiers:
                if q not in res:
                    raise ValueError("{} does not support qualifier {}"
                                     .format(self, q))
                res[q].append(i)
            else:
                res[None].append(i)

        return res
        
    def compute_effective_method(self, methods):
        raise NotImplemented

class StandardMethodCombination(MethodCombination):
    __qualifiers__ = ["before", "after", "around"]
    
    def compute_effective_method(self, methods):
        qs = self.bin_by_qualifiers(methods)

        if not qs[None]:
            raise ValueError("No applicable primary methods")

        res = call_chain(qs[None])

        if qs["before"] or qs["after"]:
            res = call_before_after(res,
                                    before=[i.callable
                                            for i in qs["before"]],
                                    after=[i.callable
                                           for i in reversed(qs["after"])])
        if qs["around"]:
            res = call_chain(qs["around"], res)

        return res
            
STANDARD_METHOD_COMBINATION = StandardMethodCombination()

class ReducingMethodCombination(MethodCombination):
    __qualifiers__ = ["around"]

    def __init__(self, fun, identity=False):
        self.fun = fun
        self.identity = identity

    def effective_method(self, funs):
        return lambda *args, **kwargs:\
            self.fun((i(*args, **kwargs) for i in funs))
        
    def compute_effective_method(self, methods):
        qs = self.bin_by_qualifiers(methods)

        if not qs[None]:
            raise ValueError("No applicable primary methods")

        if len(qs[None]) == 1 and self.identity:
            res = qs[None][0]
        else:
            res = self.effective_method([i.callable for i in qs[None]])
        
        if qs["around"]:
            res = call_chain(qs["around"], res)

        return res
