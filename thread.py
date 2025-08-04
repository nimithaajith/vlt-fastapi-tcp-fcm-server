#server listener thread
from threading import Thread
from client_thread import ClientThread
import socket
class ServerThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Server thread starts.......")
        try:
            
            PORT = 8080
            SERVER='0.0.0.0'            
            ADDR = (SERVER, PORT)

            # creating socket
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.bind(ADDR)

            print("Server is Starts listening...")
            serversocket.listen()           
            c=0
            while True:
                c=c+1            
                conn, addr = serversocket.accept()                
                ClientThread(conn,addr).start() 
                print("New device thread started",c)               
        except Exception as e:
            print("Exception during server thread....,",e)