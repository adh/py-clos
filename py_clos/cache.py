try:
    from lru import LRU
except ImportError:
    def LRU(n):
        return {}
    
class NoCachePolicy:
    pass
    
class IdentityCachePolicy(NoCachePolicy):
    @staticmethod
    def get_cache_key(object):
        return id(object)


class InstanceCachePolicy(IdentityCachePolicy):
    @staticmethod
    def get_cache_key(object):
        return object


class TypeCachePolicy(InstanceCachePolicy):
    @staticmethod
    def get_cache_key(object):
        return type(object)

