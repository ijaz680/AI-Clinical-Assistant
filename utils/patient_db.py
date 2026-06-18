import json
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "patient_db.json")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def _load_db() -> dict:
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"diagnoses": [], "reports": []}


def _save_db(db: dict):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def save_diagnosis(query: str, response: str, lang: str = "English"):
    """Save a diagnosis/chat entry to history."""
    db = _load_db()
    entry = {
        "id": len(db["diagnoses"]) + 1,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "query": query[:200],
        "response": response[:600],
        "lang": lang
    }
    db["diagnoses"].insert(0, entry)
    # Keep last 100
    db["diagnoses"] = db["diagnoses"][:100]
    _save_db(db)


def get_history(limit: int = 20) -> list:
    """Get recent diagnosis history."""
    db = _load_db()
    return db["diagnoses"][:limit]


def clear_history():
    """Clear all diagnosis history."""
    db = _load_db()
    db["diagnoses"] = []
    _save_db(db)
