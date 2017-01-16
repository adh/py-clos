from .cache import *
from .util import common_superclass
import collections

class Specializer:
    __cache_policy__ = NoCachePolicy
    def matches(self, object):
        raise NotImplemented

    def sort_key(self, arg):
        return (-1, 0)
    
    @property
    def cache_policy(self):
        return self.__cache_policy__
    
class TypeSpecializer(Specializer):
    __slots__ = ["type"]
    __cache_policy__ = TypeCachePolicy
    def __init__(self, type):
        self.type = type
    def matches(self, object):
        return isinstance(object, self.type)

    def sort_key(self, arg):
        mro = type(arg).mro()
        try:
            return (0, mro.index(self.type))
        except:
            raise ValueError("{} is not an instance of {}".format(arg,
                                                                  self.type))
ROOT_SPECIALIZER = TypeSpecializer(object)
    
class SingletonSpecializer(Specializer):
    __slots__ = ["instance"]
    __cache_policy__ = IdentityCachePolicy
    def __init__(self, instance):
        self.instance = instance
    def matches(self, object):
        return object is self.instance

class EqualitySpecializer(Specializer):
    __slots__ = ["instance"]
    __cache_policy__ = InstanceCachePolicy
    def __init__(self, instance):
        self.instance = instance
    def matches(self, object):
        return object == self.instance

class UnionSpecializer(Specializer):
    __slots__ = ["specialziers"]
    def __init__(self, specializers):
        self.specializers = specializers
    def matches(self, object):
        return any((i.matches(object) for i in specilizers))
    def sort_key(self, arg):
        return min((i.sort_key(arg) for i in i.specializer if i.matches(arg)))
    @property
    def cache_policy(self):
        return common_superclass((i.cache_policy for i in self.specializers))

    
def specializer(designator):
    if isinstance(designator, type):
        return TypeSpecializer(designator)
    if isinstance(designator, collections.Iterable):
        return UnionSpecializer((specializer(i) for i in designator))

    return designator
    
