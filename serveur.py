import socket
import select
import RSA

class Server:
    known_logs = ["root_user"]
    def __init__(self, host = 'localhost', port = 10005, max_listen = 5):
        self.host = host
        self.port = port
        self.clePub,self.clePriv = RSA.generation_cle_RSA()
        print(self.clePub,self.clePriv)
        self.max_listen = max_listen
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)#Création du socket
        self.socket.setblocking(0)
        self.socket.bind((self.host,self.port))
        self.socket.listen(5)
        self.clients=[]
        self.clients_pseudos=[]
        self.keys = []
        self.messages = []
    def run(self):
        print(f"server running on port {self.port}")
        while True:
            connexion_requests, wlist, xlist = select.select([self.socket],[],[],0.05)
            for connexion in connexion_requests:
                client_connexion, connexions_infos = connexion.accept()
                print(f"Connexion accepted: client n°{len(self.clients)}")
                connexion.setblocking(0)
                self.clients.append(client_connexion)
                self.clients_pseudos.append(None)
                self.keys.append(None)
            try:
                client_requests, wlist, xlist = select.select(self.clients,[],[],0.05)
            except select.error:
                pass
            else:
                for client in client_requests:
                    received_message = client.recv(1024)
                    received_message=received_message.decode()
                    id_sender = self.clients.index(client)
                    self.messages.append((id_sender,received_message))
                    #LOG REQUESTS TREATMENT
                    if received_message.startswith("Log: "):
                        log = received_message[5:]
                        if log in self.clients_pseudos:
                            status = 403
                        elif log in self.known_logs:
                            status = 200
                            self.clients_pseudos[id_sender] = log
                        else:
                            status = 404
                        print(f"***LOG REQUEST***\nFrom client n°{id_sender}\nRequested log: {log}\nStatus: {status}\n")
                        client.send(str(status).encode("utf-8"))
                    #SIGNUP REQUESTS TREATMENT
                    elif received_message.startswith("Create: "):
                        log = received_message[8:]
                        if log in self.clients_pseudos:
                            status = 403
                        elif log in self.known_logs:
                            status = 404
                            self.clients_pseudos[id_sender] = log
                        else:
                            status = 200
                            self.clients_pseudos[id_sender] = log
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
                    elif received_message.startswith("SymKey: "):
                        encoded_key = received_message[8:]
                        self.keys[id_sender] = RSA.dechiffrement_RSA(encoded_key,self.clePriv)
                        print(self.keys[id_sender])


server1 = Server()
server1.run()
print("server closed...")
