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

BROKER_IP = "192.168.10.100"
BROKER_PORT = 1883
SENEC_IP = "192.168.10.65"

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("Keller/Solar/control/SENEC2MQTTInterval")  # Subscribe to the topic

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    if msg.topic == "Keller/Solar/control/SENEC2MQTTInterval":
        try:
            q.put(int(msg.payload.decode("utf-8")))
            print("Intervall vom MQTT: " + str(msg.payload.decode("utf-8")))
        except:
            print("not an int")

client =mqtt.Client("SENEC-V3")
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
client.connect(BROKER_IP, BROKER_PORT) #connect to broker
q=Queue() # we use a queue to get date from the on_message callback to the main
intervall = 2


#connect to Senec
info =Senec.SenecAPI(SENEC_IP)

#go on forever
client.loop_start()
while True:

    while not q.empty():
        intervall = q.get()
        if intervall <= 1: intervall = 1
        if intervall >= 60: intervall = 60
    try:
        #get Data from Senec
        data_dict = info.get_values()
        #data_dict = info.get_all_values()
        #print(data_dict)
    except:
        print("info.get_values() ging nicht")
    try:
        #Statistic
        #client.publish("Keller/Solar/SystemStatus", data_dict['STATISTIC']['CURRENT_STATE'])                    # Battery status
        #client.publish("Keller/Solar/BatEnergyCharge", data_dict['STATISTIC']['LIVE_BAT_CHARGE_MASTER'])        # Battery charge amount since installation (kWh)
        #client.publish("Keller/Solar/BatEnergyDischarge", data_dict['STATISTIC']['LIVE_BAT_DISCHARGE_MASTER'])  # Battery discharge amount since installation (kWh)
        #client.publish("Keller/Solar/GridEnergyOut", data_dict['STATISTIC']['LIVE_GRID_EXPORT'])                # Grid export amount since installation (kWh)
        #client.publish("Keller/Solar/GridEnergyIn", data_dict['STATISTIC']['LIVE_GRID_IMPORT'])                 # Grid import amount since installation (kWh)
        #client.publish("Keller/Solar/HouseEnergy", data_dict['STATISTIC']['LIVE_HOUSE_CONS'])                   # House consumption since installation (kWh)
        #client.publish("Keller/Solar/SolarEnergy", data_dict['STATISTIC']['LIVE_PV_GEN'])                       # PV generated power since installation (kWh)
        #client.publish("Keller/Solar/TimeStamp", data_dict['STATISTIC']['MEASURE_TIME'])                        # Unix timestamp for above values (ms)

        #Energy
        client.publish("Keller/Solar/BatCurrent", data_dict['ENERGY']['GUI_BAT_DATA_CURRENT'])                  # Battery charge current: negative if discharging, positiv if charging (A)
        client.publish("Keller/Solar/SOC", data_dict['ENERGY']['GUI_BAT_DATA_FUEL_CHARGE'])                     # Remaining battery (percent)
        client.publish("Keller/Solar/BatPower", data_dict['ENERGY']['GUI_BAT_DATA_POWER'])                      # Battery charge power: negative if discharging, positiv if charging (W)
        client.publish("Keller/Solar/BatVoltage", data_dict['ENERGY']['GUI_BAT_DATA_VOLTAGE'])                  # Battery voltage (V)
        client.publish("Keller/Solar/GridPower", data_dict['ENERGY']['GUI_GRID_POW'])                           # Grid power: negative if exporting, positiv if importing (W)
        client.publish("Keller/Solar/HousePower", data_dict['ENERGY']['GUI_HOUSE_POW'])                         # House power consumption (W)
        client.publish("Keller/Solar/SolarPower", data_dict['ENERGY']['GUI_INVERTER_POWER'])                    # PV production (W)
        client.publish("Keller/Solar/OpHours", data_dict['ENERGY']['STAT_HOURS_OF_OPERATION'])                  # Appliance hours of operation
        client.publish("Keller/Solar/SystemStatus", data_dict['ENERGY']['STAT_STATE'])                          # war in Statistic Battery status

        #PV1
        client.publish("Keller/Solar/GridLimit", data_dict['PV1']['POWER_RATIO'])                               # Grid export limit (percent)

        #Grid
        client.publish("Keller/Solar/GridFreq", data_dict['PM1OBJ1']['FREQ'])                                   #Grid frequency
        client.publish("Keller/Solar/Current_L1", data_dict['PM1OBJ1']['I_AC'][0])                              #Grid current L1
        client.publish("Keller/Solar/Current_L2", data_dict['PM1OBJ1']['I_AC'][1])                              #Grid current L2
        client.publish("Keller/Solar/Current_L3", data_dict['PM1OBJ1']['I_AC'][2])                              #Grid current L3
        client.publish("Keller/Solar/Voltage_L1", data_dict['PM1OBJ1']['U_AC'][0])                              #Grid voltage L1
        client.publish("Keller/Solar/Voltage_L2", data_dict['PM1OBJ1']['U_AC'][1])                              #Grid voltage L2
        client.publish("Keller/Solar/Voltage_L3", data_dict['PM1OBJ1']['U_AC'][2])                              #Grid voltage L3
        client.publish("Keller/Solar/Power_L1", data_dict['PM1OBJ1']['P_AC'][0])                                # Grid Power L1
        client.publish("Keller/Solar/Power_L2", data_dict['PM1OBJ1']['P_AC'][1])                                # Grid Power L2
        client.publish("Keller/Solar/Power_L3", data_dict['PM1OBJ1']['P_AC'][2])                                # Grid Power L3

        client.publish("Keller/Solar/UpdateIntervall", intervall)
    except:
        print("publishen ging nicht")

    time.sleep(intervall)
