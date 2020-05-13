import Datebase
import csv
from datetime import datetime
from datetime import timedelta
import paho.mqtt.client as mqtt

#Before_run read README.md
broker = "###"
port = 8883
mqttPassword = "###"
client = mqtt.Client()

def handleCloseUp(card_id, terminal_id):
    now = datetime.now()
    recvTimestamp = datetime.timestamp(now)
    cardUser = Datebase.getUserWithCardId(card_id)
    terminal = Datebase.getTerminalWithId(terminal_id)
    if cardUser is None:
        print("Card id not registered!")
        Datebase.logForbiddenAttempt(recvTimestamp, card_id, terminal_id)
    elif terminal is None:
        print("Card close up to unregistered terminal!")
    else:
        print("card id '{}' belong to '{}' spotted in terminal nr {} - description '{}', at {}".format(cardUser.cardId, cardUser.name ,terminal.terminalId,terminal.terminalDescription,now.strftime("%d/%m/%Y, %H::%M::%S")))
        Datebase.logDoorUsage(recvTimestamp, card_id, terminal_id)

def onMessage(client, userdata, message):
    message_decoded = (str(message.payload.decode("utf-8"))).split(".")
    if message_decoded[0] == "register":
        Datebase.addNewTerminal(Datebase.Terminal(message_decoded[1], message_decoded[2]))
        client.publish("server/ack", "ack" + "." + message_decoded[1])
    elif message_decoded[0] == "closeup":
        cardId     = message_decoded[1]
        terminalId = message_decoded[2]
        handleCloseUp(cardId, terminalId)
		
def init():
    client.tls_set("ca.crt")
    client.username_pw_set(username='server', password=mqttPassword)
    client.connect(broker,port)
    client.on_message = onMessage
    client.loop_start()
    client.subscribe("terminal/closeup")
    client.subscribe("terminal/register")

def addUser():
    name = input("Type name ")
    cardId = input("Type card id ")
    Datebase.addNewUser(Datebase.User(cardId,name))

def addTerminal():
    terminalId = input("Type terminal ID ")
    terminalDesc = input("Type terminal description ")
    Datebase.addNewTerminal(Datebase.Terminal(terminalId, terminalDesc))

def removeTerminal():
    terminalId = input("Type termina ID to delete ")
    Datebase.removeTerminalById(terminalId)

def removeUser():
    userName = input("Type user name to delete ")
    Datebase.removeUserByName(userName)

def generateRaport():
    userName = input("Type user name of which you want to create raport ")
    user = Datebase.getUserWithName(userName)
    userHistory = Datebase.getUserHistory(user)
    doorAccessTime = [item[1] for item in userHistory]
    entryTime = doorAccessTime[::2]
    exitTime = doorAccessTime[1::2]
    timeInWork = sum(exitTime) - sum(entryTime)
    workHours = timeInWork/3600
    with open('raport.csv', mode='a+', newline='') as logFile:
        logWriter = csv.writer(logFile, delimiter=',', quotechar='"')
        logWriter.writerow(["{}".format(user.name), workHours])

operationSwitch = {
    "1":addUser,
    "2":addTerminal,
    "3":removeUser,
    "4":removeTerminal,
    "5":generateRaport
}

def mainLoop():
    print("Server options:")
    print("")
    print("1. to add new card")
    print("2. to add new terminal")
    print("3. to remove card (from datebase)")
    print("4. to remove terminal (from datebase)")
    print("5. to generate csv raport")
    operation = input()
    operationSwitch[operation]()

if __name__ == "__main__":
    init()
    while True:
        mainLoop()

