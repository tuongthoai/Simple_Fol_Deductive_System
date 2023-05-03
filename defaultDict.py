import collections


class defaultkeydict(collections.defaultdict):
    """The same as the default dict datastructure in python but has a single modified one default factory for key"""
    def __missing__(self, key):
        self[key] = result = self.default_factory(key)  # passing an argument to default factory
        return result
