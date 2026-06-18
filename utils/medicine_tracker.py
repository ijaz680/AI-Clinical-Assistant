import json
import os
import datetime

MED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "medicines.json")
os.makedirs(os.path.dirname(MED_PATH), exist_ok=True)


def _load() -> list:
    if os.path.exists(MED_PATH):
        try:
            with open(MED_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save(data: list):
    with open(MED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_medicine(name: str, dosage: str, timing: str, duration: str, notes: str = ""):
    """Save a medicine to the tracker."""
    meds = _load()
    med = {
        "id": len(meds) + 1,
        "name": name,
        "dosage": dosage,
        "timing": timing,          # e.g. "Morning", "Night", "After meals"
        "duration": duration,
        "notes": notes,
        "added_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "active": True
    }
    meds.append(med)
    _save(meds)
    return med


def get_medicines(active_only: bool = False) -> list:
    meds = _load()
    if active_only:
        return [m for m in meds if m.get("active", True)]
    return meds


def toggle_medicine(med_id: int):
    meds = _load()
    for m in meds:
        if m["id"] == med_id:
            m["active"] = not m.get("active", True)
    _save(meds)


def delete_medicine(med_id: int):
    meds = _load()
    meds = [m for m in meds if m["id"] != med_id]
    _save(meds)
