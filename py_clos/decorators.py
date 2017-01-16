from . import base

def generic(function=None, qualifiers=[], **kwargs):
    if function:
        return generic()(function)

    def wrapper(function):
        gf = base.defgeneric(function.__qualname__, **kwargs)
        method = base.Method.from_annotated_function(function,
                                                     qualifiers=qualifiers)
        gf.redefine(**kwargs)
        gf.add_method(method)
        return gf
    return wrapper

def qualified_generic(qualifiers):
    def wrap(function=None, **kwargs):
        return generic(function=function,
                       qualifiers=qualifiers,
                       **kwargs)
    return wrap
