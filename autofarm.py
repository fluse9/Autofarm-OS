import serial
import json
from datetime import datetime
import Databases
from psycopg2 import OperationalError
import Terrafarm

class Status(object):
    arduino = None
    unit_id = ""
    max_par = 0
    timestamp = None
    mist_io = None
    mist_pressure = 0.0
    transducer_voltage = 0.0
    water_use = 0.0
    nutrient_use = 0.0
    tank0_low = None
    tank1_low = None
    tank2_low = None
    tank3_low = None
    reservoir_low = None
    reservoir_high = None
    reservoir_temp = 0.0
    reservoir_ph = 0.0
    nutrient_concentration = 0
    germ_temp = 0.0
    germ_humidity = 0.0
    germ_dewpoint = 0.0
    germ_vpd = 0.0
    grow_temp = 0.0
    grow_humidity = 0.0
    grow_dewpoint = 0.0
    grow_vpd = 0.0
    led_io = None
    led_blue = 0.0
    led_red = 0.0
    led_green = 0.0
    led_white = 0.0
    led_uv = 0.0
    statuslist = {}
    values = []

    def __init__(self):
        # initialize and define sensor variable at specified port and baud rate and timeout size
        self.arduino = serial.Serial('/dev/ttyACM1', 115200, timeout=.1)
        self.unit_id = "AL9tw"
        self.max_par = 344.1
        self.timestamp = None
        self.mist_io = None
        self.mist_pressure = 0.0
        self.transducer_voltage = 0.0
        self.water_use = 0.0
        self.nutrient_use = 0.0
        self.tank0_low = None
        self.tank1_low = None
        self.tank2_low = None
        self.tank3_low = None
        self.reservoir_low = None
        self.reservoir_high = None
        self.reservoir_ph = 0.0
        self.nutrient_concentration = 4
        self.germ_temp = 0.0
        self.germ_humidity = 0.0
        self.germ_dewpoint = 0.0
        self.germ_vpd = 0.0
        self.grow_temp = 0.0
        self.grow_humidity = 0.0
        self.grow_dewpoint = 0.0
        self.grow_vpd = 0.0
        self.led_io = None
        self.led_blue = 0.0
        self.led_red = 0.0
        self.led_green = 0.0
        self.led_white = 0.0
        self.led_uv = 0.0
        self.statuslist = {}
        self.values = []

        self.readStatus()

    def isFloat(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def isInt(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def readStatus(self):
        # initialize count list to store current time values for synced timer
        minutecount = []

        # initialize totaldata list to store all data values in order they are received
        totaldata = []

        # loop that perpetually reads, decodes, and updates decodeddata variable with current sensor data
        while True:
            # reads, decodes, and interprets arduino data to set variables to send to database
            rawdata = self.arduino.readline()
            cleandata = rawdata.rstrip()  # gets rid of '\n' in output
            decodeddata = cleandata.decode("utf-8")  # converts byte like variable to string variable
            splitlist = decodeddata.split()

            if (str(splitlist) != '[]'):
                totaldata.append(splitlist[0])
                lastindex = totaldata[len(totaldata) - 1]
                nextlastindex = totaldata[len(totaldata) - 2]

                if (nextlastindex == 'VOLTAGE:' and (self.isFloat(lastindex) == True or self.isInt(lastindex) == True)):
                    self.transducer_voltage = float(lastindex)
                if (nextlastindex == 'PRESSURE:' and (self.isFloat(lastindex) == True or self.isInt(lastindex) == True)):
                    self.mist_pressure = float(lastindex)
                if (nextlastindex == 'LIQUIDLEVEL:' and (self.isFloat(lastindex) == True or self.isInt(lastindex) == True)):
                    if(int(lastindex) == 0):
                        self.tank0_low = False
                    if(int(lastindex) == 1):
                        self.tank0_low = True
                if (nextlastindex == 'PH:' and (self.isFloat(lastindex) == True or self.isInt(lastindex) == True)):
                    self.reservoir_ph = float(lastindex)
                if (nextlastindex == 'HUMIDITY:' and (self.isFloat(lastindex) == True or self.isInt(lastindex) == True)):
                    self.germ_humidity = float(lastindex)
                    self.grow_humidity = float(lastindex)
                if (nextlastindex == 'AIRTEMP:' and (self.isFloat(lastindex) == True or self.isInt(lastindex) == True)):
                    self.germ_temp = float(lastindex)
                    self.grow_temp = float(lastindex)
                if (nextlastindex == 'DEWPOINT:' and (self.isFloat(lastindex) == True or self.isInt(lastindex) == True)):
                    self.germ_dewpoint = float(lastindex)
                    self.grow_dewpoint = float(lastindex)
                if (nextlastindex == 'VPD:' and (self.isFloat(lastindex) == True or self.isInt(lastindex) == True)):
                    self.germ_vpd = float(lastindex)
                    self.grow_vpd = float(lastindex)
                self.timestamp = datetime.utcnow()  # updates timestamp

                if(self.timestamp.hour >= 13 or self.timestamp.hour <= 5):
                    self.led_io = True
                else:
                    self.led_io = False
                if(self.led_io == True):
                    self.led_red = 0.5*self.max_par
                    self.led_blue = 0.5*self.max_par
                else:
                    self.led_red = 0
                    self.led_blue = 0

                

                # logs Terrafarm status once per second
                currenttime = datetime.utcnow()
                minutes = currenttime.minute
                seconds = currenttime.second
                minutecount.append(minutes)
                currentminute = minutecount[len(minutecount) - 1]
                previousminute = minutecount[len(minutecount) - 2]

                if(currentminute - previousminute == 1):
                    self.prepData()
                    self.logStatus()

    def prepData(self):
        # creates tuple of all status variables over last minute to insert into the Terrafarm unit's status list in the "units" collection
        self.status_list = {
            'mist_pressure': self.mist_pressure,
            'tank0_low': self.tank0_low,
            'tank1_low': self.tank1_low,
            'tank2_low': self.tank2_low,
            'tank3_low': self.tank3_low,
            'reservoir_low': self.reservoir_low,
            'reservoir_high': self.reservoir_high,
            'reservoir_ph': self.reservoir_ph,
            'nutrient_concentration': self.nutrient_concentration,
            'germ_temp': self.germ_temp,
            'germ_humidity': self.germ_humidity,
            'germ_dewpoint': self.germ_dewpoint,
            'germ_vpd': self.germ_vpd,
            'grow_temp': self.grow_temp,
            'grow_humidity': self.grow_humidity,
            'grow_dewpoint': self.grow_dewpoint,
            'grow_vpd': self.grow_vpd,
            'led_io': self.led_io,
            'led_blue': self.led_blue,
            'led_red': self.led_red,
            'led_green': self.led_green,
            'led_white': self.led_white,
            'led_uv': self.led_uv,
        }

        print(self.status_list)
        status = json.dumps(self.status_list)
        self.values = [{'unit_id': self.unit_id, 'timestamp': self.timestamp, 'status': status}]

    def logStatus(self):
        while True:
            try:
                # inserts the dictionary into the document
                # opens connection to Postgres database with all farm unit data
                host = "terrafarm.cddahydnt6ir.us-east-2.rds.amazonaws.com"
                port = "5432"
                username = "username"
                password = "password"
                dbname = "terrafarm"
                tablename = "units.status"
                Databases.PostgresConnection(host, port, username, password, dbname).insertRow(tablename, tuple(self.values))

                self.values = []
            except OperationalError as error:
                continue
            break

Status()
