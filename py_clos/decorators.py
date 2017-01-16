from . import base

def generic(function=None, qualifiers=[], **kwargs):
    def wrapper(function):
        gf = base.defgeneric(function.__module__+"."+function.__qualname__,
                             **kwargs)
        method = base.Method.from_annotated_function(function,
                                                     qualifiers=qualifiers)
        gf.redefine(**kwargs)
        gf.add_method(method)
        return gf

    if function:
        return wrapper(function)
    else:
        return wrapper

def qualified_generic(qualifiers):
    def wrap(function=None, **kwargs):
        return generic(function=function,
                       qualifiers=qualifiers,
                       **kwargs)
    return wrap
