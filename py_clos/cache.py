try:
    from lru import LRU
except ImportError:
    def LRU(n):
        return {}
    
class NoCachePolicy:
    pass
    
class IdentityCachePolicy(NoCachePolicy):
    c_cache_key = b'I'
    @staticmethod
    def get_cache_key(object):
        return id(object)


class InstanceCachePolicy(IdentityCachePolicy):
    @staticmethod
    def get_cache_key(object):
        return object


class TypeCachePolicy(InstanceCachePolicy):
    c_cache_key = b'T'
    @staticmethod
    def get_cache_key(object):
        return type(object)

