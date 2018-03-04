
import json

import datastorage


class Settings:
    THEME_LIGHT = 'light'
    THEME_DARK = 'dark'
    THEME_SEPIA = 'sepia'
    VERSION = 1
    DEF_FONT_SIZE = 11
    DEF_THEME = 'dark'

    def __init__(self):
        pass

    @staticmethod
    def load(ds: datastorage.DataStorage):
        settings_str = ds.get_preferences()
        db_settings = json.loads(settings_str) if settings_str is not None else {}
        def_settings = {
            'font_size': Settings.DEF_FONT_SIZE,
            'theme': Settings.DEF_THEME
        }
        overall_settings = {**def_settings, **db_settings}
        return overall_settings

    @staticmethod
    def save(ds: datastorage.DataStorage, args):
        settings_str = ds.get_preferences()
        db_settings = json.loads(settings_str) if settings_str is not None else {}
        print('argzzz', args.get)
        font_size = args.get('font_size', None, type=int)
        if font_size:
            if not 5 <= font_size <= 32:
                raise AttributeError('Font size is out of range [5, 32]')
            db_settings['font_size'] = font_size
        theme = args.get('theme', None, type=str)
        if theme:
            if theme not in (Settings.THEME_LIGHT, Settings.THEME_DARK, Settings.THEME_SEPIA):
                raise AttributeError('Unknown theme: ' + theme)
            db_settings['theme'] = theme
        settings_str = json.dumps(db_settings)
        print(settings_str)
        ds.set_preferences(settings_str)
