import yaml
import os

class Settings:
    def __init__(self, default_config_path, user_config_path):
        self.default_config_path = default_config_path
        self.user_config_path = user_config_path
        self.config = self.load_config(default_config_path)
        if os.path.isfile(user_config_path):
            user_config = self.load_config(user_config_path)
            self.merge_configs(self.config, user_config)
            
        self.dropdown_options = {
            'model_options.common.language': ['auto', 'af', 'ar', 'hy', 'az', 'be', 'bs', 'bg', 'ca', 'zh', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fi', 'fr', 'gl', 'de', 'el', 'he', 'hi', 'hu', 'is', 'id', 'it', 'ja', 'kn', 'kk', 'ko', 'lv', 'lt', 'mk', 'ms', 'mr', 'mi', 'ne', 'no', 'fa', 'pl', 'pt', 'ro', 'ru', 'sr', 'sk', 'sl', 'es', 'sw', 'sv', 'tl', 'ta', 'th', 'tr', 'uk', 'ur', 'vi', 'cy'],
            'model_options.local.model': ['base', 'base.en', 'tiny', 'tiny.en', 'small', 'small.en', 'medium', 'medium.en', 'large', 'large-v1', 'large-v2', 'large-v3'],
            'model_options.local.device': ['auto', 'cpu', 'cuda'],
            'model_options.local.compute_type': ['default', 'float32', 'float16'],
            'recording_options.recording_mode': ['voice_activity_detection', 'hold_to_record', 'press_to_toggle'],
        }

    def load_config(self, config_path):
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)

    def merge_configs(self, default, user):
        for key, value in user.items():
            if isinstance(value, dict):
                default[key] = self.merge_configs(default.get(key, {}), value)
            else:
                default[key] = value
        return default

    def save_config(self):
        if self.config['model_options']['common']['language'] == 'auto':
            self.config['model_options']['common']['language'] = None
        if self.config['model_options']['common']['initial_prompt'] == '':
            self.config['model_options']['common']['initial_prompt'] = None
        if self.config['recording_options']['sound_device'] == 'auto' or '':
            self.config['recording_options']['sound_device'] = None

        with open(self.user_config_path, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False)
