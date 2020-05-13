from GpsdStreamReader import GpsdStreamReader
import time
from dateutil import tz, parser
from AsyncSensorQuery import AsyncSensorQuery
from aiohttp import web
import threading
import random


def translateGPSTimeToLocal(gpstimestamp):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    utc = parser.parse(gpstimestamp)
    utc = utc.replace(tzinfo=from_zone)

    return utc.astimezone(to_zone)


gpsReader = None
sensorQuery = None

filename = None
file_length = 0


def doLogging():
    threading.Timer(60.0, doLogging).start()

    global filename, file_length, gpsReader, sensorQuery

    # Create a new file every 24 hours
    if filename is None or file_length > 1440:
        # Find new filename
        currentTime = translateGPSTimeToLocal(gpsReader.g_utc)
        new_name = str(currentTime.month) + "_" + str(currentTime.day) + "_"
        new_name += str(currentTime.year) + "_measures_" + str(random.randint(0, 1000000)) + ".csv"
        filename = new_name
        print("Starting new file", filename, "...")

        # write header
        file = open(filename, 'w+')
        file.write("time,lat,lng,pm25,pm10\n")
        file.close()

    print("[", str(translateGPSTimeToLocal(gpsReader.g_utc)), "] Logging current data to file")

    values = sensorQuery.getResult()

    file = open(filename, 'a')
    # file.write("time,lat,lng,pm2.5,pm10")
    file.write("\"" + str(translateGPSTimeToLocal(gpsReader.g_utc)) + "\","
               + str(gpsReader.g_lat) + "," + str(gpsReader.g_lng) + "," + str(values[0]) + "," + str(values[1]) + "\n")
    file.close()
    file_length += 1


async def onRequest(request):
    sendText = """<!doctype html><html><head><meta http-equiv="refresh" content="5"/></head><body><h3>Feinstaubsensor</h3>
Wenn diese Seite angezeigt wird ist der Sensor aktiv.<br>
Diese Seite aktualisiert sich <b>alle 5 Sekunden</b> automatisch.<br>
Die Feinstaubwerte werden minütlich in .csv Dateien im Unterordner log/ abgelegt.<br>
Die aktuellen Werte lauten:<br>
<h3>PM2.5, PM10<h3>
<h3>%pm25%, %pm10%<br><h3>
Die aktuelle GPS Position:<br>
%gps%<br>
Die aktuelle Uhrzeit (GPS umgerechnet in CET):<br>
%time%</body></html>"""

    values = sensorQuery.getResult()
    sendText = sendText.replace("%pm25%", str(values[0])).replace("%pm10%", str(values[1]))
    sendText = sendText.replace("%gps%", "lat: " + str(gpsReader.g_lat) + ", lng: " + str(gpsReader.g_lng))
    sendText = sendText.replace("%time%", str(translateGPSTimeToLocal(gpsReader.g_utc)))

    return web.Response(text=sendText, content_type="text/html")


if __name__ == "__main__":

    gpsReader = GpsdStreamReader()
    gpsReader.start()

    sensorQuery = AsyncSensorQuery()
    sensorQuery.start()

    print("Waiting for GPS Signal to get current time...")
    while gpsReader.g_utc == "" or gpsReader.g_utc is None or gpsReader.g_lat == "nan":
        time.sleep(5)
        print("No GPS signal yet, checking again in 5 seconds ...")
        # TODO check if working

    print("Signal found. Getting time and converting to CET time")
    currTime = translateGPSTimeToLocal(gpsReader.g_utc)
    print("Current time:", currTime)

    print("Starting logging to file (every minute)...")
    doLogging()

    print("Starting web server (0.0.0.0:8080)...")

    app = web.Application()
    app.add_routes([web.get('/', onRequest)])
    web.run_app(app)
