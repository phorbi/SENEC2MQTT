#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Library to get a lot of useful data out of Senec appliances.

Tested with: SENEC.Home V3 hybrid duo (https://senec.com/de/produkte/senec-home-v3-hybrid)

Kudos:
* SYSTEM_STATE_NAME taken from https://github.com/mchwalisz/pysenec
"""
import requests
import struct

__author__ = "Nicolas Inden"
__copyright__ = "Copyright 2020, Nicolas Inden"
__credits__ = ["Nicolas Inden", "Mikołaj Chwalisz"]
__license__ = "Apache-2.0 License"
__version__ = "1.0.0"
__maintainer__ = "Nicolas Inden"
__email__ = "nico@smashnet.de"
__status__ = "Production"

class SenecAPI():

    def __init__(self, device_ip):
        self.device_ip = device_ip
        self.read_api  = f"http://{device_ip}/lala.cgi"

    def get_values(self):
        response = requests.post(self.read_api, json=BASIC_REQUEST)
        if response.status_code == 200:
            res = self.__decode_data(response.json())
            return self.__substitute_system_state(res)
        else:
            return {"msg": f"Status code {response.status_code}"}

    def get_all_values(self):
        request_json = {"STATISTIC": {},"ENERGY": {},"FEATURES": {},"LOG": {},"SYS_UPDATE": {},"WIZARD": {},"BMS": {},"BAT1": {},"BAT1OBJ1": {},"BAT1OBJ2": {},"BAT1OBJ3": {},"BAT1OBJ4": {},"PWR_UNIT": {},"PV1": {},"FACTORY": {},"GRIDCONFIG": {}}
        response = requests.post(self.read_api, json=request_json)
        if response.status_code == 200:
            return self.__decode_data(response.json())
        else:
            return {"msg": f"Status code {response.status_code}"}

    def __decode_data(self, data):
        return { k: self.__decode_data_helper(v) for k, v in data.items() }

    def __decode_data_helper(self, data):
        if isinstance(data, str):
            return self.__decode_value(data)
        if isinstance(data, list):
            return [self.__decode_value(val) for val in data]
        if isinstance(data, dict):
            return { k: self.__decode_data_helper(v) for k, v in data.items() }

    def __decode_value(self, value):
        if value.startswith("fl_"):
            return struct.unpack('!f', bytes.fromhex(value[3:]))[0]
        if value.startswith("u8_"):
            return struct.unpack('!B', bytes.fromhex(value[3:]))[0]
        if value.startswith("i3_") or value.startswith("u3_") or value.startswith("u1_"):
            return int(value[3:], 16)
        if value.startswith("st_"):
            return value[3:]
        return value

    def __substitute_system_state(self, data):
        system_state = data['STATISTIC']['CURRENT_STATE']
        #auskommentiert, bis die anzahl der Status bekannt ist:
        try:
            data['STATISTIC']['CURRENT_STATE'] = SYSTEM_STATE_NAME[system_state]
        except Exception:
            pass
        return data

BASIC_REQUEST = {
    'STATISTIC': {
        'CURRENT_STATE': '',  # Current state of the system (int, see SYSTEM_STATE_NAME)            "Keller/Solar/SystemStatus"
        'LIVE_BAT_CHARGE_MASTER': '',  # Battery charge amount since installation (kWh)             "Keller/Solar/BatEnergyCharge"
        'LIVE_BAT_DISCHARGE_MASTER': '',  # Battery discharge amount since installation (kWh)       "Keller/Solar/BatEnergyDischarge"
        'LIVE_GRID_EXPORT': '',  # Grid export amount since installation (kWh)                      "Keller/Solar/GridEnergyOut"
        'LIVE_GRID_IMPORT': '',  # Grid import amount since installation (kWh)                      "Keller/Solar/GridEnergyIn"
        'LIVE_HOUSE_CONS': '',  # House consumption since installation (kWh)                        "Keller/Solar/HouseEnergy"
        'LIVE_PV_GEN': '',  # PV generated power since installation (kWh)                           "Keller/Solar/SolarEnergy"
        'MEASURE_TIME': ''  # Unix timestamp for above values (ms)                                  "Keller/Solar/TimeStamp"
    },
    'ENERGY': {
        'GUI_BAT_DATA_CURRENT': '',  # Battery charge current: negative if discharging, positiv if charging (A)     "Keller/Solar/BatCurrent"
        'GUI_BAT_DATA_FUEL_CHARGE': '',  # Remaining battery (percent)                                              "Keller/Solar/SOC"
        'GUI_BAT_DATA_POWER': '',  # Battery charge power: negative if discharging, positiv if charging (W)         "Keller/Solar/BatPower"
        'GUI_BAT_DATA_VOLTAGE': '',  # Battery voltage (V)                                                          "Keller/Solar/BatVoltage"
        'GUI_GRID_POW': '',  # Grid power: negative if exporting, positiv if importing (W)                          "Keller/Solar/GridPower"
        'GUI_HOUSE_POW': '',  # House power consumption (W)                                                         "Keller/Solar/HousePower"
        'GUI_INVERTER_POWER': '',  # PV production (W)                                                              "Keller/Solar/SolarPower"
        'STAT_HOURS_OF_OPERATION': ''  # Appliance hours of operation                                               "Keller/Solar/OpHours"
    },
    'PV1': {
        'POWER_RATIO': '',  # Grid export limit (percent)                                                           "Keller/Solar/GritLimit"
    },
   'PM1OBJ1': {
       'I_AC': '',         #Grid current, note: no sign for in or out
       'FREQ': '',         #measured frequency
       'U_AC': '',         #Grid voltage
       'P_AC': '',         #Grid Power (phases)
   },
}


SYSTEM_STATE_NAME = {
    0: "INITIAL STATE",
    1: "ERROR INVERTER COMMUNICATION",
    2: "ERROR ELECTRICY METER",
    3: "RIPPLE CONTROL RECEIVER",
    4: "INITIAL CHARGE",
    5: "MAINTENANCE CHARGE",
    6: "MAINTENANCE READY",
    7: "MAINTENANCE REQUIRED",
    8: "MAN. SAFETY CHARGE",
    9: "SAFETY CHARGE READY",
    10: "FULL CHARGE",
    11: "EQUALIZATION: CHARGE",
    12: "DESULFATATION: CHARGE",
    13: "BATTERY GELADEN",
    14: "LADEN",
    15: "BATTERY LEER",
    16: "ENTLADEN",
    17: "PV + ENTLADEN",
    18: "NETZ + ENTLADEN",
    19: "PASSIV",
    20: "AUS",
    21: "EIGENVERBRAUCH",
    22: "NEUSTART",
    23: "MAN. EQUALIZATION: CHARGE",
    24: "MAN. DESULFATATION: CHARGE",
    25: "SAFETY CHARGE",
    26: "BATTERY PROTECTION MODE",
    27: "EG ERROR",
    28: "EG CHARGE",
    29: "EG DISCHARGE",
    30: "EG PASSIVE",
    31: "EG PROHIBIT CHARGE",
    32: "EG PROHIBIT DISCHARGE",
    33: "EMERGANCY CHARGE",
    34: "SOFTWARE UPDATE",
    35: "NSP ERROR",
    36: "NSP ERROR: GRID",
    37: "NSP ERROR: HARDWRE",
    38: "NO SERVER CONNECTION",
    39: "BMS ERROR",
    40: "MAINTENANCE: FILTER",
    41: "SLEEPING MODE",
    42: "WAITING EXCESS",
    43: "CAPACITY TEST: CHARGE",
    44: "CAPACITY TEST: DISCHARGE",
    45: "MAN. DESULFATATION: WAIT",
    46: "MAN. DESULFATATION: READY",
    47: "MAN. DESULFATATION: ERROR",
    48: "EQUALIZATION: WAIT",
    49: "EMERGANCY CHARGE: ERROR",
    50: "MAN. EQUALIZATION: WAIT",
    51: "MAN. EQUALIZATION: ERROR",
    52: "MAN: EQUALIZATION: READY",
    53: "AUTO. DESULFATATION: WAIT",
    54: "ABSORPTION PHASE",
    55: "DC-SWITCH OFF",
    56: "PEAK-SHAVING: WAIT",
    57: "ERROR BATTERY INVERTER",
    58: "NPU-ERROR",
    59: "BMS OFFLINE",
    60: "MAINTENANCE CHARGE ERROR",
    61: "MAN. SAFETY CHARGE ERROR",
    62: "SAFETY CHARGE ERROR",
    63: "NO CONNECTION TO MASTER",
    64: "LITHIUM SAFE MODE ACTIVE",
    65: "LITHIUM SAFE MODE DONE",
    66: "BATTERY VOLTAGE ERROR",
    67: "BMS DC SWITCHED OFF",
    68: "GRID INITIALIZATION",
    69: "GRID STABILIZATION",
    70: "REMOTE SHUTDOWN",
    71: "OFFPEAK-CHARGE",
    72: "ERROR HALFBRIDGE",
    73: "BMS: ERROR OPERATING TEMPERATURE",
    74: "FACOTRY SETTINGS NOT FOUND",
    75: "BACKUP POWER MODE - ACTIVE",
    76: "BACKUP POWER MODE - BATTERY EMPTY",
    77: "BACKUP POWER MODE ERROR",
    78: "INITIALISIERUNG",
    79: "INSTALLATIONSMODUS",
    80: "NETZ OFFLINE",
    81: "BMS UPDATE NOTWENDIG",
    82: "BMS KONFIGURATION NOTWENDIG",
    83: "ISULATIONSTEST",
    84: "SELBSTTEST",
    85: "FERNSTEUERUNG",
    86: "FEHLER: TEMPERATURSENSOR",
    87: "GRID OPERATOR: CHARGE PROHIBITED",
    88: "GRID OPERATOR: DISCHARGE PROHIBITED",
    89: "SPARE CAPACITY",
    90: "SELBSTTEST FEHLER",
    91: "ERDSCHLUSS FEHLER",
    92: "92",
    93: "93",
    94: "94",
    95: "BATTERIEDIAGNOSE",
    96: "BALANCING"
}