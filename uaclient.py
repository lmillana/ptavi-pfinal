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

def FICH_LOG(fichero, EVENT, IP, PORT, LINE):
    fich = open(fichero, 'a')
    TIME_ACT = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time)) 
    
    if EVENT == 'Error':
        data = TIME_ACT + EVENT + 'No server listening at'
        data += IP + "Port " + PORT + '\r\n'
    elif EVENT == 'Send to' or EVENT == 'Received':
        data = TIME_ACT + EVENT + IP + ':' + PORT + ':'
        data += LINE + '\r\n'
    else: #Starting or Finishing
        data = TIME_ACT + EVENT + '\r\n'
    
    fich.write(data)
    fich.close()


if __name__ == "__main__":
    # Cliente UDP simple SIP

    if len(sys.argv) != 4:
        print('SIP/2.0 400 Bad Request' + '\r\n')
        sys.exit("Usage: python3 uaclient.py config method option")

    # Dirección IP del servidor:
    try:
        CONFIG = sys.argv[1]
        METHOD = sys.argv[2]
        PORT = sys.argv[3]
    except IndexError:
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
        #Escribimos en fichero LOG:
        EVENT = 'Starting...'
        FICH_LOG(PATH_LOG, EVENT,'','','')
        #Register sin Autenticación:
        LINE = method + 'sip:' + USERNAME + ':' + PORT
        LINE += 'SIP/2.0\r\n' + 'Expires: ' + OPTION + '\r\n'

    elif method == 'INVITE':
        #Añadimos las correspondientes cabeceras:
        LINE = method + 'sip: ' + OPTION + 'SIP/2.0\r\n'
        #Header Field + Separator:
        LINE += 'Content-Type: application/sdp\r\n\r\n'
        #Message Body:
        LINE += 'v=0\r\n' + 'o= ' + USERNAME + ' ' + IP
        LINE += 's=Prueba' + '\r\n' + 't=0' + '\r\n'
        LINE += 'm=audio' + PORT_AUDIO + 'RTP' + '\r\n'

    elif method == 'BYE':
        LINE = method + 'sip:' + OPTION + 'SIP/2.0\r\n'

    try:
        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, PORT_PROXY))

        #Enviando:
        print("Enviando: \r\n" + LINE) 
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        #Escribimos en el fichero LOG: 
        FICH_LOG(PATH_LOG, 'Send to', IP_PROXY, PORT_PROXY, LINE)
    except socket.Error:
        sys.exit("ERROR: No server listening")

    try:
        #Recibimos datos:
        data = my_socket.recv(1024)
        data_dec = data.decode('utf-8')
        print("Recibimos: \r\n" + data_dec)
        #Escribimos en el fichero LOG el mensaje recibido:
        FICH_LOG(PATH_LOG,'Received', IP_PROXY, PORT_PROXY,data_dec)
    except socket.Error:
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Error', IP, PORT, '')
        sys.exit(FICH_LOG)


    print("Terminando socket...")

    # Cerramos todo
    my_socket.close()
    print("Fin.")
