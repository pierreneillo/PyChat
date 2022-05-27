import socket
import select
import RSA

class ClientInfo:
    used_pseudos = []
    def __init__(self,id):
        self.id = id
        self.pseudo = None
        self.symkey = None
        self.pubkey = None
        self.messages = []
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

class Server:
    known_logs = ["root_user","lambda_user","i_m_a_teapot","hacker","banana"]
    def __init__(self, host = 'localhost', port = 10005, max_listen = 5):
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
    def run(self):
        print(f"server running on port {self.port}")
        while True:
            connexion_requests, wlist, xlist = select.select([self.socket],[],[],0.05)
            for connexion in connexion_requests:
                client_connexion, connexions_infos = connexion.accept()
                print(f"Connexion accepted: client n°{len(self.clients)}")
                connexion.setblocking(0)
                self.clients.append(ClientInfo(len(self.clients)))
                self.clients_connexions.append(client_connexion)
            try:
                client_requests, wlist, xlist = select.select(self.clients_connexions,[],[],0.05)
            except select.error:
                pass
            else:
                for client in client_requests:
                    received_message = client.recv(1024)
                    received_message=received_message.decode()
                    id_sender = self.clients_connexions.index(client)

                    #LOG REQUESTS TREATMENT
                    if received_message.startswith("Log: "):
                        log = received_message[5:]
                        if log in ClientInfo.used_pseudos:
                            status = 403
                        elif log in self.known_logs:
                            status = 200
                            self.clients[id_sender].log(log)
                        else:
                            status = 404
                        print(f"***LOG REQUEST***\nFrom client n°{id_sender}\nRequested log: {log}\nStatus: {status}\n")
                        client.send(str(status).encode("utf-8"))
                    #SIGNUP REQUESTS TREATMENT
                    elif received_message.startswith("Create: "):
                        log = received_message[8:]
                        if log in ClientInfo.used_pseudos:
                            status = 403
                        elif log in self.known_logs:
                            status = 404
                        else:
                            status = 200
                            self.clients[id_sender].log(log)
                            Server.known_logs.append(log)
                        print(f"***SIGNUP REQUEST***\nFrom client n°{id_sender}\nRequested log: {log}\nStatus: {status}\n")
                        client.send(str(status).encode("utf-8"))
                    #SECURE REQUESTS TREATMENT
                    elif received_message.startswith("Secure: "):
                        secure_method = received_message[8:]
                        if secure_method=="RSA + ext_vig_256":
                            client.send(f"{self.clePub[0]},{self.clePub[1]}".encode("utf-8"))
                        else:
                            client.send(b"Unknown securisation method")
                        print(f"***SECURE REQUEST***\nFrom client n°{id_sender}\nValid: {secure_method=='RSA + ext_vig_256'}\n")
                    elif received_message.startswith("SymKey: "):
                        encoded_key = received_message[8:]
                        encoded_key = list(map(int,encoded_key[1:-1].split(",")))
                        self.clients[id_sender].symkey = RSA.dechiffrement_RSA(encoded_key,self.clePriv)
                        print(f"***SYM KEY RECEIVED***\nFrom client n°{id_sender}\nValue: hidden\n")
                    else:
                        print(f"***MESSAGE RECEIVED[{id_sender}]***\nContent: {received_message}\n")
    def encode(self,id,message):
        return RSA.chiffrement_vigenere256(message,self.clients[i].symkey)

    def decode(self,id,message):
        return RSA.dechiffrement_vigenere256(message,self.clients[i].symkey)


server1 = Server()
server1.run()
