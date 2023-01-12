import json


class ConfigLoader:

    def __init__(self, config_src="config.json") -> None:
        self.config_src = config_src
        self.update()

    def update(self) -> None:
        with open(self.config_src) as f:
            self.config_json = json.load(f)

    def get_section(self, section: str, update=False) -> dict:
        if update:
            self.update()
        return self.config_json[section]
