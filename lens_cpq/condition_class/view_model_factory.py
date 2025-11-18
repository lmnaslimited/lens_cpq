class ViewModelFactory:
    _instances = {}
    _class_map = {}

    @classmethod
    def register_controller(cls, key, clazz):
        cls._class_map[key] = clazz

    @classmethod
    def get_controller(cls, key, doctype, event, event_fields):
        if key in cls._instances:
            return cls._instances[key]

        clazz = cls._class_map[key]
        instance = clazz(doctype, event, event_fields)
        cls._instances[key] = instance
        return instance
