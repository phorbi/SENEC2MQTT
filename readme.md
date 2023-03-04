
# Kurzanleitung:

### Vorbereitung
- Ich habe mein FHEM auf einem debian Server (Raspian sollte gleich funktionieren)
- Getestet habe ich das mit Python3.7 und 3.9, 3.4 geht NICHT
- Ich betreibe einen Mosquitto Broker auf meinem FHEM Server nähere dazu findet ihr hier
https://mosquitto.org/download/
- Auf dem Server habe ich Python3 installiert um die Skripte laufen zu lassen
<code>sudo apt install python3</code>
- Es werden folgende libraries/packages gebraucht:   
https://pypi.org/project/paho-mqtt  
<code>python3 -m pip install paho-mqtt</code>  
und  
https://pypi.org/project/requests/  
<code>python3 -m pip install requests</code>


Es gibt zwei Pyhon Skripte.
Senec.py hat den Ursprung hier:  
https://inden.one/blog/2020/11/26/senec-python-library.html  
Und dient dazu, ähnlich wie bei dem HTTPMod Modul die Daten über HTTP beim Speicher anzufragen. Ich habe es leicht modifiziert und meinen Bedürfnissen angepasst.


SENEC2MQTT.py sendet die vom Senec bekommenen Daten auf dem MQTT Broker.
MQTT Broker, sowie SENEC Adresse müssen dort zunächst entsprechend in Zeile 20-23 vorkonfiguriert werden.


- Ich habe die beiden Skripte bei mir auf meinem FHEM Server (debian) unter <code>/usr/bin/SENEC2MQTT</code>abgelegt
- Ich habe die Dateien executable gemacht (hier bin ich wie gewohnt mit der bazooka vorgegangen):   
<code>
sudo chmod 777 /usr/bin/SENEC2MQTT/Senec.py  
sudo chmod 777 /usr/bin/SENEC2MQTT/SENEC2MQTT.py</code>  
Das geht ggf. auch etwas eleganter.
- Um SENEC2MQTT nun automatisch mit dem Systemd laufen zu lassen, muss in <code>/etc/systemd/system</code> eine Datei SENEC2MQTT.service angelegt werden.   
Inhalt:<br />
<code><br />
[Unit]<br />  
Description=Senec to MQTT Bridge<br />
Wants=network.target<br />
After=network.target<br />
[Service]<br />
Type=simple<br />
User=[TRAGT HIER EUREN USER EIN]<br />
Group=[TRAGT HIER DIE GRUPPE DES USERS EIN]<br />
ExecStart=/usr/bin/python3 /usr/bin/SENEC2MQTT/SENEC2MQTT.py<br />
Restart=always<br />
RestartSec=3<br />
[Install]<br />
WantedBy=multi-user.target</code><br />

Hinweis, in den Zeilen User und Group müsst ihr euren Linux oder Raspian user eintragen (also z.B. User=pi, Group=pi)

Die Datei muss ebenfalls ausführbar gemacht werden.  
<code>sudo chmod 777 /etc/systemd/system/SENEC2MQTT.service</code>

Ich bin mir nicht mehr ganz sicher, aber es könnte sein, dass man dann erst mal mit  
<code>sudo systemctl start SENEC2MQTT</code>  
den Dienst erstmalig starten muss.  
Damit der service auch bei einem Neustart automatisch geladen wird müsst ihr den dienst enablen  
<code>sudo systemctl enable SENEC2MQTT</code>

Nutzen und Modifizieren ist erlaubt. Wer verbessert muss teilen! 


### Nutzung
Welche Topics verwendet werden findet Ihr in SENEC2MQTT.py ab Zeile 54  
Es werden standardmäßig alle 2 Sekunden die Daten vom SENEC geholt und auf den MQTT gepublisht.
Auf dem Topic <code>Keller/Solar/control/SENEC2MQTTInterval</code> könnt ihr das Updateintervall einstellen.
Ich empfehle Werte zwischen 1 und 30.  
Das Skript ignoriert alles außer INT werte, Diese sind auf 1-60 limitiert (Werte kleiner 1 -> 1, Werte größer 60 -> 60) 
wie immer auch hier: Benutzung auf eigene Gefahr.  
Auf <code>Keller/Solar/UpdateIntervall</code> gibt der Dienst zurück, welches Intervall gerade verwendet wird.

### openWB
für eine Schnittstelle zu einer openWB habe ich eine SENEC2MQTT_openWB.py bridge gebaut. Diese liefert zusätzlich noch die Daten, die openWB möchte. 
SENEC2MQTT_openWB.py ersetzt dann SENEC2MQTT.py

Für SENEC2MQTT_openWB.py muss alles wie oben mit der SENEC2MQTT bridge beschrieben gemacht werden. also Senec.py + SENEC2MQTT_openWB.py in /usr/bin/SENEC2MQTT legen, rechte vergeben. SENEC2MQTT.service anlegen, aber bei "ExecStart=" am Ende SENEC2MQTT_openWB.py eintragen. 

### weitere Info
es gab eine längere Diskussion hier:  
https://forum.fhem.de/index.php/topic,107265.msg1221254.html#msg1221254  
Wen es interessiert kann sicherlich hier noch mehr an Informationen ziehen.
