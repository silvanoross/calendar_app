import streamlit as st
from datetime import date, datetime, timedelta
import calendar
import uuid

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quick Event Planner",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 480px !important; margin: auto; }

.app-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1a1a2e;
    text-align: center;
    margin-bottom: 0.1rem;
}
.app-sub {
    text-align: center;
    color: #666;
    font-size: 0.85rem;
    margin-bottom: 1.5rem;
}
.month-label {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: #1a1a2e;
    min-width: 160px;
    text-align: center;
    padding-top: 6px;
}
.cal-header-cell {
    text-align: center;
    font-size: 0.7rem;
    font-weight: 600;
    color: #999;
    padding: 4px 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.dates-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 0.5rem 0 1rem 0;
}
.date-pill {
    background: #ede9ff;
    color: #6c47ff;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
}
.section-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #999;
    margin-bottom: 0.3rem;
    margin-top: 0.8rem;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #6c47ff, #a678ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 1.5rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    font-family: 'DM Sans', sans-serif !important;
    box-shadow: 0 4px 15px rgba(108,71,255,0.35) !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 10px !important;
    border: 1.5px solid #e0d9ff !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6c47ff !important;
    box-shadow: 0 0 0 2px rgba(108,71,255,0.15) !important;
}
section[data-testid="column"] .stButton button {
    border-radius: 50% !important;
    padding: 0 !important;
    min-height: 38px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
}
section[data-testid="column"] .stButton button[kind="primary"] {
    background: linear-gradient(135deg, #6c47ff, #a678ff) !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(108,71,255,0.4) !important;
}
section[data-testid="column"] .stButton button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #e5e0ff !important;
    color: #1a1a2e !important;
}
section[data-testid="column"] .stButton button[kind="secondary"]:hover {
    background: #ede9ff !important;
    border-color: #6c47ff !important;
}
div[data-testid="stHorizontalBlock"] > div { padding: 0 2px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
today = date.today()
if "selected_dates" not in st.session_state:
    st.session_state.selected_dates = set()
if "view_year" not in st.session_state:
    st.session_state.view_year = today.year
if "view_month" not in st.session_state:
    st.session_state.view_month = today.month

# ── ICS builder ───────────────────────────────────────────────────────────────
def build_ics(dates, title, description, location, start_time, end_time, all_day):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//QuickEventPlanner//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    for d in sorted(dates):
        uid = str(uuid.uuid4())
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        lines.append(f"SUMMARY:{title}")
        if description:
            desc_escaped = description.replace("\n", "\\n")
            lines.append(f"DESCRIPTION:{desc_escaped}")
        if location:
            lines.append(f"LOCATION:{location}")
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        lines.append(f"DTSTAMP:{dtstamp}")
        if all_day:
            lines.append(f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}")
            next_day = d + timedelta(days=1)
            lines.append(f"DTEND;VALUE=DATE:{next_day.strftime('%Y%m%d')}")
        else:
            dt_start = datetime.combine(d, start_time)
            dt_end = datetime.combine(d, end_time)
            lines.append(f"DTSTART:{dt_start.strftime('%Y%m%dT%H%M%S')}")
            lines.append(f"DTEND:{dt_end.strftime('%Y%m%dT%H%M%S')}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="app-title">📅 Event Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">Tap dates · Add event · Export .ics</div>', unsafe_allow_html=True)

# ── Month navigation ───────────────────────────────────────────────────────────
col_prev, col_mid, col_next = st.columns([1, 3, 1])
with col_prev:
    if st.button("◀", use_container_width=True, key="prev_month"):
        if st.session_state.view_month == 1:
            st.session_state.view_month = 12
            st.session_state.view_year -= 1
        else:
            st.session_state.view_month -= 1
        st.rerun()
with col_mid:
    month_name = date(st.session_state.view_year, st.session_state.view_month, 1).strftime("%B %Y")
    st.markdown(f'<div class="month-label">{month_name}</div>', unsafe_allow_html=True)
with col_next:
    if st.button("▶", use_container_width=True, key="next_month"):
        if st.session_state.view_month == 12:
            st.session_state.view_month = 1
            st.session_state.view_year += 1
        else:
            st.session_state.view_month += 1
        st.rerun()

# ── Calendar grid ──────────────────────────────────────────────────────────────
year = st.session_state.view_year
month = st.session_state.view_month

day_names = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
header_cols = st.columns(7)
for i, d in enumerate(day_names):
    with header_cols[i]:
        st.markdown(f'<div class="cal-header-cell">{d}</div>', unsafe_allow_html=True)

cal = calendar.monthcalendar(year, month)
for week in cal:
    week_cols = st.columns(7)
    for i, day_num in enumerate(week):
        with week_cols[i]:
            if day_num == 0:
                st.markdown('<div style="aspect-ratio:1"></div>', unsafe_allow_html=True)
            else:
                d = date(year, month, day_num)
                is_selected = d in st.session_state.selected_dates
                clicked = st.button(
                    str(day_num),
                    key=f"day_{year}_{month}_{day_num}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                )
                if clicked:
                    if d in st.session_state.selected_dates:
                        st.session_state.selected_dates.remove(d)
                    else:
                        st.session_state.selected_dates.add(d)
                    st.rerun()

# ── Selected dates display ─────────────────────────────────────────────────────
if st.session_state.selected_dates:
    sorted_dates = sorted(st.session_state.selected_dates)
    pills_html = '<div class="dates-container">'
    for d in sorted_dates:
        pills_html += f'<span class="date-pill">{d.strftime("%b %d")}</span>'
    pills_html += '</div>'
    st.markdown(f'<div class="section-label">✓ {len(sorted_dates)} date{"s" if len(sorted_dates)>1 else ""} selected</div>', unsafe_allow_html=True)
    st.markdown(pills_html, unsafe_allow_html=True)
    if st.button("🗑 Clear all dates", use_container_width=False):
        st.session_state.selected_dates.clear()
        st.rerun()
else:
    st.markdown('<div style="text-align:center;color:#bbb;padding:0.5rem 0 1rem;font-size:0.9rem;">Tap days above to select them</div>', unsafe_allow_html=True)

# ── Event details ──────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-label">Event Details</div>', unsafe_allow_html=True)

event_title = st.text_input("Event title *", placeholder="e.g. Team Standup", label_visibility="collapsed")
st.caption("Event title")

event_desc = st.text_area("Description (optional)", placeholder="Notes, agenda, links…", height=80, label_visibility="collapsed")
st.caption("Description (optional)")

event_location = st.text_input("Location (optional)", placeholder="Room 3B / Zoom / etc.", label_visibility="collapsed")
st.caption("Location (optional)")

all_day = st.checkbox("All-day event", value=True)

if not all_day:
    tc1, tc2 = st.columns(2)
    with tc1:
        start_time = st.time_input("Start time", value=datetime.strptime("09:00", "%H:%M").time())
    with tc2:
        end_time = st.time_input("End time", value=datetime.strptime("10:00", "%H:%M").time())
else:
    start_time = datetime.strptime("09:00", "%H:%M").time()
    end_time = datetime.strptime("10:00", "%H:%M").time()

# ── Export ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

ready = len(st.session_state.selected_dates) > 0 and event_title.strip()

if ready:
    ics_content = build_ics(
        st.session_state.selected_dates,
        event_title.strip(),
        event_desc.strip(),
        event_location.strip(),
        start_time,
        end_time,
        all_day,
    )
    n = len(st.session_state.selected_dates)
    st.download_button(
        label=f"⬇ Export {n} Event{'s' if n>1 else ''} as .ics",
        data=ics_content,
        file_name="events.ics",
        mime="text/calendar",
        use_container_width=True,
    )
    st.caption("Open the downloaded file to import into Google Calendar, Apple Calendar, Outlook, etc.")
else:
    missing = []
    if not st.session_state.selected_dates:
        missing.append("select at least one date")
    if not event_title.strip():
        missing.append("add an event title")
    st.info(f"To export, {' and '.join(missing)}.")
