#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa User Agent Client
"""

import sys
import socket
import os
import time
import hashlib

# Cliente UDP simple SIP

if len(sys.argv) != 4:
    sys.exit("Usage: python3 uaclient.py config method option")

# Dirección IP del servidor:
try:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    PORT = sys.argv[3]
except Exception:
    sys.exit("Usage: python3 uaclient.py config method option")

#Abrimos el fichero XML
fich = open(CONFIG, 'r')
line = fich.readlines()
fich.close()


# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IP, PORT))

print("Enviando: " + LINE)
my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')

try:
    data = my_socket.recv(1024)
except ConnectionRefusedError:
    sys.exit('Connection refuses')

#Lo que recibo antes del asentimiento.
print(data.decode('utf-8'))

#Metodo de asentimiento:
message = data.decode('utf-8').split('\r\n\r\n')[0:-1]

print("Terminando socket...")

# Cerramos todo
my_socket.close()
print("Fin.")
