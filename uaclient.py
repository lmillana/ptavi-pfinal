#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa User Agent Client"""

import sys
import socket
import os
import time
import hashlib
from xml.sax.handler import ContentHandler


def FICH_LOG(fichero, EVENT, IP, PORT, LINE):
    fich = open(fichero, 'a')
    TIME_ACT = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()))

    if EVENT == 'Error':
        data = TIME_ACT + ' ' + EVENT + ': No server listening at '
        data += str(IP) + ' port ' + str(PORT) + '\r\n'
    elif EVENT == 'Send to' or EVENT == 'Received from':
        data = TIME_ACT + ' ' + EVENT + ' ' + str(IP) + ':' + str(PORT) + ':'
        data += ' ' + LINE + '\r\n'
    else:
        #Starting or Finishing
        data = TIME_ACT + ' ' + EVENT + '\r\n'

    fich.write(data)
    fich.close()


class XMLHandler(ContentHandler):
    """Cliente UDP simple SIP."""

    def __init__(self):
        #Diccionario delos datos de las etiquetas:
        self.tag_dic = {}
        #Lista donde guardar los diccionarios:
        self.list_dic = []


if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("Usage: python3 uaclient.py config method option")

    try:
        CONFIG = sys.argv[1]

        if not os.path.exists(CONFIG):
            print("File doesnt exist!")
            sys.exit("Usage: python3 uaserver.py config")

        METHOD = sys.argv[2].upper()
        if METHOD == 'REGISTER':
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

    if not METHOD in METHODS:
        print("-----ATENTION! Method have to be: REGISTER, INVITE OR BYE")
        LINE = ''
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Error', USERNAME, PORT, '')

    elif METHOD == 'REGISTER':
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Starting...', '', '',  '')
        #Register sin Autenticación:
        LINE = METHOD + ' sip:' + USERNAME + ':' + PORT
        LINE += ' SIP/2.0\r\n' + 'Expires: ' + EXPIRES + '\r\n'

    elif METHOD == 'INVITE':
        #Añadimos las correspondientes cabeceras:
        LINE = METHOD + ' sip:' + USER + ' SIP/2.0\r\n'
        #Header Field + Separator:
        LINE += 'Content-Type: application/sdp\r\n\r\n'
        #Message Body:
        LINE += 'v=0\r\n' + 'o=' + USERNAME + ' ' + IP + '\r\n'
        LINE += 's=prueba' + '\r\n' + 't=0' + '\r\n'
        LINE += 'm=audio ' + PORT_AUDIO + ' RTP' + '\r\n'

    elif METHOD == 'BYE':
        LINE = METHOD + ' sip:' + USER + ' SIP/2.0\r\n\r\n'

    try:
        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, int(PORT_PROXY)))

        #Enviando:
        print("-----SENDING: \r\n" + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Send to', IP_PROXY, PORT_PROXY, LINE)

    except socket.error:
        sys.exit('ERROR: No server listening at ' + IP_PROXY +
                 'Port: ' + PORT_PROXY)
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Error', IP, PORT, '')
        sys.exit(FICH_LOG)

    try:
        #Recibimos datos:
        data = my_socket.recv(int(PORT_PROXY))
        LINE = data.decode('utf-8')

        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Received from', IP_PROXY, PORT_PROXY, LINE)

        print("-----RECEIVED: \r\n" + LINE)
    except socket.error:
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Error', IP, PORT, '')
        sys.exit(FICH_LOG)

    #Respuesta recibida del PROXY:
    response = data.decode('utf-8').split()
    #Escribimos en el fichero LOG el mensaje recibido:
    FICH_LOG(PATH_LOG, 'Received from', IP_PROXY, PORT_PROXY, LINE)

    #Comportamiento según la respuesta:
    if response[1] == '401':
        #Enviamos Register con Autenticación:
        NONCE = response[-1].split('=')[1]
        m = hashlib.md5()
        m.update(bytes(NONCE, 'utf-8'))
        m.update(bytes(PASSWD, 'utf-8'))
        m.digest
        new_response = m.hexdigest()

        LINE_REGISTER = METHOD + ' sip:' + USERNAME + ':' + PORT
        LINE_REGISTER += ' SIP/2.0\r\n' + 'Expires: ' + EXPIRES + '\r\n'

        LINE = LINE_REGISTER + 'WWW-Authenticate: Digest response='
        LINE += new_response + '\r\n\r\n'

        #Enviamos la Autenticacion:
        print('---- SENDING:\r\n' + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n\r\n')
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Send to', IP_PROXY, PORT_PROXY, LINE)

        #Recibimos el 200 OK:
        data = my_socket.recv(int(PORT_PROXY))
        LINE = data.decode('utf-8')
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Received from', IP_PROXY, PORT_PROXY, LINE)

        print("-----RECEIVED: \r\n" + LINE)

    elif response[1] == '100' and response[4] == '180':
        #Escribimos en el fichero LOG:
        LINE = 'Trying, Ringing y OK'
        FICH_LOG(PATH_LOG, 'Received from', IP_PROXY, PORT_PROXY, LINE)
        #Respuesta a INVITE: TRYING + RINGING + OK:
        LINE = 'ACK sip:' + USER + ' SIP/2.0'

        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n\r\n')
        FICH_LOG(PATH_LOG, 'Send to', IP_PROXY, PORT_PROXY, LINE)

        print('-----SENDING:\r\n' + LINE)

        #Envio RTP:
        # aEjecutar es un string con lo que se ha de ejecutar en la shell
        aEjecutar = './mp32rtp -i ' + IP
        aEjecutar += ' -p ' + str(8765)
        aEjecutar += ' < ' + PATH_AUDIO
        os.system(aEjecutar)

        print ("LET'S RUN! ", aEjecutar)
        #Añadimos al fichero LOG:
        FICH_LOG(PATH_LOG, 'Finished audio transfer', '', '', '')
        print('Finished transfer!')

        data = my_socket.recv(int(PORT_PROXY))

    elif response[1] == '200':
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Finishing.', '', '', '')

        # Cerramos todo
        my_socket.close()
        print('The End')
