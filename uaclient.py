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

def FICH_LOG(fichero, EVENT, IP, PORT, Line):
    fich = open(fichero, 'a')
    TIME_ACT = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time)) 
    
    if EVENT == 'Error':
        datos = TIME_ACT + EVENT + 'No server listening at'
        datos += IP + "Port " + PORT + '\r\n'
    elif EVENT == 'Send to' or EVENT == 'Received':
        datos = TIME_ACT + EVENT + IP + ':' + PORT + ':'
        datos += Line + '\r\n'
    else: #Starting or Finishing
        datos = TIME_ACT + EVENT + '\r\n'
    
    fich.write(datos)
    fich.close()


if __name__ == "__main__":
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

    #USERNAME + PASSWORD:
    USERNAME = line[4].split(">")[1].split("<")[0]
    PASSWORD = line[5].split(">")[1].split("<")[0]

    #UASERVER, IP + PUERTO:
    IP = line[8].split(">")[1].split("<")[0]
    PORT = line[9].split(">")[1].split("<")[0]

    #RTP AUDIO:
    PORT_AUDIO = line[12].split(">")[1].split("<")[0]

    #PROXY, IP + PUERTO:
    IP_PROXY = line[15].split(">")[1].split("<")[0]
    PORT_PROXY = line[16].split(">")[1].split("<")[0]

    #LOG(localización del fichero de log):
    PATH_LOG = line[19].split(">")[1].split("<")[0]

    #AUDIO, PATH(localizacion del ficherod el audio):
    PATH_AUDIO = line[22].split(">")[1].split("<")[0]


    METHODS = ['INVITE', 'ACK', 'BYE']

    if not method in self.METHODS:
        print("Method have to be: REGISTER, INVITE OR BYE")
        sys.exit("Usage: python3 uaclient.py config method option")

    elif method == 'REGISTER':

    elif method == 'INVITE':

    elif method == 'BYE':
      

    try:
        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, PORT_PROXY))

        #Enviando:
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    except:
        sys.exit("ERROR: No server listening")

    try:
        #Recibimos datos:
        data = my_socket.recv(1024)
    except socket.Error:
        sys.exit('ERROR: No server listening')

    #Lo que recibo antes del asentimiento.
    print("Recibimos\r\n" + data.decode('utf-8'))

    #Metodo de asentimiento:
    message = data.decode('utf-8').split('\r\n\r\n')[0:-1]

    print("Terminando socket...")

    # Cerramos todo
    my_socket.close()
    print("Fin.")
