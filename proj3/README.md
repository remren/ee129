# EE129 - Project 3, Open Python Project
## How to Run This Project
Requirements: Python, required packages in requirements.txt

0. Find the local IP address of your device by typing in "ipconfig" into Powershell or cmd, and get the IPv4 address.
1. Start the mosquitto MQTT broker that is packaged with this folder, which will act as the server.
   1. This unfortunately requires Windows to use this specific broker. Alternatives should be good to use, however instructions will not be provided.
   2. Open Powershell and navigate into the folder "mosquitto" depending on file structure, e.g. final path should have: "cd proj3/mosquitto-master"
   3. To start the broker (Port set to 1883 in .conf) type in Powershell: .\mosquitto -c mosquitto.conf -v
      3. To find the PID of a rogue mosquitto task running on Port 1883 (will be last number):
      netstat -ano | findstr ":1883"
      4. To kill a specific PID (replace the whole [PID]):
taskkill /PID [PID] /F
   5. To double-check messages if being published from the client are correct, you can subscribe to the broker using mosquitto as well. Open a separate Powershell, repeat steps 1.i to 1.ii and see the "Additional Commands" section below on how to.
6. In an IDE or in a terminal, run the Python script "mqtt_client.py".
   1. For the terminal, this will require the environment to have the paho-mqtt package as listed in the requirements.txt
   2. The command to run the script is: "python mqtt_client.py" or "python3 mqtt_client.py"
7. The client will now prompt the user if they wish to proceed with the default broker address (which is localhost), topic, and random username.
   8. If the user types 'y', the program will proceed, and the user can now send and receive messages via the client.
   9. If 'n', the program will ask for a broker address, topic, and username. The user will be able to send messages afterward.
      1. Note, if clients have the same username, the messages will not be received correctly. This is separate to client id, which is randomly generated and kept private on the MQTT broker.
      2. The default random username attempts to mitigate this by assigning a random number to the name.
      

## Additional Commands
### For mosquitto
- To test subscribing to the broker (replace the whole [IPADDRESS], example topic here is "test"):
.\mosquitto_sub -t "test" -h [IPADDRESS] -p 1883 
- To test publishing to the broker (replace the whole <IPADDRESS>):
.\mosquitto_pub -t "test" -h [IPADDRESS] -p 1883 -m "message"