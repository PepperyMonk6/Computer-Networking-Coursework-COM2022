from socket import *
import threading
import json
serverSocket = socket(AF_INET, SOCK_DGRAM)
hostName = gethostname()
serverSocket.bind((gethostbyname(hostName), 2500))
temperateSymptoms = [
	"cough",
	"sneeze",
	"fever",
	"headache"
]
seriousSymptoms = [
	"loss of smell",
	"loss of taste",
]
clientMAP = {}


def getSymptomsResult(msg):
	temCounter = 0
	seriousCounter = 0
	array = msg.split(", ")
	for i in range(0, len(temperateSymptoms)):
		for j in range(0, len(array)):
			if array[j].lower() == temperateSymptoms[i].lower():
				temCounter = temCounter+1
	for i in range(0, len(seriousSymptoms)):
		for j in range(0, len(array)):
			if array[j].lower() == seriousSymptoms[i].lower():
				seriousCounter = seriousCounter+1
	respond = ""
	if seriousCounter > 0:
		respond = "serious symptoms"
	elif seriousCounter == 0 and temCounter >= 0 and temCounter <= 2:
		respond = "no symptoms"
	elif seriousCounter == 0 and temCounter >= 3:
		respond = "temperate symptoms"
	return respond


def checksum(msg):
    s = 0
    for i in range(0, len(msg)):
        s += ord(msg[i])
    return s

def broadcast(msg):	
	records = {
		"checksum": checksum(msg),
		"message": msg,
		"flagType": "BROADCAST",
	}
	records = json.dumps(records)
	for client in clientMAP:
		serverSocket.sendto(records.encode("ascii"), client)
	

def handleSymptoms(respond, address):
	result = getSymptomsResult(respond)
	name = clientMAP[address]
	msg = name + " has " + result
	broadcast(message)
	msg = "Instructions:\nPress 1 to send any symptoms you are experiencing\nPress 0 to leave the server\n"
	records = {
		"checksum": checksum(msg),
		"message": msg,
		"flagType": "REPLY",
	}
	records = json.dumps(records)
	serverSocket.sendto(records.encode("ascii"), address)


def connectClient(address, name):
	if len(clientMAP) < 4:
		records = {
			"checksum": checksum("You have joined the sevrver"),
			"message": "You have joined the sevrver",
			"flagType": "ESTAB",
		}
		records = json.dumps(records)
		serverSocket.sendto(records.encode("ascii"), address)
		msg = "Client " + name + " joined"
		broadcast(msg)
		clientMAP[address] = name
		msg = "Instructions:\nPress 1 to send any symptoms you are experiencing\nPress 0 to leave the server\n"
		records = {
			"checksum": checksum(msg),
			"message": msg,
			"flagType": "REPLY",
		}
		records = json.dumps(records)
		serverSocket.sendto(records.encode("ascii"), address)
	else:
		msg = "Denial of Service"
		dataToSend = {
			"checksum": checksum(msg),
			"message": msg,
			"flagType": "QUIT",
		}	
		dataToSend = json.dumps(dataToSend)
		serverSocket.sendto(dataToSend.encode("ascii"), address)


def removeClient(address):
	name = clientMAP[address]
	msg = "Client " + name + " has left"
	dataToSend = {
		"checksum": checksum(msg),
		"message": msg,
		"flagType": "QUIT",
	}	
	dataToSend = json.dumps(dataToSend)
	serverSocket.sendto(dataToSend.encode("ascii"), address)
	del clientMAP[address]
	broadcast(msg)


def receive():
	while True:
		dataPacket = serverSocket.recvfrom(1024)
		clientData = (dataPacket[0]).decode('ascii')
		clientAddress = dataPacket[1]
		records = json.loads(clientData)
		if records["flagType"] == "ESTAB":
			connectClient(clientAddress, records["message"])
		elif records["message"] == "1" and records["flagType"] == "REPLY":
			msg = "How are you feeling today?\nEnter symptoms seperated by comma and space\n"
			dataToSend = {
				"checksum": checksum(msg),
				"message": msg,
				"flagType": "REPLY",
			}	
			dataToSend = json.dumps(dataToSend)
			serverSocket.sendto(dataToSend.encode("ascii"), clientAddress)

		elif records["message"] == "0" and records["flagType"] == "QUIT":
			removeClient(clientAddress)

		elif records["flagType"] == "REPLY":
			handleSymptoms(records["message"], clientAddress)
print('Server Started')
thread = threading.Thread(target=receive)
thread.start()

