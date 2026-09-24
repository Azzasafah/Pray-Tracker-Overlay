import sys
import threading
import time

class SoundNotifier:
    """Provides non-blocking gentle chimes for prayer time alerts using Windows sound system."""

    @staticmethod
    def play_adhan_chime(enabled: bool = True):
        """Plays a gentle 3-step notification chime asynchronously."""
        if not enabled:
            return

        def _worker():
            try:
                if sys.platform == "win32":
                    import winsound
                    # Melody: E5 (659Hz) -> G#5 (830Hz) -> B5 (988Hz) gentle rising chime
                    chimes = [
                        (659, 150),
                        (830, 150),
                        (988, 320)
                    ]
                    for freq, dur in chimes:
                        winsound.Beep(freq, dur)
                        time.sleep(0.04)
                else:
                    # Non-Windows fallback (system bell)
                    print("\a", end="", flush=True)
            except Exception as e:
                print(f"[Sound] Error playing chime: {e}")

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    @staticmethod
    def play_subtle_tick(enabled: bool = True):
        """Plays a very subtle click/tick for testing or minor events."""
        if not enabled:
            return

        def _worker():
            try:
                if sys.platform == "win32":
                    import winsound
                    winsound.Beep(880, 80)
            except Exception as e:
                print(f"[Sound] Error playing tick: {e}")

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
