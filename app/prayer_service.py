import datetime
from typing import Dict, List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal

from app.api import MyQuranAPI

# Standard sequence of daily prayers
PRAYER_KEYS = ["subuh", "terbit", "dzuhur", "ashar", "maghrib", "isya"]
PRAYER_LABELS = {
    "imsak": "IMSAK",
    "subuh": "SUBUH",
    "terbit": "TERBIT",
    "dhuha": "DHUHA",
    "dzuhur": "DZUHUR",
    "ashar": "ASHAR",
    "maghrib": "MAGHRIB",
    "isya": "ISYA",
    "third_night": "1/3 MALAM"
}

class PrayerService(QObject):
    """
    Manages prayer schedule state, real-time calculations,
    countdown timing, 1/3 malam terakhir computation, and alert triggers.
    """
    # Signals
    schedule_updated = pyqtSignal(dict, bool)  # (schedule_dict, is_online)
    tick = pyqtSignal(dict)  # State update every second
    prayer_alarm = pyqtSignal(str)  # Prayer name when time arrives

    def __init__(self, city_id: str = "1608", show_imsak: bool = False, show_third_night: bool = True):
        super().__init__()
        self.city_id = city_id
        self.show_imsak = show_imsak
        self.show_third_night = show_third_night
        self.schedule: Optional[Dict] = None
        self.is_online: bool = False
        self.current_date: Optional[datetime.date] = None

        # Track which prayers have already triggered an alarm today
        self.triggered_alarms: set = set()

    def set_city(self, city_id: str):
        self.city_id = city_id
        self.refresh_schedule(force=True)

    def refresh_schedule(self, force: bool = False):
        """Fetches current schedule for self.city_id and today's date."""
        today = datetime.date.today()
        sched, is_online = MyQuranAPI.get_schedule(self.city_id, today)
        if sched:
            self.schedule = sched
            self.is_online = is_online
            if self.current_date != today:
                self.current_date = today
                self.triggered_alarms.clear()
            self.schedule_updated.emit(self.schedule, self.is_online)

    def calculate_last_third_night(self, maghrib_str: str, subuh_str: str, now: datetime.datetime) -> Optional[dict]:
        """
        Calculates the Last Third of the Night (1/3 Malam Terakhir) based on Maghrib and Subuh.
        In Islamic tradition:
          Night begins at sunset (Maghrib) and ends at dawn (Subuh / Fajr).
          Duration = Subuh - Maghrib.
          1/3 Malam Terakhir starts at Subuh - (Duration / 3).
        """
        try:
            m_h, m_m = map(int, maghrib_str.split(":"))
            s_h, s_m = map(int, subuh_str.split(":"))
            today = now.date()

            today_subuh = datetime.datetime(today.year, today.month, today.day, s_h, s_m, 0)

            # Determine whether current time belongs to the night that started yesterday
            # or the night that starts today
            if now < today_subuh:
                # Night started yesterday evening and ends this morning at Subuh
                yesterday = today - datetime.timedelta(days=1)
                maghrib_dt = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, m_h, m_m, 0)
                subuh_dt = today_subuh
            else:
                # Night starts today evening at Maghrib and ends tomorrow morning at Subuh
                maghrib_dt = datetime.datetime(today.year, today.month, today.day, m_h, m_m, 0)
                tomorrow = today + datetime.timedelta(days=1)
                subuh_dt = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, s_h, s_m, 0)

            night_duration = subuh_dt - maghrib_dt
            one_third = night_duration / 3
            third_start_dt = subuh_dt - one_third
            midnight_dt = maghrib_dt + (night_duration / 2)

            is_active_now = (third_start_dt <= now < subuh_dt)

            return {
                "start_str": third_start_dt.strftime("%H:%M"),
                "end_str": subuh_dt.strftime("%H:%M"),
                "midnight_str": midnight_dt.strftime("%H:%M"),
                "start_dt": third_start_dt,
                "end_dt": subuh_dt,
                "is_active_now": is_active_now,
                "night_hours": round(night_duration.total_seconds() / 3600, 2),
            }
        except Exception as e:
            print(f"[PrayerService] Error calculating 1/3 night: {e}")
            return None

    def update_tick(self):
        """
        Called every second by the UI timer.
        Calculates countdown, next prayer, 1/3 malam terakhir, and triggers alarm if time hits.
        """
        now = datetime.datetime.now()
        today = now.date()

        # Day change detection: auto-fetch new schedule at midnight
        if self.current_date != today or not self.schedule:
            self.refresh_schedule()

        if not self.schedule:
            state = {
                "has_data": False,
                "current_time": now.strftime("%H:%M:%S"),
                "date_display": now.strftime("%A, %d %b %Y"),
                "next_prayer": "MEMUAT...",
                "next_time": "--:--",
                "countdown_str": "--:--:--",
                "countdown_seconds": 0,
                "is_prayer_now": False,
                "prayer_items": [],
                "third_night": None,
            }
            self.tick.emit(state)
            return

        # Parse prayer times for today
        prayers_to_check = (["imsak"] if self.show_imsak else []) + list(PRAYER_KEYS)
        prayer_datetimes: List[Tuple[str, datetime.datetime]] = []

        for key in prayers_to_check:
            raw_time = self.schedule.get(key)
            if raw_time and ":" in raw_time:
                try:
                    parts = raw_time.split(":")
                    p_dt = datetime.datetime(
                        today.year, today.month, today.day,
                        int(parts[0]), int(parts[1]), 0
                    )
                    prayer_datetimes.append((key, p_dt))
                except Exception as e:
                    print(f"[PrayerService] Error parsing time for {key}: {e}")

        # Find next upcoming regular prayer
        next_prayer_key = None
        next_prayer_dt = None

        for i, (key, dt) in enumerate(prayer_datetimes):
            if dt > now:
                next_prayer_key = key
                next_prayer_dt = dt
                break

        # If all prayers today have passed, next prayer is Subuh tomorrow
        if next_prayer_dt is None and prayer_datetimes:
            first_key, first_dt = prayer_datetimes[0]
            next_prayer_key = first_key
            next_prayer_dt = first_dt + datetime.timedelta(days=1)

        # Calculate countdown
        if next_prayer_dt:
            diff = next_prayer_dt - now
            total_seconds = max(0, int(diff.total_seconds()))
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            countdown_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            total_seconds = 0
            countdown_str = "--:--:--"

        # Check for alarm: within 60 seconds after prayer start
        is_prayer_now = False
        current_active_prayer = None

        for key, dt in prayer_datetimes:
            sec_diff = (now - dt).total_seconds()
            if 0 <= sec_diff <= 60:
                is_prayer_now = True
                current_active_prayer = key
                if key not in self.triggered_alarms:
                    self.triggered_alarms.add(key)
                    self.prayer_alarm.emit(PRAYER_LABELS.get(key, key.upper()))

        # Calculate 1/3 Malam Terakhir
        maghrib_str = self.schedule.get("maghrib", "17:30")
        subuh_str = self.schedule.get("subuh", "04:05")
        third_night_info = self.calculate_last_third_night(maghrib_str, subuh_str, now)

        # Build list of items for UI table / grid
        items = []
        for key in prayers_to_check:
            p_time = self.schedule.get(key, "--:--")
            is_next = (key == next_prayer_key)
            is_active = (key == current_active_prayer) and is_prayer_now

            is_past = False
            for pk, dt in prayer_datetimes:
                if pk == key and dt < now and not is_active:
                    is_past = True
                    break

            items.append({
                "key": key,
                "label": PRAYER_LABELS.get(key, key.upper()),
                "time": p_time,
                "is_next": is_next,
                "is_active": is_active,
                "is_past": is_past,
            })

        # Append 1/3 Malam card if enabled
        if self.show_third_night and third_night_info:
            is_active_third = third_night_info["is_active_now"]
            items.append({
                "key": "third_night",
                "label": "1/3 MALAM",
                "time": third_night_info["start_str"],
                "is_next": False,
                "is_active": is_active_third,
                "is_past": False if is_active_third else (now >= third_night_info["end_dt"]),
            })

        state = {
            "has_data": True,
            "city_name": self.schedule.get("lokasi", "KAB. JOMBANG"),
            "current_time": now.strftime("%H:%M:%S"),
            "date_display": now.strftime("%A, %d %b %Y"),
            "next_prayer": PRAYER_LABELS.get(next_prayer_key, "SUBUH") if next_prayer_key else "--",
            "next_time": next_prayer_dt.strftime("%H:%M") if next_prayer_dt else "--:--",
            "countdown_str": countdown_str,
            "countdown_seconds": total_seconds,
            "is_prayer_now": is_prayer_now,
            "active_prayer_name": PRAYER_LABELS.get(current_active_prayer, "") if current_active_prayer else "",
            "prayer_items": items,
            "third_night": third_night_info,
            "is_online": self.is_online,
        }
        self.tick.emit(state)
