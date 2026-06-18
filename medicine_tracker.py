from datetime import datetime


def get_medicine_status(medicines):
    today = datetime.now().strftime("%Y-%m-%d")
    now_hour = datetime.now().hour
    now_minute = datetime.now().minute
    status = []

    for med in medicines:
        taken_today = med["taken_log"].get(today, [])
        missed = []
        upcoming = []

        for t in med["times"]:
            try:
                hour, minute = map(int, t.split(":"))
            except ValueError:
                continue

            if t not in taken_today:
                if (hour < now_hour) or (hour == now_hour and minute <= now_minute):
                    missed.append(t)
                else:
                    upcoming.append(t)

        status.append({
            "name": med["name"],
            "dose": med["dose"],
            "times": med["times"],
            "taken": taken_today,
            "missed": missed,
            "upcoming": upcoming,
            "start_date": med.get("start_date", "")
        })

    return status


def format_alerts(status):
    alerts = []
    for s in status:
        for t in s["missed"]:
            alerts.append({
                "type": "missed",
                "text": f"MISSED: {s['name']} {s['dose']} — was due at {t}"
            })
        for t in s["upcoming"]:
            alerts.append({
                "type": "upcoming",
                "text": f"UPCOMING: {s['name']} {s['dose']} — take at {t}"
            })
        for t in s["taken"]:
            alerts.append({
                "type": "taken",
                "text": f"TAKEN: {s['name']} {s['dose']} — taken at {t}"
            })
    return alerts


def get_compliance_summary(medicines):
    """Returns how many doses were taken vs total for last 7 days."""
    from datetime import timedelta
    today = datetime.now().date()
    summary = []

    for med in medicines:
        total_expected = 0
        total_taken = 0
        for i in range(7):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            expected = len(med["times"])
            taken = len(med["taken_log"].get(day, []))
            total_expected += expected
            total_taken += taken

        pct = round((total_taken / total_expected * 100) if total_expected > 0 else 0)
        summary.append({
            "name": med["name"],
            "dose": med["dose"],
            "compliance_pct": pct,
            "taken_7d": total_taken,
            "expected_7d": total_expected
        })
    return summary
