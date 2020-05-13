import paho.mqtt.client as mqtt
import time


#Before_run read README.md
broker = "###"
port = 8883
mqttPassword = "###"
client = mqtt.Client()

terminal_id = input("Type terminal id ")
terminal_description = input("Type terminal description ")
connected = False

def onMessage(client, userdata, message):
    message_decoded = (str(message.payload.decode("utf-8"))).split(".")
    if message_decoded[0] == "ack":
        if message_decoded[1] == terminal_id:
            global connected
            connected = True
            print("Ack received")
		
def init():
    client.tls_set("ca.crt")
    client.username_pw_set(username='client', password=mqttPassword)
    client.connect(broker,port)
    client.on_message = onMessage
    client.loop_start()
    client.subscribe("server/ack")
    client.publish("terminal/register", "register" + "." + terminal_id + "." + terminal_description)
    print("Waiting for ack from server")
    time.sleep(1.0)

def callAboutCloseUp(card_id):
    client.publish("terminal/closeup", "closeup" + "." + card_id + "." + terminal_id)

def closeUpCheckerLoop():
    print("New close-up")
    card_id = input("Type ID of card ")
    callAboutCloseUp(card_id)

if __name__ == "__main__":
    init()
    while not connected:
        client.publish("terminal/register", "register" + "." + terminal_id + "." + terminal_description)
        time.sleep(1.0)
		
    while True:
        closeUpCheckerLoop()