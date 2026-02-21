import json
import uuid
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data.json"


def load_data():
    if not DATA_FILE.exists():
        return {"items": []}
    return json.loads(DATA_FILE.read_text())


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))


def create_item(item: dict):
    data = load_data()
    # auto-generate ID if not exists
    if "id" not in item:
        item["id"] = str(uuid.uuid4())
    # prevent duplicate ID (very rare, but safe)
    existing_ids = [i["id"] for i in data["items"]]
    while item["id"] in existing_ids:
        item["id"] = str(uuid.uuid4())
    data["items"].append(item)
    save_data(data)
    return item


def read_items():
    return load_data()["items"]


def update_item(item_id: str, new_data: dict):
    data = load_data()
    for idx, item in enumerate(data["items"]):
        if item["id"] == item_id:
            # keep the same ID
            new_data["id"] = item_id
            data["items"][idx] = new_data
            save_data(data)
            return new_data
    raise ValueError(f"Item with ID {item_id} not found")


def delete_item(item_id: str):
    data = load_data()
    for idx, item in enumerate(data["items"]):
        if item["id"] == item_id:
            removed = data["items"].pop(idx)
            save_data(data)
            return removed
    raise ValueError(f"Item with ID {item_id} not found")
