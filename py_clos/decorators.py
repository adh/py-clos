from . import base
from . import util
import sys

# This is somewhat horrible hack based on inspecting sys._getframe,
# but it ssems to be best way to implement this without having
# repeated or redundant nonsencial function names in user code. In
# contrast to inspecting module namespace or keeping global registry
# this perfectly matches behavior of normal python scoping rules.

def generic(proc=None, qualifiers=[], frame=None,
            function=None, module=None, **kwargs):
    def wrapper(proc, frame=None):
        if frame is None:
            frame = sys._getframe(1)
            
        gf = function
        
        if gf is None:
            mod = module
            if mod is not None:
                gf = util.lookup_object(mod, proc.__name__)
            else:
                try:
                    gf = frame.f_locals[proc.__name__]
                except KeyError:
                    pass
                
        if gf is None:
            gf = base.GenericFunction(proc.__module__ + '.' + proc.__qualname__)
        
        gf.redefine(**kwargs)
        method = base.Method.from_annotated_function(proc,
                                                     qualifiers=qualifiers)
        gf.add_method(method)
        return gf

    if proc:
        return wrapper(proc, frame=sys._getframe(1))
    else:
        return wrapper

def qualified_generic(qualifiers):
    def wrap(proc=None, **kwargs):
        return generic(proc=proc,
                       frame=sys._getframe(1),
                       qualifiers=qualifiers,
                       **kwargs)
    return wrap
