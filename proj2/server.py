# Import socket module
from socket import *
import sys # In order to terminate the program

# Create a TCP server socket
#(AF_INET is used for IPv4 protocols)
#(SOCK_STREAM is used for TCP)
serverSocket = socket(AF_INET, SOCK_STREAM)

# Assign a port number
serverPort = 6789

# Bind the socket to server address and server port
serverSocket.bind(("", serverPort))

# Listen to at most 1 connection at a time
serverSocket.listen(1)

# Server should be up and running and listening to the incoming connections
while True:
    print('The server is ready to receive')

    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()

    # If an exception occurs during the execution of try clause
    # the rest of the clause is skipped
    # If the exception type matches the word after except
    # the except clause is executed
    try:
        # Receives the request message from the client
        message = connectionSocket.recv(1024).decode()
        
        
        ## Examine POST message (attempt)
        # print("Incoming Request:", message)
        usrpwd = None
        if message.startswith("POST"):
            # print("POST message")
            # print(message.split())
            ## Retrieve last item in message, username and pwd
            usrpwd = message.split()[-1].split("&")
            usn = usrpwd[0].split("=")[-1]
            pwd = usrpwd[1].split("=")[-1]
            print("USN:", usn, "PWD:", pwd)
            if usn == "fish" and pwd == "morefish":
                print("yay")
            else:
                connectionSocket.send("HTTP/1.1 401 Unauthorized\r\n\r\n".encode())
                connectionSocket.send("<html><head></head><body><h1>401 Unauthorized</h1></body></html>\r\n".encode())
                connectionSocket.close()
        
        # Extract the path of the requested object from the message
        # The path is the second part of HTTP header, identified by [1]
        filename = message.split()[1]

        if filename == "/":
            filename = "/server_files/homepage.html"
        print(filename)

        # Modify to display image when requested
        content_type = None
        if filename.endswith('.png'):
            content_type = 'image/png'
            # print('test!')
        else:
            content_type = 'text/html'

        # For images, open file in binary mode; for HTML, text mode
        if content_type.startswith('image/png'):
            # to eliminate first slash
            # print(filename[1:])
            # open image file
            with open(filename[1:], 'rb') as f:
                outputdata = f.read()

            # Send the HTTP response header line to the connection socket on image
            connectionSocket.send(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode())

            # Send the binary image data
            connectionSocket.send(outputdata)
        else:
            # Check if the GET request ends with "green" or "red", respond with correct page
            if filename.endswith("green"):
                filename = "/server_files/green.html"
            if filename.endswith("red"):
                filename = "/server_files/red.html"

            # Return to homepage if request ends with "homepage"
            if filename.endswith("homepage"):
                filename = "/server_files/homepage.html"

            # Give login page if request ends with "login"
            if filename.endswith("login"):
                filename = "/server_files/login.html"

            # Because the extracted path of the HTTP request includes
            # a character '\', we read the path from the second character
            f = open(filename[1:])

            # Store the entire content of the requested file in a temporary buffer
            outputdata = f.read()

            # Send the HTTP response header line to the connection socket
            connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())

            # Send the content of the requested file to the connection socket
            for i in range(0, len(outputdata)):
                connectionSocket.send(outputdata[i].encode())
            connectionSocket.send("\r\n".encode())

        # Close the client connection socket
        connectionSocket.close()
            
    except IOError as error:
        # Send HTTP response message for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())

        # Close the client connection socket
        connectionSocket.close()

        print("An error has occured:", type(error).__name__)

serverSocket.close()
sys.exit() #Terminate the program after sending the corresponding data
