try:
    from lru import LRU
except ImportError:
    def LRU(n):
        return {}
    
class NoCachePolicy:
    pass
    
class IdentityCachePolicy(NoCachePolicy):
    @classmethod
    def get_cache_key(cls, object):
        return id(object)


class InstanceCachePolicy(IdentityCachePolicy):
    @classmethod
    def get_cache_key(cls, object):
        return object


class TypeCachePolicy(InstanceCachePolicy):
    @classmethod
    def get_cache_key(cls, object):
        return type(object)

