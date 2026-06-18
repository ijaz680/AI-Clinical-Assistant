import json
import os
from datetime import datetime

MEMORY_FILE = "memory/patient_memory.json"
os.makedirs("memory", exist_ok=True)


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "chat_history": [],
        "medicines": [],
        "conditions": [],
        "created_at": datetime.now().isoformat()
    }


def save_memory(memory):
    memory["last_updated"] = datetime.now().isoformat()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def add_message(memory, role, content):
    memory["chat_history"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_memory(memory)


def add_medicine(memory, name, dose, times, start_date):
    memory["medicines"].append({
        "name": name,
        "dose": dose,
        "times": times,
        "start_date": start_date,
        "taken_log": {}
    })
    save_memory(memory)


def remove_medicine(memory, name):
    memory["medicines"] = [m for m in memory["medicines"] if m["name"] != name]
    save_memory(memory)


def log_taken(memory, med_name, date, time_slot):
    for med in memory["medicines"]:
        if med["name"] == med_name:
            if date not in med["taken_log"]:
                med["taken_log"][date] = []
            if time_slot not in med["taken_log"][date]:
                med["taken_log"][date].append(time_slot)
    save_memory(memory)


def clear_memory():
    fresh = {
        "chat_history": [],
        "medicines": [],
        "conditions": [],
        "created_at": datetime.now().isoformat()
    }
    save_memory(fresh)
    return fresh
