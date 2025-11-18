class ViewModelFactory:
    _instances = {}
    _class_map = {}

    @classmethod
    def get_controller(cls, key, clazz, doctype, event, event_fields):
        """Returns existing instance if available, else creates new one."""
        
        # Check if an instance already exists
        if key in cls._instances:
            return cls._instances[key]

        # Instantiate a new controller
        instance = clazz(doctype, event, event_fields)

        # Store it for reuse
        cls._instances[key] = instance
        
        return instance
