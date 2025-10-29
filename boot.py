# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
# Complete project details at https://RandomNerdTutorials.com/micropython-programming-with-esp32-and-esp8266/

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()
from payload import device_payload

from esp32 import NVS

nvs = NVS("blind")

try:
    print(nvs.get_i32("offset"))
except:    
    nvs.set_i32("offset", 200)
    nvs.commit()
    print ("initialised offset")


try:
    print(nvs.get_i32("closed_position"))
except:    
    nvs.set_i32("closed_position", 1200)
    nvs.commit()
    print ("initialised closed position")
    
offset = nvs.get_i32("offset")
last_offset = 0
closed_position = nvs.get_i32("closed_position")
last_closed_position = 0

import motor
m = motor.HalfStepMotor.frompins(10, 7, 6, 5)

ssid = 'FARLEIGH-MESH'
password = 'Julie1801!'
mqtt_server = '192.168.68.51'
mqtt_user = 'beantree'
mqtt_pass = 's2sfilwY'

#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
uid_str = ubinascii.hexlify(machine.unique_id()).decode()

print(device_payload)
topic_sub = b'blind/#'
topic_pub = b'hello'

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

device_topic = "homeassistant/device/" + uid_str + "/config"

#**************************************
#    Handle incoming messages
#*************************************
    
def sub_cb(topic, msg):
  print((topic, msg))
  global blind_cmd
  global offset
  global closed_position
  
  # blind open / close message
  if topic == b'blind/switch1/set':
    print('blind open/close message received')
    if msg == b'CLOSE':
      blind_cmd = 'CLOSE'
    elif msg == b'STOP':
      blind_cmd = 'STOP'
    else:
      blind_cmd = 'OPEN'
    
  if topic == b'blind/offset/command':
    offset = int(msg.decode("utf-8"))
    print(msg, offset)
    
  if topic == b'blind/closed_position/command':
    closed_position = int(msg.decode("utf-8"))
    print(msg, closed_position)
        
def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, user=mqtt_user, password=mqtt_pass)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()
  
#**************************************
#    Open the blind
#*************************************
def open_blind():
    print("Opening the blind")
    
    if endstop.value() == 0:         # endstop already active
        m.step(200)                  # move away
        time.sleep(2)                # wait 2 seconds
    
    # move backwards until we hit the endstop
    while endstop.value() == 1 and blind_cmd != 'STOP':
        m.step(-1)
        client.check_msg()
        
    time.sleep(2)                    # wait 2 seconds
    
    #move out to the offset that defines our zero postion
    # i.e. the normal open position of the blind
    m.step(offset)
    m.zero()                         # set the zero position
    m.disable()
    client.publish(b'blind/switch1', 'OPEN')
    
#**************************************
#    Close the blind
#*************************************
def close_blind():
    print("Closing the blind", m.pos)
    while endstop.value() == 1 and blind_cmd != 'STOP' and m.pos <= closed_position:
        m.step(1)
        client.check_msg()    
    # m.step_until(closed_position)
    m.disable()
    client.publish(b'blind/switch1', 'CLOSED')
    
def update_endstop_state():
    print("endstop state",endstop.value())
    led.value(endstop.value())
    if endstop.value() == 1:
      msg = 'OFF'
    else:
      msg = 'ON'
    print("about to publish endstop state")
    client.publish(b'blind/sensor/endstop',msg)

    
#**************************************
#    Setup
#**************************************    

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()
  
client.publish(device_topic, device_payload)

endstop = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin(8, machine.Pin.OUT)
led.value(endstop.value())
last_endstop_state = not endstop.value()

# set the two flags different to force a blind opening to start
blind_cmd = 'OPEN'
last_blind_cmd = 'CLOSE'

client.publish(b'blind/offset/state',str(offset))
client.publish(b'blind/closed_position/state',str(closed_position))
update_endstop_state()

#**************************************
#    Loop
#**************************************

while True:
  try:
    client.check_msg()
    
    if (time.time() - last_message) > message_interval:

      last_message = time.time()
      counter += 1
  except OSError as e:
    print("OS error:", e)
    restart_and_reconnect()
    
    
  if endstop.value() != last_endstop_state:
    last_endstop_state = endstop.value()
    update_endstop_state()

  if blind_cmd != last_blind_cmd:
      print("blind command", blind_cmd)
      last_blind_cmd = blind_cmd
      if blind_cmd == 'CLOSE':
          close_blind()
      elif blind_cmd == 'OPEN':
          open_blind()
          
  if offset != last_offset:
      print('new offset', offset)
      last_offset = offset
      nvs.set_i32("offset", offset)
      nvs.commit()
      client.publish(b'blind/offset/state',str(offset))

  if closed_position != last_closed_position:
      print('new closed position', closed_position)
      last_closed_position = closed_position
      nvs.set_i32("closed_position", closed_position)
      nvs.commit()
      client.publish(b'blind/closed_position/state',str(closed_position))
