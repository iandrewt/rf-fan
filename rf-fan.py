import json
import time
import RPi.GPIO as GPIO
from flask import Flask, request, jsonify

app = Flask(__name__)
config_file_path = "config.json"

device_states = {}

@app.route("/fan/api/v1.0/status", methods=["GET"])
def getStatus():
    device_id = request.args.get('id')
    if device_id == None:
        info = json.loads(request.data)
        device_id = info["id"]
    response = {}
    response["id"] = int(device_id)
    if device_id in device_states:
        response["speed"] = int(device_states[device_id])
    else:
        response["speed"] = 0
    return json.dumps(response)

@app.route("/fan/api/v1.0/update", methods=["GET","POST"])
def update():
    device_id = ""
    speed = ""
    if request.method == "GET":
        device_id = request.args.get('id')
        speed = request.args.get('speed')
    else:
        device_dict = json.loads(request.data)
        device_id = device_dict["id"]
        speed = device_dict["speed"]
    device_states[device_id] = speed
    signal = getGpioSignal(int(device_id), int(speed))
    response = {}
    if signal is not None:
        gpioSend(signal)
        response["id"] = int(device_id)
        response["speed"] = int(speed)
        response["success"] = 1
    else:
        response["success"] = 0
    return json.dumps(response)

def getGpioSignal(device_id, speed):
    config_file = open(config_file_path,"r")
    config_info = config_file.read()
    config_json_info = json.loads(config_info)
    accessories = config_json_info["accessories"]
    for accessory in accessories:
        accessory_id = accessory["id"]
        if accessory_id == device_id:
            gpio_start = accessory["gpio_start"]
            gpio_end = accessory["gpio_end"]
            gpio_speeds = accessory["gpio_speeds"]
            for gpio in gpio_speeds:
                gpio_speed = gpio["speed"]
                gpio_signal = gpio["signal"]
                if gpio_speed == speed:
                    return gpio_start + gpio_signal + gpio_end
    return None

def gpioSend(signal):
    config_file = open(config_file_path,"r")
    config_info = config_file.read()
    config_json_info = json.loads(config_info)
    gpio_pin = config_json_info["gpio_pin"]
    num_attempts = config_json_info["num_attempts"]
    short_on = config_json_info["short_on"]
    short_off = config_json_info["short_off"]
    long_on= config_json_info["long_on"]
    long_off= config_json_info["long_off"]
    extra_off = config_json_info["extra_off"]

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.OUT)
    for t in range(num_attempts):
        for i in signal:
            if i == '1':
                time.sleep(long_off)
                GPIO.output(gpio_pin, 1)
                time.sleep(short_on)
                GPIO.output(gpio_pin, 0)
            elif i == '0':
                time.sleep(short_off)
                GPIO.output(gpio_pin, 1)
                time.sleep(long_on)
                GPIO.output(gpio_pin, 0)
            else:
                continue
        GPIO.output(gpio_pin, 0)
        time.sleep(extra_off)
    GPIO.cleanup()

if __name__ == '__main__':
    app.run()
