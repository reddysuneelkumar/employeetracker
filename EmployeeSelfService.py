from datetime import datetime
from EmployeeSelfDB import save_record_db

def calc_hours(d, in_time, out_time):
    if not in_time or not out_time:
        return None

    return round(
        (datetime.combine(d, out_time) - datetime.combine(d, in_time)).total_seconds() / 3600,
        2
    )

def save_record(d, in_time, out_time, mode):

    m = mode.lower()

    if m == "work entry":
        status = "work"
    elif m == "work from home":
        status = "wfh"
    elif m == "leave":
        status = "leave"
    else:
        status = "nodata"

    hours = None
    if status in ["work", "wfh"]:
        hours = calc_hours(d, in_time, out_time)

    in_str = in_time.strftime("%H:%M") if in_time else None
    out_str = out_time.strftime("%H:%M") if out_time else None

    save_record_db(d, in_str, out_str, hours, status)


def calculate_analytics(records):

    total_days = 0
    good_days = 0
    total_hours = 0
    wfh = 0
    leave = 0

    for r in records.values():

        if r["status"] == "nodata":
            continue

        total_days += 1

        if r["status"] == "leave":
            leave += 1
            good_days += 1

        elif r["status"] == "wfh":
            wfh += 1
            good_days += 1

        elif r["status"] == "work" and r["hours"]:
            total_hours += r["hours"]

            if r["hours"] >= 6:
                good_days += 1

    avg = round(total_hours / total_days, 2) if total_days else 0
    score = round((good_days / total_days) * 100, 1) if total_days else 0

    return {
        "total_days": total_days,
        "good_days": good_days,
        "avg_hours": avg,
        "success_rate": score,
        "wfh_days": wfh,
        "leave_days": leave
    }


def get_month_status(year, m, records):

    total = 0
    good = 0

    for k, r in records.items():
        if k.startswith(f"{year}-{str(m).zfill(2)}"):

            if r["status"] == "nodata":
                continue

            total += 1

            if r["status"] in ["leave", "wfh"]:
                good += 1
            elif r["hours"] and r["hours"] >= 6:
                good += 1

    if total == 0:
        return "⚪"

    return "🟢" if good / total >= 0.7 else "🔴"
