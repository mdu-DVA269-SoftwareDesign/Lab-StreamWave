import json
from abc import ABC
from pathlib import Path
from typing import Union


class JsonDataManager(ABC):
    def __init__(self, data_file: Path, default_data: Union[list, dict] = None):
        self._data_file = data_file
        self._default_data = default_data if default_data is not None else []
        self._db = self._load()
    
    @property
    def data_file(self) -> Path:
        return self._data_file
    
    def _load(self) -> Union[list, dict]:
        if not self._data_file.exists():
            with open(self._data_file, "w") as f:
                json.dump(self._default_data, f)
            return self._default_data.copy() if isinstance(self._default_data, (list, dict)) else self._default_data
        with open(self._data_file, "r") as f:
            return json.load(f)
    
    def _save(self) -> None:
        with open(self._data_file, "w") as f:
            json.dump(self._db, f, indent=4)
    
    def reload(self) -> None:
        self._db = self._load()
