import yaml
import os

class Settings:
    def __init__(self, default_config_path, user_config_path):
        self.config = self.load_config(default_config_path)
        if os.path.isfile(user_config_path):
            user_config = self.load_config(user_config_path)
            self.merge_configs(self.config, user_config)

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
