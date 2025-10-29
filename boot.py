# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network
from WIFI_CONFIG import SSID, PASSWORD

wlan = network.WLAN()
wlan.active(False)

wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        pass
print('network config:', wlan.ipconfig('addr4'))

import test_ota



