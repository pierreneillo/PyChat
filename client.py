import socket
connexion_serveur = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("Attempting connexion on port 10005")
connexion_serveur.connect(('127.0.0.1',10005))
print("Sucessful")
connexion_serveur.send(b"Hello")
print(connexion_serveur.recv(1024))