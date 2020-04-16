from gps import *
import threading


# from https://github.com/custom-build-robots/Feinstaubsensor/

# Klasse um auf den GPSD Stream via Thread zuzugreifen.
class GpsdStreamReader(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.session = gps(mode=WATCH_ENABLE)
        self.g_utc = session.utc
        self.g_lat = session.fix.latitude
        self.g_lng = session.fix.longitude

        self.current_value = None
        # Der Thread wird ausgefuehrt
        self.running = True

    def run(self):
        while self.running:
            # Lese den naechsten Datensatz von GPSD
            self.session.next()
            self.g_utc = session.utc
            self.g_lat = session.fix.latitude
            self.g_lng = session.fix.longitude
