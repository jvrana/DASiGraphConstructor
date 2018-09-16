class ConfigRegistry(type):
    """Stores a list of models that can be accessed by name."""
    models = {}

    def __init__(cls, name, bases, selfdict):
        """Saves model to the registry"""
        super().__init__(name, bases, selfdict)
        if not name == "ModelBase":
            ConfigRegistry.models[name] = cls

    @staticmethod
    def get_config(model_name):
        """Gets model by model_name"""
        if model_name not in ConfigRegistry.models:
            raise Exception(
                "Config \"{}\" not found in ConfigRegistry.".format(model_name))
        else:
            return ConfigRegistry.models[model_name]

    def __getattr__(cls, item):
        """
        Special warning for attribute errors.
        Its likely that user may have wanted to use a model interface instead of
        the Base class.
        """
        raise AttributeError("'{0}' has no attribute '{1}'. Method may be a ModelInterface method."
                             " Did you mean '<yoursession>.{0}.{1}'?"
                             .format(cls.__name__, item))


class Config(object, metaclass=ConfigRegistry):
    DEBUG = False
    TESTING = False
    DATABASE = None


class Production(Config):
    DATABASE = ''


class Development(Config):
    TESTING = True
    DATABASE = 'sqlite:///development'


class Testing(Config):
    TESTING = True
    DEBUG = True
    DATABASE = 'sqlite:///testing'
