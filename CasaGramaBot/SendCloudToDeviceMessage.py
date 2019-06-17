import logging
import os.path
import time

from iothub_service_client import IoTHubMessaging, IoTHubMessage, IoTHubError

OPEN_CONTEXT = 0
MESSAGE_COUNT = 1

with open('properties/CONNECT_STRING.txt', 'r') as connection_string:
    CONNECTION_STRING = connection_string.read()
with open('properties/LED_DEVICE.txt', 'r') as led_device:
    DEVICE_ID = led_device.read()

# $LOGPATH has to be changed
output_dir = "$LOGPATH"
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler(os.path.join(output_dir, "logs.log")),
                        logging.StreamHandler()
                    ])


def open_complete_callback(context):
    LOG.info('      open_complete_callback called with context: {0}'.format(context))


def send_complete_callback(context, messaging_result):
    LOG.info('      send_complete_callback called with context : {0}'.format(context))
    LOG.info('      messagingResult : {0}'.format(messaging_result))


def iothub_message_raspberry(command):
    try:
        iothub_messaging = IoTHubMessaging(CONNECTION_STRING)
        iothub_messaging.open(open_complete_callback, OPEN_CONTEXT)

        for i in range(0, MESSAGE_COUNT):
            msg_txt_formatted = command
            LOG.info("      Sending message: [%s]", msg_txt_formatted)
            message = IoTHubMessage(bytearray(msg_txt_formatted, 'utf8'))

            iothub_messaging.send_async(DEVICE_ID, message, send_complete_callback, i)
            time.sleep(3)
            iothub_messaging.close()

    except IoTHubError as iothub_error:
        LOG.error("IoT Hub error detected")
        LOG.error("Unexpected error %s from IoTHub", iothub_error)
        return
    except KeyboardInterrupt:
        LOG.error("Messaging has stopped")
