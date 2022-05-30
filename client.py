import socket
import RSA
from random import *

class Client:
    def __init__(self,pseudo,port=10024,host="127.0.0.1"):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.pseudo = pseudo
        self.clePub,self.clePriv = RSA.generation_cle_RSA()
        print(f"Attempting connexion on port {self.port}...")
        self.socket.connect((self.host,self.port))
        print("Connexion sucessful")
        self.log()
        self.secure()
        self.basic_comm()

    def log(self):
        print("Logging...")
        self.socket.send(f"\x02{self.pseudo}".encode("utf-8"))
        status = self.socket.recv(131072)
        status = int(status.decode())
        if status==200:
            print("Login sucessful")
        elif status==403:
            print("Access forbidden")
        elif status==404:
            print(f"No such existing account '{self.pseudo}'")
        else:
            print(f"Error {status}")

    def logout(self):
        print("Logging out...")
        self.socket.send(f"Logout: {self.pseudo}".encode("utf-8"))
        status = self.socket.recv(131072)
        status = int(status.decode())
        if status==200:
            print("Log out sucessful")
            self.socket.close()
            print("Connexion closed")
        elif status==500:
            print("An error occured, please try later")

    def signup(self):
        print("Creating your account...")
        self.socket.send(f"Create: {self.pseudo}".encode("utf-8"))
        status = self.socket.recv(131072)
        status = int(status.decode())
        if status==200:
            print("Sign up sucessful")
        elif status==403:
            print("Forbidden pseudo")
        elif status==404:
            print("An account already exists with this pseudo")
        else:
            print(f"Error {status}")

    def secure(self):
        print("Requesting a secured communication channel...")
        self.socket.send(b"\x05")
        #Here, the clients requests a secured communication, with a symetrical key (vigénère algorithm extended to ascii table) exchanged with RSA protocol first. This way of functionning does NOT prevent MITM attack
        #For now, RSA + ext_vig_256 is the only proposed connexion
        #Steps:
        #  1.The server sends its public key
        #  2.The client sends the symetric key, encoded with the server's public key
        #  3.The server is able to decode the symetric key with its private key, and each side has the symetric key, communication is ready
        self.server_public_key = tuple(map(lambda x: int(x.strip()),self.socket.recv(131072).split(b",")))
        print("Server's public key received...")
        self.symetric_key = "".join([chr(randint(0,255)) for _ in range(6)])
        cle_chiffree = RSA.chiffrement_RSA(self.symetric_key,self.server_public_key)
        cle_chiffree = "\xff".join(list(map(str,cle_chiffree)))
        self.socket.send(f"\x06{cle_chiffree}".encode("utf-8"))
        answer = self.socket.recv(131072)
        if answer == b"200":
            print("Channel secured")
        else:
            print("An error occured while securizing the channel, please try later")

    def getloggedlist(self):
        print("Asking for logged users list...")
        self.socket.send("\x01".encode("utf-8"))
        answer = self.socket.recv(131072)
        if answer == b"403":
            print("User has not access to this information")
        else:
            print(self.decode(answer.decode("utf-8"),self.symetric_key))

    def basic_comm(self):
        print("Type your messages! to end the conversation, simply type 'end'")
        ended=False
        while not ended:
            message = str(input("> "))
            if message!="end":
                encoded_message = RSA.chiffrement_vigenere256(message,self.symetric_key)
                self.socket.send(b"\x04"+encoded_message.encode("utf-8"))
                answer = self.socket.recv(131072).decode("utf-8")
                answer = RSA.dechiffrement_vigenere256(answer,self.symetric_key)
                print(answer)
            else:
                confirm = str(input("Do you really want to end the conversation? [y/n]"))
                if confirm == "y":
                    ended = True
    def encode(self,message,key):
        return RSA.chiffrement_vigenere256(message,key)

    def decode(self,message,key):
        return RSA.dechiffrement_vigenere256(message,key)

