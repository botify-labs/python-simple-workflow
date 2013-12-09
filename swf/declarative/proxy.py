class Proxy(object):
    def __getattr__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except(AttributeError) as err:
            if not err.message.startswith("'{}'".format(
                                          self.__class__.__name__)):
                raise

        try:
            return getattr(self._model, attr)
        except AttributeError:
            raise AttributeError("'{}' has no attribute '{}'".format(
                                 self.__class__.__name__, attr))
