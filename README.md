AIS-140 Backend Server for VLT Devices
****************************************
This project implements the AIS-140 standard mandated by the Indian Government and defined by ARAI, enabling secure, real-time communication with vehicle tracking devices (VLTs) over TCP for intelligent transport system compliance.
# FastAPI + PostgreSQL + TCP Socket Server + FCM Notifications
This is a production-ready live project built using:
- FastAPI for API
- Threaded TCP socket server for device connections
- PostgreSQL as backend DB
- Firebase Cloud Messaging (FCM) for mobile notifications
- Docker & Docker Compose for deployment

## Features
- Receive device data via TCP socket
- Save data to PostgreSQL
- Send FCM notifications
- Dockerized for production

🚀 Deployment
1. Clone the Repository

git clone https://github.com/nimithaajith/vlt-fastapi-tcp-fcm-server.git
cd vlt-fastapi-tcp-fcm-server

2. Set Environment Variables
modify .env file

3. Run with Docker Compose

docker-compose up -d --build

[docker-compose down       #  Stop and remove old containers    

docker exec -it <containername> bash  # Access a container 
]

The FastAPI app will be available at http://localhost:8000.
Server will be listening at port 8080

## CLIENT PROGRAM SAMPLE FOR INITIAL TESTING TCP SOCKET COMMUNICATION ##
************************************************************************
import socket
import time

SERVER = "127.0.0.1"  # or the IP where your server is hosted
PORT = 8080           #  TcpThread port
#   AIS 140 renewed protocol 
# login packet sample for device imei= 9999999999
message = "$LGN,KL09A12,9999999999,FV1.0,AIS140S"

# Create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
client_socket.connect((SERVER, PORT))

# Send message
client_socket.sendall(message.encode("utf-8"))
time.sleep(5)
# position velocity time packet sample for device imei= 9999999999
message = "$PVT,SATWAY,FV1.0,NR,1,L,9999999999,KL09A12,1,14122022,172946,31.589618,N,75.875231,E,0,117.58,39,286.7,0.42,0.43,BHARAT,0,1,12.2,4.1,0,C,12,404,53,16C7,E4C2,2138,700000,29,2137,700000,21,2136,700000,21,968A,70000,19,0000,0000,00,0,492894,00AC*"
client_socket.sendall(message.encode("utf-8"))
time.sleep(5)
# position velocity time packet sample for device imei= 9999999999 with iginition ON
message = "$PVT,SATWAY,FV1.0,IN,1,L,9999999999,KL09A12,1,14122022,172946,31.589618,N,75.875231,E,0,117.58,39,286.7,0.42,0.43,BHARAT,0,1,12.2,4.1,0,C,12,404,53,16C7,E4C2,2138,700000,29,2137,700000,21,2136,700000,21,968A,70000,19,0000,0000,00,0,492894,00AC*"
client_socket.sendall(message.encode("utf-8"))
print("Message sent to TCP server.")
time.sleep(5)
n=input("Enter exit to quit :")
if n=='quit':
    client_socket.close()





