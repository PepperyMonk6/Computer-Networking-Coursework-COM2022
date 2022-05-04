import socket
import json
hostName = socket.gethostname()
SERVER_ADDRESS = (socket.gethostbyname(hostName), 2500)
offline = False
connectionEstablished = False
clienSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
global clientName


def checksum(msg):
    s = 0
    for i in range(0, len(msg)):
        s += ord(msg[i])
    return s


def send(dMsg, checksum, flagType):
    while True:
        try:
            records = {
                "checksum": checksum,
                "message": dMsg,
                "flagType": flagType
            }
            records = json.dumps(records)
            clienSocket.sendto(records.encode('ascii'), SERVER_ADDRESS)
        except socket.timeout:
            print("Time out, retransmitting\n")
            continue
        except:
            pass
            print('Server is off\n')
            clienSocket.close()
            break
        receive()
        break


def respond():
    global connectionEstablished
    global clientName
    global offline
    global flagType
    inpData = ""
    while inpData == "" or inpData == None:
        inpData = f'{input("")}'
    checkSum = checksum(inpData)
    if not connectionEstablished:
        connectionEstablished = True
        clientName = inpData
        flagType = "ESTAB"
    elif inpData == "0":
        offline = True
        flagType = "QUIT"
    else:
        flagType = "REPLY"
    send(inpData, checkSum, flagType) 


def receive():
    try:
        dataPacket = clienSocket.recvfrom(1024)     
        serverData = (dataPacket[0]).decode('ascii') 
        records = json.loads(serverData)
        if records["flagType"] != "NAK":
            if records["flagType"] == "BROADCAST":
                print(records["message"] + "\n")
                receive()
            elif records["flagType"] == "QUIT":
                print(records["message"] + "\n")
                clienSocket.close()
            elif records["flagType"] == "ACK":
                print("ACK packet recived\n")
                receive()
            elif records["flagType"] == "ESTAB":
                print("Connected to server\n")
                receive()
            elif records["flagType"] == "REPLY":
                print(records["message"] + "\n")
                respond()                
        else:
            print("recived NAK, retransmitting\n")
            flagType = None
            if records["message"] == clientName:
                flagType = "ESTAB"
            elif records["message"] == "0":
                flagType = "QUIT"
            else:
                flagType = "REPLY"
            send(records["message"], checksum(records["message"]), flagType)
    except:
        pass                    


print("Enter your name")
respond()






