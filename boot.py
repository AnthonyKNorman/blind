# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network, machine, ubinascii
from WIFI_CONFIG import SSID, PASSWORD

client_id = ubinascii.hexlify(machine.unique_id())
uid_str = ubinascii.hexlify(machine.unique_id()).decode()

# Set the hostname BEFORE activating/connecting the interface
new_hostname = "ESP32C3-" + uid_str
network.hostname(new_hostname)

wlan = network.WLAN()
wlan.active(False)

wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        pass
print('network config:', wlan.ipconfig('addr4'))
ip_addr = wlan.ipconfig('addr4')[0]
print (ip_addr)


import test_ota
