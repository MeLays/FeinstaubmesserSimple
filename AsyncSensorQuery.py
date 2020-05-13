from SDS011 import SDS011
import threading
import time


class AsyncSensorQuery(threading.Thread):

    def __init__(self, serialport="/dev/ttyUSB0"):
        threading.Thread.__init__(self)
        self.sensor = SDS011(serialport, use_query_mode=True)
        self.result = (0., 0.)

    def run(self):
        time.sleep(5)
        print("sensor is being queried ...")
        self.result = self.sensor.query()
        print("pm2.5:", self.result[0], "pm10:", self.result[1])

    def getResult(self):
        return self.result
