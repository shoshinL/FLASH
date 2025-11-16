class SettingsContext:
    _settings_manager = None

    @classmethod
    def set_settings_manager(cls, settings_manager):
        cls._settings_manager = settings_manager

    @classmethod
    def get_settings_manager(cls):
        if cls._settings_manager is None:
            raise RuntimeError("SettingsManager has not been initialized.")
        return cls._settings_manager