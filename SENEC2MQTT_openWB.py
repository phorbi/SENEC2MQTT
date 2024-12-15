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

import SENEC2MQTT_logging  # Importieren Sie den Handler aus Ihrer Konfiguration
logger = SENEC2MQTT_logging.logger  # Erstellen Sie einen Logger

BROKER_IP = "192.168.10.100"
BROKER_PORT = 1883
SENEC_IP = "192.168.10.65"

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    logger.info('connected to broker')
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("Keller/Solar/control/SENEC2MQTTInterval")  # Subscribe to the topic

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    if msg.topic == "Keller/Solar/control/SENEC2MQTTInterval":
        logger.info(f'message from {msg.topic}')
        try:
            q.put(int(msg.payload.decode("utf-8")))
            print("Intervall vom MQTT: " + str(msg.payload.decode("utf-8")))
            logger.info(f'Intervall vom MQTT: {str(msg.payload.decode("utf-8"))} Sekunden')
        except:
            logger.error(f'Payload for {msg.topic} is not an int')
            print("not an int")

def on_disconnect(client, userdata, rc):
    logger.info(f'disconnected from MQTT Broker {BROKER_IP}:{BROKER_PORT}, reconnecting')
    client.connect(BROKER_IP, BROKER_PORT)

client =mqtt.Client("SENEC-V3")

client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
client.on_disconnect = on_disconnect # Define callback function for desiconnection handling

logger.info(f'connecting to MQTT Broker: {BROKER_IP}:{BROKER_PORT}')
client.connect(BROKER_IP, BROKER_PORT) #connect to broker

q=Queue() # we use a queue to get date from the on_message callback to the main
intervall = 5

# connect to Senec
info = Senec.SenecAPI(SENEC_IP)

# go on forever
client.loop_start()
while True:

    while not q.empty():
        intervall = q.get()
        if intervall <= 1: intervall = 1
        if intervall >= 60: intervall = 60
    try:
        #get Data from Senec
        logger.debug('begin try get_values()')
        data_dict = info.get_values()
        #data_dict = info.get_all_values()
        logger.debug(f'get_values returned: {data_dict}')
    except:
        logger.error('get_values() ging nicht')
    try:
        logger.debug('begin publish')
       
        # openWB PV-Modul
        # PV-Leistung in W, int, positiv
        client.publish("openWB/set/pv/1/W", int(data_dict['ENERGY']['GUI_INVERTER_POWER']))
        print("inverter power: ", int(-1*data_dict['ENERGY']['GUI_INVERTER_POWER']))

        # openWB Batterie
        # Speicherleistung in Wall, int, positiv Ladung, negativ Entladung
        client.publish("openWB/set/houseBattery/W", int(data_dict['ENERGY']['GUI_BAT_DATA_POWER']))
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

        # Spannung in Volt für Phase1, float, Punkt als Trenner
        client.publish("openWB/set/evu/VPhase1", data_dict['PM1OBJ1']['U_AC'][0])
        # Spannung in Volt für Phase2, float, Punkt als Trenner
        client.publish("openWB/set/evu/VPhase2", data_dict['PM1OBJ1']['U_AC'][1])
        # Spannung in Volt für Phase3, float, Punkt als Trenner
        client.publish("openWB/set/evu/VPhase3", data_dict['PM1OBJ1']['U_AC'][2])
        # Netzfrequenz in Hz, float, Punkt als Trenner
        client.publish("openWB/set/evu/HzFrequenz", data_dict['PM1OBJ1']['FREQ'])

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

    except:
        logger.error('publish fehlgeschlagen')
    logger.debug(f'begin sleeping for {intervall} seconds')
    time.sleep(intervall)
