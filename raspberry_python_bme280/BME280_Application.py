from AzureIOTHubDataSender import *
from Adafruit_BME280 import *
from time import sleep
import config as config

CONNECTION_STRING = config.CONNECTION_STRING
MSG_TXT = "{\"deviceId\": \"Raspberry Pi - Python\",\"temperature\": %f,\"humidity\": %f,\"pressure\": %f}"
SLEEP_DELAY_IN_S = config.SLEEP_DELAY_IN_S
sensor = BME280(address = config.I2C_ADDRESS)
iotHubConnection = AzureIOTHubDataSender(CONNECTION_STRING)


def readDataStringFromSensor(sensor):
    temperature = sensor.read_temperature()
    humidity = sensor.read_humidity()
    pressure = sensor.read_pressure()

    msg_txt_formatted = MSG_TXT % (
        temperature,
        humidity,
        pressure)

    return msg_txt_formatted


def runMainApplicationLoop(iotHubConnection, sensor):
    while True:
        message = readDataStringFromSensor(sensor)
        print("Sending following Message to the Azure IoT Hub:")
        print(message)
        iotHubConnection.sendStringToIOTHub(message)
        sleep(SLEEP_DELAY_IN_S)

if __name__ == "__main__":
    print ( "\nPython %s" % sys.version )
    print ( "IoT Hub Client for Python" )

    runMainApplicationLoop(iotHubConnection, sensor)