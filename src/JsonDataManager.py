import json
from abc import ABC
from pathlib import Path
from typing import Any, Optional, List


class JsonDataManager(ABC):
    def __init__(self, data_file: Path, default_data: list[Any] = [], id_field: str = "id"):
        # super().__init__()
        self._data_file = data_file
        self._default_data = default_data if default_data is not None else []
        self._id_field = id_field
        self._db = self._load()

    @property
    def data_file(self) -> Path:
        return self._data_file

    def _load(self) -> list:
        if not self._data_file.exists():
            with open(self._data_file, "w") as f:
                json.dump(self._default_data, f)
            return self._default_data.copy()
        with open(self._data_file, "r") as f:
            return json.load(f)

    def _save(self) -> None:
        with open(self._data_file, "w") as f:
            json.dump(self._db, f, indent=4)

    def reload(self) -> None:
        self._db = self._load()

    def add(self, item: Any) -> Any:
        if hasattr(item, "model_dump"):
            item_dict = item.model_dump()
        elif isinstance(item, dict):
            item_dict = item
        else:
            raise ValueError("Item must have a model_dump() method")

        self._db.append(item_dict)
        self._save()
        return item

    def get_by_id(self, item_id: Any) -> Optional[dict]:
        for item in self._db:
            if item.get(self._id_field) == item_id:
                return item
        return None

    def get_all(self) -> List[dict]:
        return self._db.copy()

    def delete(self, item_id: Any) -> bool:
        for i, item in enumerate(self._db):
            if item.get(self._id_field) == item_id:
                del self._db[i]
                self._save()
                return True
        return False

    def update(self, item_id: Any, data: dict) -> Optional[dict]:
        for i, item in enumerate(self._db):
            if item.get(self._id_field) == item_id:
                self._db[i].update(data)
                self._save()
                return self._db[i]
        return None
