import os
import yaml


# Config class, which loads the configuration file and provides
# a way to access the configuration values.
class Config:
    def __init__(self, env: str):
        print(f"Loading configuration for environment: {env}")
        self.env = env
        self.config_path = f"config.{env}.yaml"
        self.config = self.load_config(self.config_path)
        print(f"Configuration loaded successfully")

    def load_config(self, config_path: str) -> dict:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as file:
            try:
                config = yaml.safe_load(file)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid config file: {config_path}") from e
        return config

    def __getitem__(self, key: str):
        return self.config[key]
