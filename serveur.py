import socket
import select

class Server:
    def __init__(self, host = 'localhost', port = 10005, max_listen = 5):
        self.host = host
        self.port = port
        self.max_listen = max_listen
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)#Création du socket
        self.socket.setblocking(0)
        self.socket.bind((self.host,self.port))
        self.socket.listen(5)
        self.clients=[]
        self.clients_pseudos=[]
        self.messages=[]
    def run(self):
        print(f"server running on port {self.port}")
        while True:
            connexion_requests, wlist, xlist = select.select([self.socket],[],[],0.05)
            for connexion in connexion_requests:
                client_connexion, connexions_infos = connexion.accept()
                connexion.setblocking(0)
                self.clients.append(client_connexion)
            try:
                client_requests, wlist, xlist = select.select(self.clients,[],[],0.05)
            except select.error:
                pass
            else:
                for client in client_requests:
                    received_message = client.recv(1024)
                    received_message=received_message.decode()
                    self.messages.append((self.clients.index(client),received_message))
                    print(f"***Received message***\nFrom client n°{self.clients.index(client)}\nContent:\n{received_message}")
                    client.send(b"Message received: id = " +bytes(str(len(self.messages))))
server1 = Server()
server1.run()
print("server closed...")
