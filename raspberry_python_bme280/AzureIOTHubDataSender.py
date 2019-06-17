import random
import time
import sys
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue
import config as config
from Adafruit_BME280 import *
import re
from telemetry import Telemetry

# HTTP options
# Because it can poll "after 9 seconds" polls will happen effectively
# at ~10 seconds.
# Note that for scalabilty, the default value of minimumPollingTime
# is 25 minutes. For more information, see:
# https://azure.microsoft.com/documentation/articles/iot-hub-devguide/#messaging
TIMEOUT = 241000
MINIMUM_POLLING_TIME = 9


# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

RECEIVE_CONTEXT = 0
MESSAGE_SWITCH = True
TWIN_CONTEXT = 0
SEND_REPORTED_STATE_CONTEXT = 0
METHOD_CONTEXT = 0
TEMPERATURE_ALERT = 30.0

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0
BLOB_CALLBACKS = 0
TWIN_CALLBACKS = 0
SEND_REPORTED_STATE_CALLBACKS = 0
METHOD_CALLBACKS = 0
EVENT_SUCCESS = "success"
EVENT_FAILED = "failed"

# chose HTTP, AMQP or MQTT as transport protocol
PROTOCOL = IoTHubTransportProvider.MQTT


class AzureIOTHubDataSender:

    def __init__(self, connectionString):

        self.CONNECTION_STRING = connectionString
        self.MESSAGE_COUNT = 0
        self.telemetry = Telemetry()
        self.client = self.iothubClientInit()

        if self.client.protocol == IoTHubTransportProvider.MQTT:
            print ( "IoTHubClient is reporting state" )
            reported_state = "{\"newState\":\"standBy\"}"
            self.client.send_reported_state(reported_state, len(reported_state), self.sendReportedStateCallback, SEND_REPORTED_STATE_CONTEXT)

        self.telemetry.send_telemetry_data(self.parseIOTHubName(self.CONNECTION_STRING), EVENT_SUCCESS, "IoT hub connection is established")

        return

    def iothubClientInit(self):
        # prepare iothub client
        client = IoTHubClient(self.CONNECTION_STRING, PROTOCOL)
        client.set_option("product_info", "HappyPath_RaspberryPi-Python")

        if client.protocol == IoTHubTransportProvider.HTTP:
            client.set_option("timeout", TIMEOUT)
            client.set_option("MinimumPollingTime", MINIMUM_POLLING_TIME)

        # set the time until a message times out
        client.set_option("messageTimeout", MESSAGE_TIMEOUT)

        # to enable MQTT logging set to 1
        if client.protocol == IoTHubTransportProvider.MQTT:
            client.set_option("logtrace", 0)

        # set callback after a message is received
        client.set_message_callback(self.receiveMessageCallback, RECEIVE_CONTEXT)

        # if MQTT or MQTT_WS is used -> set device twin callback
        if client.protocol == IoTHubTransportProvider.MQTT or client.protocol == IoTHubTransportProvider.MQTT_WS:
            client.set_device_twin_callback(self.deviceTwinCallback, TWIN_CONTEXT)
            client.set_device_method_callback(self.deviceMethodCallback, METHOD_CONTEXT)
            
        return client

    # Sends the given string to the Azure IOT Hub
    def sendStringToIOTHub(self, messageString):
        message = IoTHubMessage(messageString)
        message.message_id = "message_%d" % self.MESSAGE_COUNT
        message.correlation_id = "correlation_%d" % self.MESSAGE_COUNT

        self.client.send_event_async(message, self.sendConfirmationCallback, self.MESSAGE_COUNT)

        status = self.client.get_send_status()

        print ( "Send status: %s" % status )
        self.MESSAGE_COUNT += 1

    def receiveMessageCallback(self, message, counter):
        global RECEIVE_CALLBACKS
        message_buffer = message.get_bytearray()
        size = len(message_buffer)
        print ( "Received Message [%d]:" % counter )
        print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode("utf-8"), size) )
        map_properties = message.properties()
        key_value_pair = map_properties.get_internals()
        print ( "    Properties: %s" % key_value_pair )
        counter += 1
        RECEIVE_CALLBACKS += 1
        print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
        return IoTHubMessageDispositionResult.ACCEPTED

    def sendConfirmationCallback(self, message, result, user_context):
        global SEND_CALLBACKS
        print ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
        map_properties = message.properties()
        print ( "    message_id: %s" % message.message_id )
        print ( "    correlation_id: %s" % message.correlation_id )
        key_value_pair = map_properties.get_internals()
        print ( "    Properties: %s" % key_value_pair )
        SEND_CALLBACKS += 1
        print ( "    Total calls confirmed: %d" % SEND_CALLBACKS )

    def deviceTwinCallback(self, update_state, payload, user_context):
        global TWIN_CALLBACKS
        print ( "\nTwin callback called with:\nupdateStatus = %s\npayload = %s\ncontext = %s" % (update_state, payload, user_context) )
        TWIN_CALLBACKS += 1
        print ( "Total calls confirmed: %d\n" % TWIN_CALLBACKS )


    def sendReportedStateCallback(self, status_code, user_context):
        global SEND_REPORTED_STATE_CALLBACKS
        print ( "Confirmation for reported state received with:\nstatus_code = [%d]\ncontext = %s" % (status_code, user_context) )
        SEND_REPORTED_STATE_CALLBACKS += 1
        print ( "    Total calls confirmed: %d" % SEND_REPORTED_STATE_CALLBACKS )

    def deviceMethodCallback(self, method_name, payload, user_context):
        global METHOD_CALLBACKS,MESSAGE_SWITCH
        print ( "\nMethod callback called with:\nmethodName = %s\npayload = %s\ncontext = %s" % (method_name, payload, user_context) )
        METHOD_CALLBACKS += 1
        print ( "Total calls confirmed: %d\n" % METHOD_CALLBACKS )
        device_method_return_value = DeviceMethodReturnValue()
        device_method_return_value.response = "{ \"Response\": \"This is the response from the device\" }"
        device_method_return_value.status = 200
        if method_name == "start":
            MESSAGE_SWITCH = True
            print ( "Start sending message\n" )
            device_method_return_value.response = "{ \"Response\": \"Successfully started\" }"
            return device_method_return_value
        if method_name == "stop":
            MESSAGE_SWITCH = False
            print ( "Stop sending message\n" )
            device_method_return_value.response = "{ \"Response\": \"Successfully stopped\" }"
            return device_method_return_value
        return device_method_return_value

    def print_last_message_time(self, client):
        try:
            last_message = client.get_last_message_receive_time()
            print ( "Last Message: %s" % time.asctime(time.localtime(last_message)) )
            print ( "Actual time : %s" % time.asctime() )
        except IoTHubClientError as iothub_client_error:
            if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
                print ( "No message received" )
            else:
                print ( iothub_client_error )

    def parseIOTHubName(self, CONNECTION_STRING):
        m = re.search("HostName=(.*?)\.", CONNECTION_STRING)
        return m.group(1)
