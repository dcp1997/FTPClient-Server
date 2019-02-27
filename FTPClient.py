#Devin Puckett
import sys
import shutil
import os.path
import re
import socket
#checks validity of the reply sent from the server
def replyParse(reply):
    import sys
    inp = reply
    errorOK = True
    inpU = inp.upper()
    if not inp.count(" ") >= 1:
        print("ERROR -- reply-code")
        return
    errorCode, rest = inp.split(" ", 1)
    # checks to see if the error code is of the correct format
    if len(errorCode) > 3:
        print("ERROR -- reply-code")
        return
    errorCode = int(errorCode)
    # checks for the error code to be in the correct range
    if errorCode > 599 or errorCode < 100:
        print("ERROR -- reply-code")
        return
    if inp[3] == " " and errorCode in range(100, 599):
        # checks for non ASCII characters
        for letter in range(4, len(inp)):
            if ord(inp[letter]) > 127 or ord(inp[letter]) < 0:
                errorOK = False
                print("ERROR -- reply-text")
                return
    if errorOK:
        # checks for CRLF at end of error message
        if not ord(inp[-1]) == 10 or not ord(inp[-2]) == 13:
            print("ERROR -- <CRLF>")
            return
        else:
            print("FTP reply " + str(errorCode) + " accepted. Text is: " + rest.rstrip("\r\n"))
            return
def main():
    connected = False
    portNum = int(sys.argv[1])
    controlSock = socket.socket()
    getCount = 0
    for line in sys.stdin:
        inpU = line.upper()
        inpU = inpU.strip("'")
        if inpU.startswith("CONNECT"):
            #checks for a space between the command and the host
            if not inpU[7] == " ":
                print(line.rstrip("\r\n"))
                print("ERROR -- request")
                continue
            sp = inpU.split()
            #checks to see that a host and port have been specified
            if not len(sp) == 3:
                print(line.rstrip("\r\n"))
                print("ERROR -- server-host")
                continue
            conInp1, conInp2, conInp3 = line.split(" ")
            strippedHost = conInp2.strip(".")
            #checks to see if the domain contains only alphanumeric characters
            if not re.match("[a-zA-Z0-9]*", strippedHost):
                print(line.rstrip("\r\n"))
                print("ERROR -- server-host")
                connectOK = False
                continue
            #checks that the port is a number
            if not re.match("[0-9]*", conInp3):
                print (line.rstrip("\r\n"))
                print("ERROR -- server-host")
                continue
            conInp3 = int(conInp3)
            #checks for the correct range of the port number
            if conInp3>65535 or conInp3<0:
                print(line.rstrip("\r\n"))
                print("ERROR -- server-port")
                continue
            else:
                connected = True
                port = conInp3
                print(line.rstrip("\r\n"))
                print("CONNECT accepted for FTP server at host " + conInp2 + " and port " + str(conInp3))
                if not controlSock == None:
                    controlSock.close()
                controlSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try: controlSock.connect((strippedHost, port))
                except(socket.error):
                    print("CONNECT failed")
                    connected = False
                    continue
                #receives initial reply from server, and then logs in to server
                reply = controlSock.recv(4096).decode()
                replyParse(reply)
                sys.stdout.write("USER anonymous"+"\r\n")
                U = "USER anonymous\r\n"
                controlSock.send(U.encode())
                UReply = controlSock.recv(4096).decode()
                replyParse(UReply)
                sys.stdout.write("PASS guest@"+"\r\n")
                P = "PASS guest@\r\n"
                controlSock.send(P.encode())
                PReply = controlSock.recv(4096).decode()
                replyParse(PReply)
                sys.stdout.write("SYST"+"\r\n")
                S = "SYST\r\n"
                controlSock.send(S.encode())
                SReply = controlSock.recv(4096).decode()
                replyParse(SReply)
                sys.stdout.write("TYPE I"+"\r\n")
                T = "TYPE I\r\n"
                controlSock.send(T.encode())
                TReply = controlSock.recv(4096).decode()
                replyParse(TReply)
                continue
        if inpU.startswith("GET"):
            getOK = True
            #checks that a valid CONNECT has happened before a get request
            if connected == False:
                print(line.rstrip("\r\n"))
                print("ERROR -- expecting CONNECT")
                continue
            #check to see that there's a space between command and pathname
            if not line[3] == " ":
                sys.stdout.write(line)
                print("ERROR -- request")
                continue
            get, pathName = line.split(" ")
            if connected == True and inpU[3] == " ":
                #checks that the pathname is made up of ASCII characters
                for letter in range(0, len(pathName)):
                    if ord(pathName[letter]) > 127:
                        print(line.rstrip("\r\n"))
                        print("ERROR -- pathname")
                        getOK = False
                        break
                if getOK == False:
                    continue
            if getOK:
                myIP = socket.gethostbyname(socket.gethostname())
                newIP = str(myIP.replace(".", ","))
                portNum2 = portNum%256
                portNum1 = (portNum - portNum2)//256
                portNum1 = str(portNum1)
                portNum2 = str(portNum2)
                print(line.rstrip("\r\n"))
                print("GET accepted for " + pathName.rstrip())
                PT = "PORT " + newIP +"," + portNum1+","+portNum2 + "\r\n"
                sys.stdout.write(PT)
                #listens for an incoming data connection from the server
                dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dataSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    dataSock.bind(("", portNum))
                except(socket.error):
                    print("GET failed, FTP-data port not allocated.")
                    continue
                dataSock.listen(1)
                controlSock.send(PT.encode())
                PTReply = controlSock.recv(4096).decode()
                replyParse(PTReply)
                portNum += 1
                R = "RETR " + pathName.rstrip()+"\r\n"
                sys.stdout.write(R)
                controlSock.send(R.encode())
                RReply = controlSock.recv(4096).decode()
                if RReply.startswith("150"):
                    #if the file exists, accepts data connection and downloads file from server
                    (data, addr) = dataSock.accept()
                    dataSock = data
                    replyParse(RReply)
                    getCount += 1
                    with open("retr_files/file"+ str(getCount), "wb") as file:
                        while 1:
                            recvFile = dataSock.read()
                            if not recvFile: break
                            file.write(recvFile)
                    RReply = controlSock.recv(4096).decode()
                    replyParse(RReply)
                    continue
                else:
                    replyParse(RReply)
                    continue
        if inpU.startswith("QUIT"):
            #checks that a valid connect request has been processed first
            if not connected:
                sys.stdout.write(line)
                print("ERROR -- expecting CONNECT")
                continue
            #checks for extraneous characters
            if not len(line) == 5:
                sys.stdout.write(line)
                print("ERROR -- request")
                continue
            else:
                #sends quit command to server, closes connection and closes client
                sys.stdout.write(line)
                print("QUIT accepted, terminating FTP client")
                sys.stdout.write("QUIT"+"\r\n")
                controlSock.send("QUIT\r\n".encode())
                QReply = controlSock.recv(4096).decode()
                replyParse(QReply)
                controlSock.close()
                break
        else:
            #prints request error if an unrecognized command is passed
            sys.stdout.write(line)
            print("ERROR -- request")
            continue

main()
        


