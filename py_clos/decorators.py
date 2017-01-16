from . import base
from . import util

def generic(proc=None, qualifiers=[], function=None, module=None, **kwargs):
    def wrapper(proc):
        gf = function
        
        if gf is None:
            mod = module
            if mod is None:
                mod = proc.__module__
            try:
                gf = util.lookup_object(mod, proc.__qualname__)
            except:
                pass
            
        if gf is None:
            gf = base.GenericFunction(proc.__module__ + '.' + proc.__qualname__)
        
        gf.redefine(**kwargs)
        method = base.Method.from_annotated_function(proc,
                                                     qualifiers=qualifiers)
        gf.add_method(method)
        return gf

    if proc:
        return wrapper(proc)
    else:
        return wrapper

def qualified_generic(qualifiers):
    def wrap(proc=None, **kwargs):
        return generic(proc=proc,
                       qualifiers=qualifiers,
                       **kwargs)
    return wrap
