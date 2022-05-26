import socket

class Client:
    def __init__(self,pseudo,host="127.0.0.1",port=10005):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.pseudo = pseudo
        print(f"Attempting connexion on port {self.port}...")
        self.socket.connect((self.host,self.port))
        print("Connexion sucessful")
    def log(self):
        print("Logging...")
        self.socket.send(f"Log: {self.pseudo}".encode("utf-8"))
        status = self.socket.recv(1024)
        status = int(status.decode())
        if status==200:
            print("Login sucessful")
        elif status==403:
            print("Access forbidden")
        elif status==404:
            print(f"No such existing account '{self.pseudo}'")
        else:
            print(f"Error {status}")
    def signup(self):
        print("Crating your account...")
        self.socket.send(f"Create: {self.pseudo}".encode("utf-8"))
        status = self.socket.recv(1024)
        status = int(status.decode())
        if status==200:
            print("Sign up sucessful")
        elif status==403:
            print("Forbidden pseudo")
        elif status==404:
            print("An account already exists with this pseudo")
        else:
            print(f"Error {status}")
