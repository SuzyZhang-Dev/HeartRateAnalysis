import network
from time import sleep
from umqtt.simple import MQTTClient
import ujson
import random
#https://pypi.org/project/ujson/ library ujson

# Replace these values with your own
SSID = "KMD757_Group2"
PASSWORD = "KMD757_Group2"
BROKER_IP = "192.168.2.253"

kubios_result = dict()

class MQTTConnectionError(Exception):
    pass

# Function to connect to WLAN
def connect_wlan():
    # Connecting to the group WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    count = 0

    # Attempt to connect once per second
    while wlan.isconnected() == False:
        if count > 15:
            raise MQTTConnectionError("Internet Connection Failed")
        print("Connecting... ")
        count += 1
        sleep(1)

    # Print the IP address of the Pico
    print("Connection successful. Pico IP:", wlan.ifconfig()[0])
    
def connect_local_mqtt(): #different port
    mqtt_client=MQTTClient("", BROKER_IP,port=1883)
    mqtt_client.connect(clean_session=True)
    return mqtt_client

def connect_kubios_mqtt():
    mqtt_client=MQTTClient("", BROKER_IP,port=21883)
    mqtt_client.connect(clean_session=True)
    mqtt_client.set_callback(subscribe)
    return mqtt_client

def subscribe(topic, msg):
    global kubios_result
    # to receive the message from kubios
    # print('received message %s on topic %s' % (msg, topic))
    # print(ujson.loads(msg))
    kubios_result = ujson.loads(msg)
        

# Local basic analysis through MQTT
def publish_basic_analysis(result):
    connect_wlan()
    
    try:
        mqtt_client = connect_local_mqtt()
    except Exception as e:
        raise MQTTConnectionError(f"Failed to connect to MQTT: {e}")
    
    try:
        topic = "hr-local"
        msg = result
        json_msg = ujson.dumps(msg)
        mqtt_client.publish(topic, json_msg)
    except Exception as e:
        raise MQTTConnectionError(f"Failed to send MQTT message: {e}")


# Main kubios program
def kubios_mqtt_request(data: list[int]) -> dict:
    #Connect to WLAN
    connect_wlan()
    random_number = random.randint(1, 5000)
    
    # Connect to MQTT
    try:
        mqtt_client=connect_kubios_mqtt()
        mqtt_client.subscribe("kubios-response")
        
    except Exception as e:
        raise MQTTConnectionError(f"Failed to connect to MQTT: {e}")
        # print(e)

    # Send MQTT message
    try:
        # Sending a message.
        topic = "kubios-request"
        # data = [] #self.intervals
        msg = {
            "id": random_number,
            "type": "RRI",
            "data": data,
            "analysis": { "type": "readiness" }
        }

        json_msg = ujson.dumps(msg)
        
        mqtt_client.publish(topic, json_msg)
        # print(f"Sending to MQTT: {topic} -> {json_msg}")
        while True:
            mqtt_client.check_msg()
            if kubios_result != dict():
                break
        return kubios_result
            
    except Exception as e:
        raise MQTTConnectionError(f"Failed to send MQTT message: {e}")

# for testing     
# print(kubios_mqtt_request([828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812,
#            812, 756, 820, 812, 800]))