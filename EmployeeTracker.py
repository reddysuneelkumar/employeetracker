import streamlit as st
import calendar
from datetime import date

from EmployeeSelfDB import *
from EmployeeSelfService import *

st.set_page_config(page_title="Employee Tracker")

# =========================
# STATE INIT
# =========================
if "auth" not in st.session_state:
    st.session_state.auth = False

if "toast" not in st.session_state:
    st.session_state.toast = None

if "show_profile" not in st.session_state:
    st.session_state.show_profile = False

if "month" not in st.session_state:
    st.session_state.month = date.today().month

if "day" not in st.session_state:
    st.session_state.day = date.today().day  # ✅ FIX SAFE DEFAULT

# =========================
# INIT DB
# =========================
init_db()
init_pin_table()

# =========================
# TOAST
# =========================
if st.session_state.toast:
    msg, icon = st.session_state.toast
    st.toast(msg, icon=icon)
    st.session_state.toast = None

# =========================
# SETUP
# =========================
if not get_user_name() or not get_pin():

    st.title("Setup Your Tracker")

    name = st.text_input("Name")
    pin = st.text_input("PIN", type="password")
    confirm = st.text_input("Confirm PIN", type="password")

    if st.button("Save Setup"):
        if name and pin == confirm:
            save_user_name(name)
            save_pin(pin)
            st.session_state.auth = True
            st.session_state.toast = ("Setup complete ✅", "✅")
            st.rerun()
        else:
            st.error("Enter valid details")

    st.stop()

# =========================
# LOGIN
# =========================
if not st.session_state.auth:

    st.title("Login")

    pin = st.text_input("Enter PIN", type="password")

    if st.button("Login"):
        if pin == get_pin():
            st.session_state.auth = True
            st.session_state.toast = ("Login successful ✅", "🔓")
            st.rerun()
        else:
            st.error("Wrong PIN")

    st.stop()

# =========================
# MAIN
# =========================
records = load_records_db()
user = get_user_name()

year = date.today().year
month = st.session_state.month

# =========================
# HEADER
# =========================
c1, c2, c3 = st.columns([6,1,1])

with c1:
    st.title(f"{user}'s Tracker")

with c2:
    if st.button("👤", key="profile_btn"):
        st.session_state.show_profile = not st.session_state.show_profile

with c3:
    if st.button("⏻", key="logout_btn"):
        st.session_state.auth = False
        st.session_state.toast = ("Logged out", "🔌")
        st.rerun()

# =========================
# PROFILE
# =========================
if st.session_state.show_profile:
    new_name = st.text_input("Name", value=user)
    current_pin = st.text_input("Current PIN", type="password")
    new_pin = st.text_input("New PIN", type="password")

    if st.button("Update Profile"):

        if current_pin == get_pin():
            if new_pin:
                save_pin(new_pin)

            save_user_name(new_name)
            st.session_state.toast = ("Updated ✅", "✅")
        else:
            st.session_state.toast = ("Wrong PIN", "❌")

        st.rerun()

# =========================
# ANALYTICS
# =========================
a = calculate_analytics(records)

cols = st.columns(6)
cols[0].metric("Days", a["total_days"])
cols[1].metric("Good", a["good_days"])
cols[2].metric("Avg", a["avg_hours"])
cols[3].metric("Score", f"{a['success_rate']}%")
cols[4].metric("WFH", a["wfh_days"])
cols[5].metric("Leave", a["leave_days"])

# =========================
# YEAR OVERVIEW ✅ FIXED
# =========================
st.subheader(f"Year Overview - {year}")

months = list(calendar.month_abbr)[1:]
cols = st.columns(4)

for i, m in enumerate(months):
    idx = i + 1
    status = get_month_status(year, idx, records)

    if cols[i % 4].button(f"{status} {m}", key=f"month_{idx}"):
        st.session_state.month = idx
        st.session_state.day = 1
        st.session_state.toast = (f"{m} opened", "📅")
        st.rerun()

# =========================
# CALENDAR ✅ FIXED
# =========================
st.subheader(f"{calendar.month_name[month]} {year}")

# ✅ DAYS HEADER FIX
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
cols = st.columns(7)

for i in range(7):
    cols[i].markdown(f"**{days[i]}**")

def tile(d):

    key = str(date(year, month, d))

    if key in records:
        r = records[key]

        if r["status"] == "leave":
            return f"🟡 {d}\n\n6+h"

        if r["status"] == "wfh":
            return f"🔵 {d}\n\n6+h"

        if r["status"] == "work" and r["hours"] is not None:
            h = round(r["hours"], 1)
            icon = "🟢" if h >= 6 else "🔴"
            return f"{icon} {d}\n\n{h}h"

    return f"⚪ {d}"

cal = calendar.monthcalendar(year, month)

for week in cal:
    cols = st.columns(7)

    for i, d in enumerate(week):
        if d == 0:
            continue

        # ✅ UNIQUE KEY FIX
        if cols[i].button(tile(d), key=f"day_{year}_{month}_{d}"):
            st.session_state.day = d
            st.session_state.toast = (f"Selected {d}", "📌")
            st.rerun()

# =========================
# INPUT
# =========================
sel = date(year, month, st.session_state.day)

st.write(f"Selected: {sel}")

mode = st.radio("Type", ["Work Entry","Work From Home","Leave","No Data"])

in_t = st.time_input("In Time")
out_t = st.time_input("Out Time")

c1, c2 = st.columns(2)

# SAVE
with c1:
    if st.button("Save Entry"):
        save_record(sel, in_t, out_t, mode)
        st.session_state.toast = ("Saved ✅", "✅")
        st.rerun()

# CLEAR
with c2:
    confirm = st.checkbox("Confirm Clear")

    if st.button("Clear Data"):
        if confirm:
            import sqlite3
            conn = sqlite3.connect("employee_data.db")
            conn.execute("DELETE FROM records")
            conn.commit()
            conn.close()

            st.session_state.toast = ("Cleared ✅", "🧹")
        else:
            st.session_state.toast = ("Confirm first", "⚠️")

        st.rerun()
