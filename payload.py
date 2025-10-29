device_payload = """{
  "dev": {
    "ids": "34f051b880f5",
    "name": "Blind"
  },
  "o": {
    "name":"Blind 1"
  },
  "cmps": {
    "sensor1": {
      "p": "binary_sensor",
      "name":"End Stop",
      "state_topic": "blind/sensor/endstop",
      "unique_id":"379840e0c951",
      "payload_on": "ON",
      "payload_off": "OFF"
    },
    "offset1": {
      "p": "number",
      "unique_id": "eee0e4839d46",
      "name":"Offset",
      "min":"0",
      "max":"300",
      "command_topic": "blind/offset/command",
      "state_topic": "blind/offset/state"
    },
    "closed1": {
      "p": "number",
      "unique_id": "d8e28d5bc06a",
      "name":"Closed Position",
      "min":"0",
      "max":"2000",
      "command_topic": "blind/closed_position/command",
      "state_topic": "blind/closed_position/state"
    },
    "switch1": {
      "p": "cover",
      "unique_id": "fcc1bd8e30c6",
      "name":"Blind",
      "command_topic": "blind/switch1/set",
      "state_topic": "blind/switch1",
      "payload_on": "CLOSE",
      "payload_off": "OPEN",
      "state_on": "CLOSED",
      "state_off": "OPEN"
    }
  }
}"""
