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
        data = TIME_ACT + EVENT + ': No server listening at'
        data += IP + "port " + PORT + '\r\n'
    elif EVENT == 'Send to' or EVENT == 'Received from':
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

    try:
        CONFIG = sys.argv[1]
        METHOD = sys.argv[2]
        if METHOD = 'REGISTER':
            EXPIRES = sys.argv[3]
        else:
        #METHOD = 'INVITE' or METHOD = 'BYE':
            USER = sys.argv[3]

    except IndexError:
        sys.exit("Usage: python3 uaclient.py config method option")

    #Abrimos el fichero XML
    fich = open(CONFIG, 'r')
    line = fich.readlines()
    fich.close()

    #CLIENT, USERNAME + PASSWORD:
    USERNAME = line[4].split(">")[1].split("<")[0]
    PASSWD = line[5].split(">")[1].split("<")[0]

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


    METHODS = ['REGISTER', 'INVITE', 'BYE']

    if not method in self.METHODS:
        print("Method have to be: REGISTER, INVITE OR BYE")
        sys.exit("Usage: python3 uaclient.py config method option")

    elif method == 'REGISTER':
        #Escribimos en fichero LOG:
        FICH_LOG(PATH_LOG, 'Starting...','','','')
        #Register sin Autenticación:
        LINE = method + 'sip:' + USERNAME + ':' + PORT
        LINE += 'SIP/2.0\r\n' + 'Expires: ' + EXPIRES + '\r\n'

    elif method == 'INVITE':
        #Añadimos las correspondientes cabeceras:
        LINE = method + 'sip:' + USER + 'SIP/2.0\r\n'
        #Header Field + Separator:
        LINE += 'Content-Type: application/sdp\r\n\r\n'
        #Message Body:
        LINE += 'v=0\r\n' + 'o=' + USERNAME + ' ' + IP
        LINE += 's=Prueba' + '\r\n' + 't=0' + '\r\n'
        LINE += 'm=audio' + PORT_AUDIO + 'RTP' + '\r\n'


    elif method == 'BYE':
        #Escribimos en fichero LOG:
        FICH_LOG(PATH_LOG, 'Finishing.','','','')

        LINE = method + 'sip:' + USER + 'SIP/2.0\r\n'

    try:
        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, PORT_PROXY))

        #Enviando:
        print("Sending: \r\n" + LINE) 
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Send to', IP_PROXY, PORT_PROXY, LINE)
    except socket.Error:
        sys.exit("ERROR: No server listening")

    try:
        #Recibimos datos:
        data = my_socket.recv(1024)
        print("Receiving: \r\n" + data.decode('utf-8')

    except socket.Error:
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Error', IP, PORT, '')
        sys.exit(FICH_LOG)

    #Respuesta recibida: 
    response = data.decode('utf-8').split("\r\n")
    LINE = ' '.join(response)

    #Escribimos en el fichero LOG el mensaje recibido:
    FICH_LOG(PATH_LOG,'Received from', IP_PROXY, PORT_PROXY, LINE)

    #Comportamiento según la respuesta:
    if response[0] == 'SIP/2.0 401 Unauthorized':
        #Enviamos Register con Autenticación:
        m = hashlib.md5()
        NONCE = response[1].split('=')[-1]
        m.update(b'NONCE')
        m.update(b'PASSWD')

        LINE += 'WWW Authenticate: Digest response= ' 
        LINE += m.hexdigest() + '\r\n'

        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Send to', IP_PROXY, PORT_PROXY, LINE)

    elif response[0] == 'SIP/2.0 100 Trying':
        #TRYING + RINGING + OK:
        LINE = method + 'sip:' + USER + ' SIP/2.0'

        #Envio RTP:
        #IP_AUDIO = ¡¡¡¡¡¡¡FALTA!!!!!!! 
        # aEjecutar es un string con lo que se ha de ejecutar en la shell
        aEjecutar = './mp32rtp -i ' +  'INCOMPLETO'
        aEjecutar += '-p' +  PORT_AUDIO
        aEjecutar +=  '< ' + PATH_AUDIO)

        print ("Let's run", aEjecutar)
        os.system(aEjecutar)

    elif response[0] == 'SIP/2.0 200 OK':
        print("Ending socket...")

        # Cerramos todo
        my_socket.close()
        print("Fin.")
