#Devin Puckett
import sys
import shutil
import os.path
import socket


#a function to check for the correct CRLF order
def crlfcheck(inp):
    if not ord(inp[-1]) == 10 or \
            not ord(inp[-2]) == 13:
        return False
    else:
        return True
def main():
    inpCount = 0
    pNum = int(sys.argv[1])
    #creates server listening socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(("", pNum))
    serverSocket.listen(1)
    sock, addr = serverSocket.accept()
    serverSocket = sock
    serverSocket.send("220 COMP 431 FTP server ready.\r\n".encode())
    sys.stdout.write("220 COMP 431 FTP server ready.\r\n")
    passInput = False
    userInput = False
    newPort = False
    retrOk = False
    cd = str(os.getcwd()) + "/"
    retrCount = 0
    portNum = 0000
    portIP = 0000
    #continuous loop that listens for connecting sockets and inputs from clients
    while True:
        inp = serverSocket.recv(4096).decode()
        if inp == 0:
            continue
        inp3 = inp
        inp2 = inp.upper()
        strp = inp2.strip()
        if inp2.startswith("USER"):
            # checks for a space between USER command and username
            if not inp[4] == " ":
                sys.stdout.write(inp)
                serverSocket.send("500 Syntax error, command unrecognized.\r\n".encode())
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                continue
            userOk = bool
            if len(strp) < 5:
                # checks if the input contains a username
                userOk = False
                sys.stdout.write(inp)
                serverSocket.send("502 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("502 Syntax error in parameter.\r\n")
                continue
            if len(strp) > 4:
                for letter in range(4, len(strp)):
                    # checks each letter of username for appropriate characters
                    if ord(strp[letter]) > 127:
                        userOk = False
                        sys.stdout.write(inp)
                        serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        break
                    if letter == len(strp) - 1 and ord(strp[letter]) <= 127:
                        userOk = True
                        break
            # checks for correct order of CRLF
            if not crlfcheck(inp):
                userOk = False
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter\r\n")
            if userOk:
                sys.stdout.write(inp)
                userInput = True
                passInput = False
                serverSocket.send("331 Guest access OK, send password.\r\n".encode())
                sys.stdout.write("331 Guest access OK, send password.\r\n")
                continue
        if inp2.startswith("PASS"):
            #checks for space between command and parameter
            if not inp[4] == " ":
                sys.stdout.write(inp)
                serverSocket.send("500 Syntax error, command unrecognized.\r\n".encode())
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                continue
            passwordOk = bool
            #checks to see if there is a parameter
            if len(strp) < 5:
                passwordOk = False
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
            if len(strp) > 4:
                #checks for valid password characters
                for x in range(4, len(strp)):
                    if ord(strp[x]) > 127:
                        passwordOk = False
                        sys.stdout.write(inp)
                        serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        break
                    if x == len(strp) and ord(strp[x]) <= 127:
                        passwordOk = True
                        break

            if not crlfcheck(inp):
                    passwordOk = False
                    sys.stdout.write(inp)
                    serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    continue
            if not userInput:
                #checks to see if a USER command has been passed first
                sys.stdout.write(inp)
                serverSocket.send("503 Bad sequence of commands.\r\n".encode())
                sys.stdout.write("503 Bad sequence of commands.\r\n")
            if passwordOk:
                sys.stdout.write(inp)
                passInput = True
                serverSocket.send("230 Guest login OK.\r\n".encode())
                sys.stdout.write("230 Guest login OK.\r\n")
                continue
        elif inp2.startswith("RETR"):
            # checks if logged in
            if not inp[4] == " ":
                sys.stdout.write(inp)
                serverSocket.send("500 Syntax error, command unrecognized.\r\n".encode())
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                continue
            retrOk = True
            if len(strp) < 5:
                # checks for a path
                retrOk = False
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
            if len(strp) > 4:
                # checks parameter for acceptable characters
                for letter in range(4, len(strp)):
                    if ord(strp[letter]) > 127:
                        retrOk = False
                        sys.stdout.write(inp)
                        serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        break
                    if letter == len(strp) and ord(strp[letter]) <= 127:
                        retrOk = True
                        break
            if not crlfcheck(inp):
                retrOk = False
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
                #checks to see if a username has been input
            if not userInput and not passInput:
                sys.stdout.write(inp)
                serverSocket.send("530 Not logged in.\r\n".encode())
                sys.stdout.write("530 Not logged in.\r\n")
                continue
                #checks so see if the USER is logged in
            if not passInput and userInput:
                sys.stdout.write(inp)
                serverSocket.send("503 Bad sequence of commands.\r\n".encode())
                sys.stdout.write("503 Bad sequence of commands.\r\n")
                continue
            if retrOk:
                #checks for a new PORT command
                if not newPort:
                    sys.stdout.write(inp)
                    serverSocket.send("503 Bad sequence of commands.\r\n".encode())
                    sys.stdout.write("503 Bad sequence of commands.\r\n")
                    continue
                #checks path for a leading \ or /
                if "/" in inp3[5] or "\\" in inp3[5]:
                    inp3 = inp3.replace("/", "", 1)
                    inp3 = inp3.replace("\\", "", 1)
                fileString = inp3[5:]
                fileString = fileString.strip()
                #checks if the file exists
                if not os.path.exists(fileString):
                    sys.stdout.write(inp)
                    serverSocket.send("550 File not found or access denied.\r\n".encode())
                    sys.stdout.write("550 File not found or access denied.\r\n")
                    continue
                sys.stdout.write(inp)
                serverSocket.send("150 File status okay.\r\n".encode())
                sys.stdout.write("150 File status okay.\r\n")
                #creates and tries to connect an FTP Data socket
                fileSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try: fileSocket.connect((portIP, portNum))
                except(socket.error):
                    serverSocket.send("425 Can not open data connection.\r\n".encode())
                    sys.stdout.write("425 Can not open data connection.\r\n")
                    continue
                retrCount = str(retrCount)
                with open(fileString, "rb") as data:
                    while 1:
                        sFile = data.read(4096)
                        if not sFile: break
                        fileSocket.write(sFile)
                sys.stdout.write("250 File action completed.\r\n")
                serverSocket.send("250 File action completed.\r\n".encode())
                fileSocket.close()
                continue
        elif inp2.startswith("PORT"):
            # checks for space between command and port
            if not inp[4] == " ":
                sys.stdout.write(inp)
                serverSocket.send("500 Syntax error, command unrecognized.\r\n".encode())
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                continue
            portOk = True
            if len(strp) < 5:
                # checks for a parameter
                portOk = False
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
            else:
                for digit in range(4, -3):
                    if ord(strp[digit]) < 48 or ord(strp[digit]) > 57:
                        if strp[digit] == ".":
                            portOk = True
                            break
                        else:
                            portOk = False
                            sys.stdout.write(inp)
                            serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                            sys.stdout.write("501 Syntax error in parameter.\r\n")
                            break

            if not crlfcheck(inp):
                portOk = False
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
            if portOk:
                num = strp[4:len(strp)]
                num = num.split(",")
                if len(num) != 6:
                    sys.stdout.write(inp)
                    serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    continue
                #checks for a proper login
                if not userInput and not passInput:
                    sys.stdout.write(inp)
                    serverSocket.send("530 Not logged in.\r\n".encode())
                    sys.stdout.write("530 Not logged in.\r\n")
                    continue
                if not passInput and userInput:
                    sys.stdout.write(inp)
                    serverSocket.send("503 Bad sequence of commands.\r\n".encode())
                    sys.stdout.write("503 Bad sequence of commands.\r\n")
                    continue
                #calculates the Port Number and sets the port number for future RETR commands
                num5 = int(num[4])
                num6 = int(num[5])
                portNum = (num5 * 256) + num6
                portNumStr = str(portNum)
                sys.stdout.write(inp)
                newPort = True
                serverSocket.send(("200 Port command successful (" + num[0].strip() + "." + num[1] + "." + num[2] + "." + num[3] + "," + portNumStr + ").\r\n").encode())
                sys.stdout.write("200 Port command successful (" + num[0].strip() + "." + num[1] + "." + num[2] + "." + num[3] + "," + portNumStr + ").\r\n")
                portIP = num[0].strip() + "." + num[1] + "." + num[2] + "." + num[3]
                continue
        elif inp2.startswith("TYPE"):
            # checks for space between type command and type code
            if not inp[4] == " ":
                sys.stdout.write(inp)
                serverSocket.send("500 Syntax error, command unrecognized.\r\n".encode())
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                continue
            typeOk = bool
            if ord(inp[5]) != 65:
                if ord(inp[5]) != 73:
                    # checks for appropriate type codes
                    typeOk = False
                    sys.stdout.write(inp)
                    serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    continue
            if not crlfcheck(inp):
                typeOk = False
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
            if typeOk:
                #checks if logged in
                if not userInput and not passInput:
                    sys.stdout.write(inp)
                    serverSocket.send("530 Not logged in.\r\n".encode())
                    sys.stdout.write("530 Not logged in.\r\n")
                    continue
                if not passInput and userInput:
                    sys.stdout.write(inp)
                    serverSocket.send("503 Bad sequence of commands.\r\n".encode())
                    sys.stdout.write("503 Bad sequence of commands.\r\n")
                    continue
                sys.stdout.write(inp)
                t = "200 Type set to " + inp[5]+".\r\n"
                serverSocket.send(t.encode())
                sys.stdout.write(t)
                continue
        elif inp2.startswith("SYST"):
            if len(inp2) > 6:
                # checks for extra characters
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
            if not crlfcheck(inp):
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
            #login check
            if not userInput and not passInput:
                sys.stdout.write(inp)
                serverSocket.send("530 Not logged in.\r\n".encode())
                sys.stdout.write("530 Not logged in.\r\n")
                continue
            if not passInput and userInput:
                sys.stdout.write(inp)
                serverSocket.send("503 Bad sequence of commands.\r\n".encode())
                sys.stdout.write("503 Bad sequence of commands.\r\n")
                continue
            else:
                sys.stdout.write(inp)
                serverSocket.send("215 UNIX Type: L8.\r\n".encode())
                sys.stdout.write("215 UNIX Type: L8.\r\n")
                continue
        elif inp2.startswith("NOOP"):
            if len(inp2) > 6:
                # checks for extra characters
                sys.stdout.write(inp)
                serverSocket.send("500 Syntax error, command unrecognized.\r\n".encode())
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                continue
            if not crlfcheck(inp):
                # checks for correct CRLF
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
            if not userInput and not passInput:
                sys.stdout.write(inp)
                serverSocket.send("530 Not logged in.\r\n".encode())
                sys.stdout.write("530 Not logged in.\r\n")
                continue
            if not passInput and userInput:
                sys.stdout.write(inp)
                serverSocket.send("503 Bad sequence of commands.\r\n".encode())
                sys.stdout.write("503 Bad sequence of commands.\r\n")
                continue
            else:
                sys.stdout.write(inp)
                serverSocket.send("200 Command OK.\r\n".encode())
                sys.stdout.write("200 Command OK.\r\n")
                continue
        elif inp2.startswith("QUIT"):
            if len(inp2) > 6:
                # check for extra characters
                sys.stdout.write(inp)
                serverSocket.send("500 Syntax error, command unrecognized.\r\n".encode())
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                continue
            if not crlfcheck(inp):
                sys.stdout.write(inp)
                serverSocket.send("501 Syntax error in parameter.\r\n".encode())
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                continue
            else:
                #closes current connection with a client, and creates a new listening socket for the next client
                sys.stdout.write(inp)
                serverSocket.send("221 Goodbye.\r\n".encode())
                serverSocket.close()
                sys.stdout.write("221 Goodbye.\r\n")
                serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                serverSocket.bind(("", pNum))
                serverSocket.listen(1)
                sock, addr = serverSocket.accept()
                serverSocket = sock
                serverSocket.send("220 COMP 431 FTP server ready.\r\n".encode())
                sys.stdout.write("220 COMP 431 FTP server ready.\r\n")
                passInput = False
                userInput = False
                newPort = False
                retrOk = False
                cd = str(os.getcwd()) + "/"
                retrCount = 0
                portNum = 0000
                portIP = 0000
                continue
        else:
            # sys.stdout.writes an error message if the command is not an FTP command
            sys.stdout.write(inp)
            serverSocket.send("500 Syntax error, command unrecognized.\r\n".encode())
            sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
            continue

main()