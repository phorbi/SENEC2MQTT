"""
Bridge zwischen Senec Speicher und MQTT
"""

__author__ = "Patrick Horbach"
__copyright__ = "Copyright 2022, Patrick Horbach"
__credits__ = ["Nicolas Inden", "Mikołaj Chwalisz"]
__license__ = "Apache-2.0 License"
__version__ = "0.2.0"
__maintainer__ = "Patrick Horbach"
__email__ = ""
__status__ = "Production"


import time
import paho.mqtt.client as mqtt
import Senec
from queue import Queue
import math

BROKER_IP = "192.168.10.100"
BROKER_PORT = 1883
SENEC_IP = "192.168.10.65"

# The callback for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    # Print result of connection attempt
    print("Connected with result code {0}".format(str(rc)))
    # Subscribe to the topic
    client.subscribe("Keller/Solar/control/SENEC2MQTTInterval")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == "Keller/Solar/control/SENEC2MQTTInterval":
        q.put(int(msg.payload.decode("utf-8")))
        print("Intervall vom MQTT: " + str(msg.payload.decode("utf-8")))


client = mqtt.Client("SENEC-openWB-bridge")
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
client.connect(BROKER_IP, BROKER_PORT)  # connect to broker
q = Queue()  # we use a queue to get date from the on_message callback to the main
intervall = 2


# connect to Senec
info = Senec.SenecAPI(SENEC_IP)

# go on forever
client.loop_start()
while True:

    while not q.empty():
        intervall = q.get()
    try:
        # get Data from Senec
        data_dict = info.get_values()

        # openWB PV-Modul
        # PV-Leistung in W, int, positiv
        client.publish("openWB/set/pv/1/W", int(data_dict['ENERGY']['GUI_INVERTER_POWER']))
        print("inverter power: ", int(-1*data_dict['ENERGY']['GUI_INVERTER_POWER']))
        # Erzeugte Energie in Wh, float, nur positiv
        # client.publish("openWB/set/pv/1/WhCounter", 1000 * data_dict['STATISTIC']['LIVE_PV_GEN'])

        # openWB Batterie
        # Speicherleistung in Wall, int, positiv Ladung, negativ Entladung
        client.publish("openWB/set/houseBattery/W", int(data_dict['ENERGY']['GUI_BAT_DATA_POWER']))
        # Geladene Energie in Wh, float, nur positiv
        # client.publish("openWB/set/houseBattery/WhImported", 1000 * data_dict['STATISTIC']['LIVE_BAT_CHARGE_MASTER'])
        # Entladene Energie in Wh, float nur positiv
        # client.publish("openWB/set/houseBattery/WhExported", 1000 * data_dict['STATISTIC']['LIVE_BAT_DISCHARGE_MASTER'])
        # Ladestand des Speichers, int, 0-100
        client.publish("openWB/set/houseBattery/%Soc", int(data_dict['ENERGY']['GUI_BAT_DATA_FUEL_CHARGE']))

        # openWB Strombezugsmodul
        # Bezugsleistung in Watt, int, positiv Bezug, negativ Einspeisung
        client.publish("openWB/set/evu/W", int(data_dict['ENERGY']['GUI_GRID_POW']))
        # Strom in Ampere für Phase1, float, Punkt als Trenner, positiv Bezug, negativ Einspeisung; SENEC liefert den Strom ohne VZ, daher nehmen wir das VZ von der Leistung
        client.publish("openWB/set/evu/APhase1", math.copysign(data_dict['PM1OBJ1']['I_AC'][0], data_dict['PM1OBJ1']['P_AC'][0]))
        # Strom in Ampere für Phase2, float, Punkt als Trenner, positiv Bezug, negativ Einspeisung; SENEC liefert den Strom ohne VZ, daher nehmen wir das VZ von der Leistung
        client.publish("openWB/set/evu/APhase2", math.copysign(data_dict['PM1OBJ1']['I_AC'][1], data_dict['PM1OBJ1']['P_AC'][1]))
        # Strom in Ampere für Phase3, float, Punkt als Trenner, positiv Bezug, negativ Einspeisung; SENEC liefert den Strom ohne VZ, daher nehmen wir das VZ von der Leistung
        client.publish("openWB/set/evu/APhase3", math.copysign(data_dict['PM1OBJ1']['I_AC'][2], data_dict['PM1OBJ1']['P_AC'][2]))
        # Bezogene Energie in Wh, float, Punkt als Trenner, nur Positiv
        # client.publish("openWB/set/evu/WhImported", 1000 * data_dict['STATISTIC']['LIVE_GRID_IMPORT'])
        # Eingespeiste Energie in Wh, float, Punkt als Trenner, nur Positiv
        # client.publish("openWB/set/evu/WhExported", 1000 * data_dict['STATISTIC']['LIVE_GRID_EXPORT'])

        # Spannung in Volt für Phase1, float, Punkt als Trenner
        client.publish("openWB/set/evu/VPhase1", data_dict['PM1OBJ1']['U_AC'][0])
        # Spannung in Volt für Phase2, float, Punkt als Trenner
        client.publish("openWB/set/evu/VPhase2", data_dict['PM1OBJ1']['U_AC'][1])
        # Spannung in Volt für Phase3, float, Punkt als Trenner
        client.publish("openWB/set/evu/VPhase3", data_dict['PM1OBJ1']['U_AC'][2])
        # Netzfrequenz in Hz, float, Punkt als Trenner
        client.publish("openWB/set/evu/HzFrequenz", data_dict['PM1OBJ1']['FREQ'])

        # Statistic
        # Battery status
        # client.publish("Keller/Solar/SystemStatus", data_dict['STATISTIC']['CURRENT_STATE'])
        # Battery charge amount since installation (kWh)
        # client.publish("Keller/Solar/BatEnergyCharge", data_dict['STATISTIC']['LIVE_BAT_CHARGE_MASTER'])
        # Battery discharge amount since installation (kWh)
        # client.publish("Keller/Solar/BatEnergyDischarge", data_dict['STATISTIC']['LIVE_BAT_DISCHARGE_MASTER'])
        # Grid export amount since installation (kWh)
        # client.publish("Keller/Solar/GridEnergyOut", data_dict['STATISTIC']['LIVE_GRID_EXPORT'])
        # Grid import amount since installation (kWh)
        # client.publish("Keller/Solar/GridEnergyIn", data_dict['STATISTIC']['LIVE_GRID_IMPORT'])
        # House consumption since installation (kWh)
        # client.publish("Keller/Solar/HouseEnergy", data_dict['STATISTIC']['LIVE_HOUSE_CONS'])
        # PV generated power since installation (kWh)
        # client.publish("Keller/Solar/SolarEnergy", data_dict['STATISTIC']['LIVE_PV_GEN'])
        # Unix timestamp for above values (ms)
        # client.publish("Keller/Solar/TimeStamp", data_dict['STATISTIC']['MEASURE_TIME'])

        # Energy
        # Battery charge current: negative if discharging, positiv if charging (A)
        client.publish("Keller/Solar/BatCurrent", data_dict['ENERGY']['GUI_BAT_DATA_CURRENT'])
        # Remaining battery (percent)
        client.publish("Keller/Solar/SOC", data_dict['ENERGY']['GUI_BAT_DATA_FUEL_CHARGE'])
        # Battery charge power: negative if discharging, positiv if charging (W)
        client.publish("Keller/Solar/BatPower", data_dict['ENERGY']['GUI_BAT_DATA_POWER'])
        # Battery voltage (V)
        client.publish("Keller/Solar/BatVoltage", data_dict['ENERGY']['GUI_BAT_DATA_VOLTAGE'])
        # Grid power: negative if exporting, positiv if importing (W)
        client.publish("Keller/Solar/GridPower", data_dict['ENERGY']['GUI_GRID_POW'])
        # House power consumption (W)
        client.publish("Keller/Solar/HousePower", data_dict['ENERGY']['GUI_HOUSE_POW'])
        # PV production (W)
        client.publish("Keller/Solar/SolarPower", data_dict['ENERGY']['GUI_INVERTER_POWER'])
        # Appliance hours of operation
        client.publish("Keller/Solar/OpHours", data_dict['ENERGY']['STAT_HOURS_OF_OPERATION'])

        # PV1
        # Grid export limit (percent)
        client.publish("Keller/Solar/GridLimit", data_dict['PV1']['POWER_RATIO'])

        client.publish("Keller/Solar/UpdateIntervall", intervall)
    except:
        print("da ging was schief, später nochmal probieren")

    time.sleep(intervall)
