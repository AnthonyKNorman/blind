device_payload = {
  "dev": {
    "ids": "",
    "name": ""
  },
  "o": {
    "name":""
  },
  "cmps": {
    "sensor1": {
      "p": "binary_sensor",
      "name":"End Stop",
      "state_topic": "",
      "unique_id":"",
      "payload_on": "ON",
      "payload_off": "OFF"
    },
    "offset1": {
      "p": "number",
      "unique_id": "",
      "name":"Offset",
      "min":"-1000",
      "max":"1000",
      "command_topic": "",
      "state_topic": ""
    },
    "closed1": {
      "p": "number",
      "unique_id": "",
      "name":"Closed Position",
      "min":"0",
      "max":"5000",
      "command_topic": "",
      "state_topic": ""
    },
    "strength": {
      "p": "sensor",
      "unique_id": "",
      "name":"WiFi Signal Strength",
      "device_class": "power",
      "state_topic": ""
    },
    "version": {
      "p": "sensor",
      "unique_id": "",
      "name":"OTA Version Number",
      "device_class": "power",
      "state_topic": ""
    },
    "switch1": {
      "p": "cover",
      "unique_id": "",
      "name":"Blind",
      "command_topic": "",
      "state_topic": "",
      "payload_on": "CLOSE",
      "payload_off": "OPEN",
      "state_on": "CLOSED",
      "state_off": "OPEN"
    },
    "button1": {
      "p": "button",
      "unique_id": "",
      "name":"Home",
      "command_topic": "",
      "payload_press": "HOME"
    },
    "reset": {
      "p": "button",
      "unique_id": "",
      "name":"Reset",
      "command_topic": "",
      "payload_press": "RESET"
    }
  }
}

