## Barebones mqtt client.
## How to use:
##  - Run this client, either in an IDE or via terminal with Python + required packages installed (requirements.txt):
##      - python3 mqtt_client
##      - python mqtt_client

import time, random
import paho.mqtt.client as mqtt

broker = 'localhost'
port = 1883
topic = 'default'
usn = f"basic_client{random.randint(0, 100)}"
pwd = ""

client_id = f'python-mqtt-{random.randint(0, 1000)}'

# implement terminal input

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == mqtt.CONNACK_ACCEPTED:
        print(f"Connected to MQTT Broker at [{broker}]!")
        print(f"Your username is: {usn}, client ID is: {client_id}. \nType to publish messages (or ':q' to exit):")
        # Subscribe to topic when connected
        client.subscribe(topic)
    else:
        print(f"Failure to connect. Return code={reason_code}")

def on_message(client, userdata, msg):
    try:
        # For debug
        # print(f"Received message: Topic={msg.topic}, QoS={msg.qos}, Payload={msg.payload.decode()}")
        incoming_msg = msg.payload.decode("utf-8")

        # Handle Connects/Disconnects
        if "<>" in incoming_msg:
            parts = incoming_msg.split("<>")
            if len(parts) >= 2:
                if parts[0] in ["disconnect", "connect"]:
                    print(f"\n[topic={topic}] {parts[1]}")
                    return

        # Handle regular messages with username prefix
        if ":" in incoming_msg:
            parts = incoming_msg.split(":", 1)  # Split only on first colon
            if len(parts) >= 2:
                sender = parts[0].strip()
                message_content = parts[1].strip()

                if sender != usn and sender != "":
                    print(f"\n[topic={topic}] {incoming_msg}")
                # If sender == usn, do nothing (don't echo own messages)
                return

        # Handle other messages
        print(f"\n[topic={topic}] External MQTT Client MSG: {incoming_msg}")
    except Exception as e:
        print(f"Error processing message: {e}")

def connect_mqtt(client):
    client.username_pw_set(username=usn, password=pwd)
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(broker, port)
        publish(client, topic, f"connect<>{usn} has connected.")
    except Exception as e:
        print(f"Error connecting to MQTT Broker: {e}")
        exit(1)
    return client

def publish(client, topic, payload):
    result = client.publish(topic, payload)
    status = result.rc
    ## For Debug
    if payload.split("<>")[0] == "disconnect" or "connect":
        time.sleep(1)
        return
    if status == mqtt.MQTT_ERR_SUCCESS:
        print(f"[topic={topic}] {payload}")
    else:
        print(f"Failed to publish message to {topic}")
    time.sleep(1)

def run(client):
    client.loop_start()
    time.sleep(1)  # Sleep needed to give time for connection to establish

    try:
        while True:
            user_input = input("> ")
            if user_input == ':q':
                publish(client, topic, f"disconnect<>{usn} has disconnected.")
                print("\nExiting...")
                break
            # Publish user input
            publish(client, topic, f"{usn}: {user_input}")

    except KeyboardInterrupt:
        publish(client, topic, f"disconnect<>{usn} has disconnected.")
        print("\nExiting...")
    finally:
        client.loop_stop()
        client.disconnect()

# Request user's topic of choice and username
print("Connect to default IP, test topic, and use random username? Type y/n")
try:
    while True:
        user_input = input("> ")
        if user_input.lower() == 'y':
            break
        elif user_input.lower() == 'n':
            print("Enter the address for the broker:")
            broker = input("> ")
            print("\nEnter your topic:")
            topic = input("> ")
            print("\nEnter your username:")
            usn = input("> ")
            break
        else:
            print("\nPlease enter a y or n response.")
except KeyboardInterrupt:
    print("\nExiting...")
    exit(0)

# Create and connect client
client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client = connect_mqtt(client)

# Start the main loop
run(client)