from socket import *
import sys  # In order to terminate the program
import select  # To handle user input and server requests

"""
NOTE: Needs to be ran on a Linux/Unix machine. Windows does not allow select to operate
##       on non-socket objects, so the stdin doesn't work. >:(
"""

# Create a TCP server socket
# (AF_INET is used for IPv4 protocols)
# (SOCK_STREAM is used for TCP)
serverSocket = socket(AF_INET, SOCK_STREAM)

# Assign a port number
serverPort = 6789

# Bind the socket to server address and server port
serverSocket.bind(("", serverPort))
# Listen to at most 1 connection at a time
serverSocket.listen(1)

# Login Statistics File
statfile = "logindata.txt"


# Handle Login Data
def readLoginData():
    try:
        with open(statfile, 'r') as f:
            lines = f.readlines()
            success = int(lines[0].strip())
            failed = int(lines[1].strip())
            return success, failed
    except IOError:
        return 0, 0


def writeLoginData(success, failed):
    with open(statfile, 'w') as f:
        f.write(f"{success}\n{failed}\n")


while True:
    # Server should be up and running and listening to the incoming connections
    print('The server is ready to receive')

    # Wait for either stdin input or socket connection
    rdySockets, _, _ = select.select([serverSocket, sys.stdin], [], [])

    for source in rdySockets:
        # Handle User Input
        if source == sys.stdin:
            cmd = sys.stdin.readline().strip()
            if cmd == "exit":
                print("Shutting down server...")
                serverSocket.close()
                sys.exit()
            elif cmd == "help":
                print(
                    """
*** SERVER COMMAND HELP ***\n
help - show this help message\n
exit - terminate server and stop all connections\n
*** ------------------- ***
                    """)
            else:
                print(f"{cmd}: Command Not Found")

        elif source == serverSocket:  # New client connection
            connectionSocket, addr = serverSocket.accept()
            try:
                # Receives the request message from the client
                message = connectionSocket.recv(1024).decode()

                # Handle POST request (login)
                usrpwd = None
                if message.startswith("POST"):
                    ## Retrieve last item in message, username and pwd
                    usrpwd = message.split()[-1].split("&")
                    usn = usrpwd[0].split("=")[-1]
                    pwd = usrpwd[1].split("=")[-1]
                    print("USN:", usn, "PWD:", pwd)
                    success, failed = readLoginData()
                    if usn == "fish" and pwd == "morefish":
                        success += 1
                        writeLoginData(success, failed)
                        connectionSocket.send(f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode())
                        connectionSocket.send("<html><head></head><body><h1>EE129 Project 2: Successful Login</h1>"
                                              f"<p>Successful Logins: {success}</p><p>Failed Logins: {failed}</p>"
                                              """
                                              <p>
                                              <form action="/return" method="GET">
                                                <input type="hidden" name="action" value="homepage">
                                                <button type="submit">Return to Homepage</button>
                                              </form></p>
                                              """
                                              "</body></html>\r\n".encode())
                        connectionSocket.close()
                    else:
                        writeLoginData(success, failed + 1)
                        connectionSocket.send("HTTP/1.1 401 Unauthorized\r\n\r\n".encode())
                        connectionSocket.send("<html><body><h1>401 Unauthorized</h1></body></html>".encode())
                    connectionSocket.close()
                    continue

                # Handle GET Requests
                # Extract the path of the requested object from the message
                # The path is the second part of HTTP header, identified by [1]
                filename = message.split()[1]
                if filename == "/":
                    filename = "/server_files/homepage.html"
                print(filename)

                # Display image when requested
                content_type = 'image/png' if filename.endswith('.png') else 'text/html'

                if content_type == 'image/png':
                    with open(filename[1:], 'rb') as f:
                        outputdata = f.read()
                    # Send the HTTP response header line to the connection socket on image
                    connectionSocket.send(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode())

                    # Send the binary image data
                    connectionSocket.send(outputdata)
                else:
                    # Check if the GET request ends with "green" or "red", respond with correct page
                    if filename.endswith("green"): filename = "/server_files/green.html"
                    if filename.endswith("red"): filename = "/server_files/red.html"
                    # Return to homepage if request ends with "homepage"
                    if filename.endswith("homepage"): filename = "/server_files/homepage.html"
                    # Give login page if request ends with "login"
                    if filename.endswith("login"): filename = "/server_files/login.html"

                    # Because the extracted path of the HTTP request includes
                    # a character '\', we read the path from the second character
                    with open(filename[1:]) as f:
                        # Store the entire content of the requested file in a temporary buffer
                        outputdata = f.read()

                    # Send the HTTP response header line to the connection socket
                    connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
                    for i in range(0, len(outputdata)):
                        connectionSocket.send(outputdata[i].encode())
                    connectionSocket.send("\r\n".encode())
                # Close the client connection socket
                connectionSocket.close()

            except IOError as error:
                connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
                connectionSocket.send("<html><body><h1>404 Not Found</h1></body></html>".encode())
                connectionSocket.close()
                print("An error has occurred:", type(error).__name__)
