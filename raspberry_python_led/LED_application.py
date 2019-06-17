import RPi.GPIO as GPIO
import config as config
from AzureIOTHubCommandListener import *

CONNECTION_STRING = config.CONNECTION_STRING
LED_PIN = config.LED_PIN

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN,GPIO.OUT)

iotHubConnection = AzureIOTHubCommandListener(CONNECTION_STRING)

def runMainApplication():
    iotHubConnection.startWaitForCommandsLoop(onCommandReceivedCallback)

def onCommandReceivedCallback(msg):
    if msg == "led on":
        print("Led ON")
        GPIO.output(LED_PIN, GPIO.HIGH)
    elif msg == "led off":
        print("Led Off")
        GPIO.output(LED_PIN, GPIO.LOW)
    else:
        print("Unknown command!")

if __name__ == '__main__':
    print ( "Starting the LED Application" )
    print ( "    Connection string=%s" % CONNECTION_STRING )

    runMainApplication()