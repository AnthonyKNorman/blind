import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import esp
esp.osdebug(None)
import gc
gc.collect()
from payload import device_payload
import json
import os

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
m = motor.HalfStepMotor.frompins(5, 6, 7, 10)

mqtt_server = '192.168.68.51'
mqtt_user = 'beantree'
mqtt_pass = 's2sfilwY'

device_payload["dev"]["name"] = "Blind " + uid_str
device_payload["o"]["name"] = "Blind " + uid_str
device_payload["dev"]["ids"] = uid_str

# blind switch
device_payload["cmps"]["switch1"]["unique_id"] = uid_str + "aa"
switch_cmd_topic = "blind/" + uid_str + "/switch/cmd"
switch_state_topic = "blind/" + uid_str + "/switch/state"
device_payload["cmps"]["switch1"]["state_topic"] = switch_state_topic
device_payload["cmps"]["switch1"]["command_topic"] = switch_cmd_topic

# closed position
device_payload["cmps"]["closed1"]["unique_id"] = uid_str + "ab"
closed_cmd_topic = "blind/" + uid_str + "/closed/cmd"
closed_state_topic = "blind/" + uid_str + "/closed/state"
device_payload["cmps"]["closed1"]["state_topic"] = closed_state_topic
device_payload["cmps"]["closed1"]["command_topic"] = closed_cmd_topic

# offset from zero
device_payload["cmps"]["offset1"]["unique_id"] = uid_str + "ac"
offset_cmd_topic = "blind/" + uid_str + "/offset/cmd"
offset_state_topic = "blind/" + uid_str + "/offset/state"
device_payload["cmps"]["offset1"]["state_topic"] = offset_state_topic
device_payload["cmps"]["offset1"]["command_topic"] = offset_cmd_topic


# endstop
device_payload["cmps"]["sensor1"]["unique_id"] = uid_str + "ad"
endstop_state_topic = "blind/" + uid_str + "/endstop/state"
device_payload["cmps"]["sensor1"]["state_topic"] = endstop_state_topic

# home
device_payload["cmps"]["button1"]["unique_id"] = uid_str + "ae"
home_cmd_topic = "blind/" + uid_str + "/home/cmd"
device_payload["cmps"]["button1"]["command_topic"] = home_cmd_topic

# wifi signal strength
device_payload["cmps"]["strength"]["unique_id"] = uid_str + "af"
strength_state_topic = "blind/" + uid_str + "/strength/state"
device_payload["cmps"]["strength"]["state_topic"] = strength_state_topic

# OTA Version
device_payload["cmps"]["version"]["unique_id"] = uid_str + "ag"
version_state_topic = "blind/" + uid_str + "/version/state"
device_payload["cmps"]["version"]["state_topic"] = version_state_topic

# reset
device_payload["cmps"]["reset"]["unique_id"] = uid_str + "ah"
reset_cmd_topic = "blind/" + uid_str + "/reset/cmd"
device_payload["cmps"]["reset"]["command_topic"] = reset_cmd_topic

device_payload_dump = json.dumps(device_payload)

print(device_payload_dump)

topic_sub = b'blind/' + uid_str + '/#'
topic_pub = b'hello'

endstop = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin(8, machine.Pin.OUT)


# flash the led to show we got this far
for i in range(10):
    led.value(not led.value())
    time.sleep_ms(500)

last_message = 0
message_interval = 300    # five minutes
counter = 0

device_topic = "homeassistant/device/" + uid_str + "/config"

#**************************************
#    Handle incoming messages
#*************************************
    
def sub_cb(topic, msg):
  print((topic, msg))
  global blind_cmd
  global last_blind_cmd
  global offset
  global closed_position
  
  # blind open / close message
  
  byte_topic = bytearray()
  byte_topic.extend(switch_cmd_topic)
  
  if topic == byte_topic:
    print('blind open/close message received')
    if msg == b'CLOSE':
      blind_cmd = 'CLOSE'
    elif msg == b'STOP':
      blind_cmd = 'STOP'
    else:
      blind_cmd = 'OPEN'
    last_blind_cmd = ""
    
  byte_topic = bytearray()
  byte_topic.extend(offset_cmd_topic)
    
  if topic == byte_topic:
    offset = int(msg.decode("utf-8"))
    print(msg, offset)
    
  byte_topic = bytearray()
  byte_topic.extend(closed_cmd_topic)
    
  if topic == byte_topic:
    closed_position = int(msg.decode("utf-8"))
    print(msg, closed_position)
    
  # capture HOME command
  byte_topic = bytearray()
  byte_topic.extend(home_cmd_topic)
    
  if topic == byte_topic:
    print('home command received')
    blind_cmd = 'HOME'
    last_blind_cmd = ''
    
  # capture RESET command
  byte_topic = bytearray()
  byte_topic.extend(reset_cmd_topic)
    
  if topic == byte_topic:
    print('reset command received')
    restart_and_reconnect()
        
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
#    Home the blind
#*************************************
def home_blind():
    print("Homing the blind")
    
    if endstop.value() == 0:         # endstop already active
        
        while endstop.value() == 1:  # move away until the endstop is not active
            m.step(1)
            
        m.step(200)                  # move away a bit more
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
    
    byte_state_topic = bytearray()
    byte_state_topic.extend(switch_state_topic)
    client.publish(byte_state_topic, 'OPEN')
    
    
#**************************************
#    Open the blind
#*************************************
def open_blind():
    print("Opening the blind")
    
    if m.pos < 0:
        home_blind()

    while blind_cmd != 'STOP' and m.pos > 0:
        m.step(-1)
        client.check_msg()    
    # m.step_until(closed_position)
    m.disable()

    
    byte_state_topic = bytearray()
    byte_state_topic.extend(switch_state_topic)
    client.publish(byte_state_topic, 'OPEN')
    
#**************************************
#    Close the blind
#*************************************
def close_blind():
    print("Closing the blind", m.pos)
    while blind_cmd != 'STOP' and m.pos <= closed_position:
        m.step(1)
        client.check_msg()    
    # m.step_until(closed_position)
    m.disable()

    byte_state_topic = bytearray()
    byte_state_topic.extend(switch_state_topic)
    client.publish(byte_state_topic, 'CLOSED')
    
    
def update_endstop_state():
    print("endstop state",endstop.value())
    led.value(endstop.value())
    if endstop.value() == 1:
      msg = 'OFF'
    else:
      msg = 'ON'
      
    print("about to publish endstop state")
    byte_state_topic = bytearray()
    byte_state_topic.extend(endstop_state_topic)
    client.publish(byte_state_topic, msg)
    
def publish_wifi_strength():
    strength = wlan.status('rssi')
    # send the wifi strength position
    byte_state_topic = bytearray()
    byte_state_topic.extend(strength_state_topic)
    client.publish(byte_state_topic, str(strength))

    
#**************************************
#    Setup
#**************************************    

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()
  
client.publish(device_topic, device_payload_dump)

# Send the latest software version
# get the current version (stored in version.json)
if 'version.json' in os.listdir():    
    with open('version.json') as f:
        current_version = int(json.load(f)['version'])
    print(f"Current device firmware version is '{current_version}'")
byte_state_topic = bytearray()
byte_state_topic.extend(version_state_topic)
client.publish(byte_state_topic, str(current_version))

led.value(endstop.value())
last_endstop_state = not endstop.value()

# send the offset state
byte_state_topic = bytearray()
byte_state_topic.extend(offset_state_topic)
client.publish(byte_state_topic, str(offset))

# send the closed position
byte_state_topic = bytearray()
byte_state_topic.extend(closed_state_topic)
client.publish(byte_state_topic, str(closed_position))

# update the endstop state
update_endstop_state()

publish_wifi_strength()


# home the blind and set the flags
blind_cmd = 'OPEN'
last_blind_cmd = 'OPEN'
home_blind()

#**************************************
#    Loop
#**************************************

while True:
  try:
    client.check_msg()
  except OSError as e:
    print("OS error:", e)
    restart_and_reconnect()
    
  if (time.time() - last_message) > message_interval:
    # send the wifi strength  
    publish_wifi_strength()
    # send the device topic to ensure continuity
    client.publish(device_topic, device_payload_dump)
        
    last_message = time.time()
    counter += 1    
    
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
      elif blind_cmd == 'HOME':
          home_blind()
          
  if offset != last_offset:
    print('new offset', offset)
    last_offset = offset
    nvs.set_i32("offset", offset)
    nvs.commit()

    byte_state_topic = bytearray()
    byte_state_topic.extend(offset_state_topic)
    client.publish(byte_state_topic, str(offset))
      
  if closed_position != last_closed_position:
    print('new closed position', closed_position)
    last_closed_position = closed_position
    nvs.set_i32("closed_position", closed_position)
    nvs.commit()
    
    byte_state_topic = bytearray()
    byte_state_topic.extend(closed_state_topic)
    client.publish(byte_state_topic, str(closed_position))
    

