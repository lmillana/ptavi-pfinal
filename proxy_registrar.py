#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa Proxy Registrar
"""
import sys
from uaclient import FICH_LOG
import socketserver


class ProxyRegistrarHandler(socketserver.DatagramRequestHandler):
    """
    Proxy-Registrar server class
    """
    METHODS = ['REGISTER', 'INVITE', 'ACK', 'BYE']

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP_CLIENT = str(self.client_address[0])
        PORT_CLIENT = int(self.client_address[1])

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            text = self.rfile.read()
            LINE = line.decode('utf-8')
            
            method = text.decode('utf-8').split(' ')[0].upper()
            #Añadimos mensajes de recepcion en el fichero LOG:
            FICH_LOG(PATH_LOG, 'Received from', IP_CLIENT, PORT_CLIENT, LINE)

            if not method in self.METHODS:
                answer = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'

            elif method = 'REGISTER':
                
            elif method = 'INVITE':
            
            elif method = 'ACK':
            
            elif method = 'BYE':
            
            else:
                answer = 'SIP/2.0 Bad Request\r\n\r\n'

            self.wfile.write(bytes(answer, 'utf-8'))


if __name__ = "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 proxy_registrar.py config")

    try:
        CONFIG = sys.argv[1]
        
        if not os.path.exists(CONFIG):
            print("File doesnt exist!")
            sys.exit("Usage: python3 uaserver.py config")

    except IndexError:
        sys.exit("Usage: python3 proxy_registrar.py config")

    #Abrimos el fichero XML
    fich = open(CONFIG, 'r')
    line = fich.readlines()
    fich.close()

    #SERVER, NAME + IP + PORT:
    SERVER_NAME = line[4].split('>')[1].split('<')[0]
    SERVER_IP = line[5].split('>')[1].split('<')[0]
    SERVER_PORT = line[6].split('>')[1].split('<')[0]

    #DATABASE, PATH + PASSWORD:
    DATA_PATH = line[9].split('>')[1].split('<')[0]
    DATA_PASSW = line[10].split('>')[1].split('<')[0]

    #LOG:
    PATH_LOG = line[13].split('>')[1].split('<')[0]


    print("Server " + SERVER_NAME + "listening at port " + SERVER_PORT)
    #Escribimos en el fichero LOG:
    FICH_LOG(PATH_LOG, 'Starting...', '','','')

    serv = socketserver.UDPserver(IP,PORT),ProxyRegistrarHandler)

    try:
        serv.serve_forever()
    except:
        FICH_LOG(PATH_LOG, 'Error', IP_PROXY, PORT_PROXY, '')
        sys.exit("ERROR: No server listening")
