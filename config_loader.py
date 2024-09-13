import sys
import tomllib
from pathlib import Path


def load_config():
    config_file = Path("config.toml")

    try:
        with config_file.open("rb") as f:
            toml_config = tomllib.load(f)
            print(f"Loaded configuration: {toml_config}")
            return toml_config
    except (IOError, tomllib.TOMLDecodeError) as e:
        print(f"Error reading config file {config_file}: {e}")
        sys.exit(1)
