
class CustomSettings(object):

    _instance = None

    @classmethod
    def set_prop(cls, attr, value):
        instance = cls.get_instance()
        setattr(instance, attr, value)

    @classmethod
    def get_prop(cls, attr):
        instance = cls.get_instance()
        if not hasattr(instance, attr):
            raise Exception("Properties do not contain attr: {}".format(attr))
        return getattr(instance, attr)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CustomSettings
        return cls._instance

