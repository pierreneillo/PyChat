import socket
import select
import RSA
from random import *

class ClientInfo:
    used_pseudos = []
    def __init__(self,id,server):
        self.id = id
        self.pseudo = f"Client n°{id}"
        self.symkey = None
        self.pubkey = None
        self.messages = []
        self.server = server
    @property
    def logged(self):
        return self.pseudo is not None
    @property
    def secured(self):
        return self.symkey is not None
    def log(self,pseudo):
        self.pseudo = pseudo
        ClientInfo.used_pseudos.append(pseudo)
    def logout(self):
        ClientInfo.used_pseudos.pop(ClientInfo.used_pseudos.index(self.pseudo))
    @classmethod
    def getlogged(cls):
        pass
    def change_pseudo(self,id_sender,*args):
        assert self.id == id_sender
        self.pseudo = args[0]
        ClientInfo.used_pseudos.append(self.pseudo)
        self.server.clients_connexions[self.id].send(b"200")



class Server:
    known_logs = ["root_user","lambda_user","i_m_a_teapot","hacker","banana"]
    def __init__(self, port = 10005, host = 'localhost', max_listen = 5):
        self.host = host
        self.port = port
        self.clePub,self.clePriv = RSA.generation_cle_RSA()
        self.max_listen = max_listen
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)#Création du socket
        self.socket.setblocking(0)
        self.socket.bind((self.host,self.port))
        self.socket.listen(5)
        self.clients_connexions=[]
        self.clients = []
    def relay(self,id_sender,*param):
        '''The aim of this method is to relay a message from a client to another'''
        id_dest = param[0]
        content = param[1]
        self.clients_connexions[id_dest].send(f"\x00".encode("utf-8"))
    def random_answer(self,id_sender,*param):
        answers = ["Bien reçu", "Ok", "5/5", "Super!", "Ici la lune..."]
        self.clients_connexions[id_sender].send(choice(answers).encode("utf-8"))
    def end_connexion(self):
        pass
    def public_key(self,id_sender,*args):
        self.clients_connexions[id_sender].send(",".join(list(map(str,self.clePub))).encode("utf-8"))
    def decode_sym_key(self,id_sender,*args):
        encoded_key = list(map(int,args))
        self.clients[id_sender].symkey = RSA.dechiffrement_RSA(encoded_key,self.clePriv)
        self.clients_connexions[id_sender].send(b"200")
    def run(self):
        print(f"server running on port {self.port}")
        while True:
            print("tdb")
            connexion_requests, wlist, xlist = select.select([self.socket],[],[],0.05)
            print(f"start checking for connexions [{len(connexion_requests)}]")
            for connexion in connexion_requests:
                client_connexion, connexions_infos = connexion.accept()
                print(f"Connexion accepted: client n°{len(self.clients)}")
                connexion.setblocking(0)
                self.clients.append(ClientInfo(len(self.clients),self))
                self.clients_connexions.append(client_connexion)
            print("connexions checked")
            try:
                client_requests, wlist, xlist = select.select(self.clients_connexions,[],[],0.05)
            except select.error:
                pass
            else:
                for client in client_requests:
                    print("***MESSAGE***")
                    id_sender = self.clients_connexions.index(client)
                    procedures = [self.end_connexion,
                    ClientInfo.getlogged,
                    self.clients[id_sender].change_pseudo,
                    self.relay,
                    self.random_answer,
                    self.public_key,
                    self.decode_sym_key]
                    #The procedure list represents the different actions that can be asked for by the client
                    #the client must send \x00 character as first character of the message to end the connexion for instance
                    #The sent procedures are:
                    # 0. Relay
                    # 1. Answer
                    received_message = client.recv(1024)
                    print(received_message)
                    procedure = received_message[0]
                    received_message = received_message.decode("utf-8")
                    param = list(received_message[1:].strip().split("\xff"))
                    procedures[procedure](id_sender,*param)

    def encode(self,id,message):
        return RSA.chiffrement_vigenere256(message,self.clients[i].symkey)

    def decode(self,id,message):
        return RSA.dechiffrement_vigenere256(message,self.clients[i].symkey)


server1 = Server(10024)
server1.run()
