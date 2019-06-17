import time
import sys
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError
import time


class AzureIOTHubCommandListener:

    def __init__(self, connection_string):
        self.CONNECTION_STRING = connection_string
        self.PROTOCOL = IoTHubTransportProvider.AMQP

        self.receive_callbacks = 0
        self.wait_count = 10
        self.RECEIVE_CONTEXT = 0

        return


    def receiveMessageCallback(self, message, counter):
        message_buffer = message.get_bytearray()
        size = len(message_buffer)
        print ( "Received Message [%d]:" % counter )
        print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
        msg = message_buffer[:size].decode('utf-8')
        map_properties = message.properties()
        key_value_pair = map_properties.get_internals()
        print ( "    Properties: %s" % key_value_pair )
        counter += 1
        self.receive_callbacks += 1
        print ( "    Total calls received: %d" % receive_callbacks )

        self.onCommandReceivedCallback(msg)
        
        return IoTHubMessageDispositionResult.ACCEPTED


    def iothubClientInit(self):
        client = IoTHubClient(self.CONNECTION_STRING, self.PROTOCOL)

        client.set_message_callback(self.receiveMessageCallback, self.RECEIVE_CONTEXT)

        return client

    def startWaitForCommandsLoop(self, onCommandReceivedCallback):
        self.onCommandReceivedCallback = onCommandReceivedCallback
        try:
            client = self.iothubClientInit()

            while True:
                print ( "IoTHubClient waiting for commands, press Ctrl-C to exit" )

                status_counter = 0
                while status_counter <= self.wait_count:
                    status = client.get_send_status()
                    print ( "Send status: %s" % status )
                    time.sleep(10)
                    status_counter += 1

        except IoTHubError as iothub_error:
            print ( "Unexpected error %s from IoTHub" % iothub_error )
            return
        except KeyboardInterrupt:
            print ( "IoTHubClient sample stopped" )