from premiers import pr
from random import *

MAX = 50

def PGCD(a,b):
    return b if a%b==0 else PGCD(b,a%b)

def premiers(a,b):
    return PGCD(a,b)==1

def algo_euclide_etendu(r,u,v,r1,u1,v1):
    if r1==0:
        return r,u,v
    return algo_euclide_etendu(r1,u1,v1,r-(r//r1)*r1,u-(r//r1)*u1,u-(r//r1)*u1)

def coefficients_de_bezout(a,b):
    return algo_euclide_etendu(a,1,0,b,0,1)[1:]


def RSA(p,q):
    n = p*q
    phi = (p-1)*(q-1)
    for i in range(2,phi):
        if premiers(i,phi):
            e=i
            break
    d = coefficients_de_bezout(e,phi)[0]
    while d<=0:
        d+=phi
    return [(e,n),(d,n)]

def generation_cle_RSA():
    p,q = int(choice(pr[:MAX])),int(choice(pr[:100]))
    return RSA(p,q)


def chiffrement_RSA(message,clePub):
    e,n = clePub
    messageCode = []
    for char in message:
        messageCode.append((ord(char)**e)%n)
    return messageCode

def dechiffrement_RSA(message,clePriv):
    d,n = clePriv
    messageDecode = ""
    for num in message:
        messageDecode += chr((num**d)%n)
    return messageDecode

def chiffrement_vigenere256(message,cle):
    s = ""
    for i in range(len(message)):
        c = message[i]
        k = cle[i%len(cle)]
        s += chr( (ord(c) +  ord(k))%255)
    return s

def dechiffrement_vigenere256(message,cle):
    s = ""
    for i in range(len(message)):
        c = message[i]
        k = cle[i%len(cle)]
        s += chr( (ord(c) -  ord(k))%255)
    return s

