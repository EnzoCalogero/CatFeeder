#!/usr/bin/python


import argparse
import datetime
import time
from time import gmtime, strftime
import subprocess
import random
import ssl

import jwt
import paho.mqtt.client as mqtt

##########################################################


import RPi.GPIO as GPIO  # import GPIO
from hx711 import HX711  # import the class HX711
from gpiozero import LightSensor, Buzzer
#import dht11
import Adafruit_DHT
GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
#GPIO.cleanup()

def temp_humid_val_old():
    instance = dht11.DHT11(pin=17)
    result = instance.read()
    temp = result.temperature
    hump = result.humidity
    return (temp, hump)

def temp_humid_val():
    pin = 17
    sensor = Adafruit_DHT
    sensor = Adafruit_DHT.DHT11
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return (humidity, temperature)

def weight_val():
    hx = HX711(dout_pin=5, pd_sck_pin=6)  # create an object
    val = hx.get_raw_data_mean()
    val = int((val + 206000.)/(-961.))
    print(val)  # get raw data reading from hx711
    #GPIO.cleanup()
    return val


def light_val():
    ldr = LightSensor(4)  # alter if using a different pin
    return ldr.value


##########################################################
# The initial backoff time after a disconnection occurs, in seconds.
minimum_backoff_time = 1

# The maximum backoff time before giving up, in seconds.
MAXIMUM_BACKOFF_TIME = 32

# Whether to wait with exponential backoff before publishing.
should_backoff = False

def create_jwt(project_id, private_key_file, algorithm):
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
    Args:
     project_id: The cloud project ID this device belongs to
     private_key_file: A path to a file containing either an RSA256 or ES256
         private key.
     algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
    Returns:
      An MQTT generated from the given project_id and private key, which
      expires in 20 minutes. After 20 minutes, your client will be
      disconnected, and a new JWT will have to be generated.
    Raises:
      ValueError: If the private_key_file does not contain a known key.
    """

    token = {
        # The time that the token was issued at
        'iat': datetime.datetime.utcnow(),
        # When this token expires. The device will be disconnected after the
        # token expires, and will have to reconnect.
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        # The audience field should always be set to the GCP project id.
        'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print(
            'Creating JWT using {} from private key file {}'.format(
                    algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print('on_connect', error_str(rc))
    # After a successful connect, reset backoff time and stop backing off.
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))
    # Since a disconnect occurred, the next loop iteration will wait with
    # exponential backoff.
    global should_backoff
    should_backoff = True


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    print('on_publish')
# python3 pi_cpu_temp_mqtt.py --project_id=pi-iot-project-235918 --registry_id=example-registry --device_id=catfeeder --private_key_file=rsa_private.pem --algorithm=RS256

def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
                'Example Google Cloud IoT Core MQTT device connection code.'))
    parser.add_argument(
            '--project_id',
            default="pi-iot-project-235918",
            help='GCP cloud project name')
    parser.add_argument(
            '--registry_id',
            default='example-registry',
            help='Cloud IoT Core registry id')
    parser.add_argument(
            '--device_id',
            default='catfeeder',

            help='Cloud IoT Core device id')
    parser.add_argument(
            '--private_key_file',
            default='rsa_private.pem',
            help='Path to private key file.')
    parser.add_argument(
            '--algorithm',
            choices=('RS256', 'ES256'),
            default='RS256',
            help='Which encryption algorithm to use to generate the JWT.')
    parser.add_argument(
            '--cloud_region', default='us-central1', help='GCP cloud region')
    parser.add_argument(
            '--ca_certs',
            default='roots.pem',
            help=('CA root certificate from https://pki.google.com/roots.pem'))
    parser.add_argument(
            '--mqtt_bridge_hostname',
            default='mqtt.googleapis.com',
            help='MQTT bridge hostname.')
    parser.add_argument(
            '--mqtt_bridge_port', default=8883, help='MQTT bridge port.')

    return parser.parse_args()


def main():
    global minimum_backoff_time
    args = parse_command_line_args()

    # Create our MQTT client. The client_id is a unique string that identifies
    # this device. For Google Cloud IoT Core, it must be in the format below.
    client = mqtt.Client(
            client_id=(
                    'projects/{}/locations/{}/registries/{}/devices/{}'
                    .format(
                            args.project_id, args.cloud_region,
                            args.registry_id, args.device_id)))

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    args.project_id, args.private_key_file, args.algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=args.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Connect to the Google MQTT bridge.
    client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)

    # Start the network loop.
    client.loop_start()

    # Wait if backoff is required.
    if should_backoff:
        # If backoff time is too large, give up.
        if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
            print('Exceeded maximum backoff time. Giving up.')
        else:
            # Otherwise, wait and connect again.
            delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
            print('Waiting for {} before reconnecting.'.format(delay))
            time.sleep(delay)
            minimum_backoff_time *= 2
            client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)

    mqtt_topic = '/devices/{}/events'.format(args.device_id)

    # Get the Raspberry Pi's processor temperature. 
    #temp = 40
    weight = weight_val()
    #while (True):
    payload='{'
    payload=payload + '"device":"{}",'.format(args.device_id)
    payload=payload + '"time":"{}",'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    payload=payload + '"sensor":"{}",'.format("Weight")
    payload=payload + '"val":{}'.format( weight)
    payload=payload + '}'
    
    #temp = weight_val()
    #while (True):
    #payload = '{}/{} Time {} temperature {}'.format(
    #            args.registry_id, args.device_id, strftime("%Y-%m-%d %H:%M:%S", gmtime()), temp)
    print('Publishing message for weight {}'.format(payload))
    # Publish "payload" to the MQTT topic. qos=1 means at least once
    # delivery. Cloud IoT Core also supports qos=0 for at most once
    # delivery.
    client.publish(mqtt_topic, payload, qos=1)
    #    time.sleep(60 * 15)
    # End the network loop and finish.
    
    ##################
    #  light section #
    ##################
    light=light_val()
    
    payload='{'
    payload=payload + '"device":"{}",'.format(args.device_id)
    payload=payload + '"time":"{}",'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    payload=payload + '"sensor":"{}",'.format("Light")
    payload=payload + '"val":{}'.format(light)
    payload=payload + '}'
   
    print('Publishing message for light {}'.format(payload))
    client.publish(mqtt_topic, payload, qos=1)
    #################
    # temp          #
    #################
    temp, hum=temp_humid_val()

   
    payload='{'
    payload=payload + '"device":"{}",'.format(args.device_id)
    payload=payload + '"time":"{}",'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    payload=payload + '"sensor":"{}",'.format("Temperature")
    payload=payload + '"val":{}'.format( temp)
    payload=payload + '}'

    print('Publishing message for temperature {}'.format(payload))

    client.publish(mqtt_topic, payload, qos=1)
    #################
    # humidy        #
    #################


    payload='{'
    payload=payload + '"device":"{}",'.format(args.device_id)
    payload=payload + '"time":"{}",'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    payload=payload + '"sensor":"{}",'.format("Humidity")
    payload=payload + '"val":{}'.format( hum)
    payload=payload + '}'

   
    print('Publishing message for humidy {}'.format(payload))
    
    client.publish(mqtt_topic, payload, qos=1)
    client.loop_stop()


    print('Finished.')


if __name__ == '__main__':
    main()
