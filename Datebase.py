import json
import csv
from datetime import datetime

TERMINAL_JSON_FILE = 'Terminals.json'
CARDS_JSON_FILE = 'EmployeeCards.json'

class User:
    def __init__(self, _cardId, _name):
        self.cardId = _cardId
        self.name = _name

class Terminal:
    def __init__(self, _terminalId, _terminalDescription):
        self.terminalId = _terminalId
        self.terminalDescription = _terminalDescription


## User part
def getUserWithCardId(cardId):
    with open(CARDS_JSON_FILE) as json_file:
        EmployeeData = json.load(json_file)
        for employee in EmployeeData:
            if employee['CardId'] == str(cardId):
                return User(employee['CardId'], employee['Name'])

def getUserWithName(name):
    with open(CARDS_JSON_FILE) as json_file:
        EmployeeData = json.load(json_file)
        for employee in EmployeeData:
            if employee['Name'] == str(name):
                return User(employee['CardId'], employee['Name'])

def addNewUser(user):
    with open(CARDS_JSON_FILE) as json_file:
        employeeData = json.load(json_file)
        employeeData.append({
            'Name'  : user.name,
            'CardId': user.cardId
        })
        with open(CARDS_JSON_FILE,'w') as json_file:
            json.dump(employeeData, json_file, indent=4)

def removeUserByName(name):
    with open(CARDS_JSON_FILE) as json_file:
        employeeData = json.load(json_file)
        for employee in employeeData:
            if employee['Name'] == str(name):
                employeeData.remove(employee)
                with open(CARDS_JSON_FILE,'w') as json_file:
                    json.dump(employeeData, json_file, indent=4)
##

## Terminal part
def getTerminalWithId(terminalId):
    with open(TERMINAL_JSON_FILE) as json_file:
        terminalData = json.load(json_file)
        for terminal in terminalData:
            if terminal['TerminalId'] == str(terminalId):
                return Terminal(terminal['TerminalId'], terminal['Description'])

def addNewTerminal(terminal):
    with open(TERMINAL_JSON_FILE) as json_file:
        terminalData = json.load(json_file)
        terminalData.append({
            'TerminalId' : terminal.terminalId,
            'Description': terminal.terminalDescription
        })
        with open(TERMINAL_JSON_FILE,'w') as json_file:
            json.dump(terminalData, json_file, indent=4)

def removeTerminalById(terminalId):
    with open(TERMINAL_JSON_FILE) as json_file:
        terminalData = json.load(json_file)
        for terminal in terminalData:
            if terminal['TerminalId'] == str(terminalId):
                terminalData.remove(terminal)
                with open(TERMINAL_JSON_FILE,'w') as json_file:
                    json.dump(terminalData, json_file, indent=4)
##

def logDoorUsage(time, cardId, terminalId):
    with open('log.csv', mode='a+', newline='') as logFile:
        logWriter = csv.writer(logFile, delimiter=',', quotechar='"')
        logWriter.writerow([cardId, terminalId, time])

def logForbiddenAttempt(time, cardId, terminalId):
    with open('errorLog.csv', mode='a+', newline='') as logFile:
        logWriter = csv.writer(logFile, delimiter=',', quotechar='"')
        logWriter.writerow([cardId, terminalId, time])

def getUserHistory(user):
    userHistory = []
    with open('log.csv', newline='') as logfile:
        logs = csv.reader(logfile, delimiter=',', quotechar='"')
        for log in logs:
            if log[0] == user.cardId:
                userHistory.append((log[1],float(log[2])))
    return userHistory