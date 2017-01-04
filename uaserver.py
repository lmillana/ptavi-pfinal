#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa User Agent Server.
"""
import sys
import socketserver
import os
from uaclient import FICH_LOG

if len(sys.argv) != 2:
    sys.exit("Usage: python3 uaserver.py config")

try:
    CONFIG = sys.argv[1]

    if not os.path.exists(CONFIG):
        print("File doesnt exist!")
        sys.exit("Usage: python3 uaserver.py config")

except IndexError:
    sys.exit("Usage: python3 uaserver.py config")


class ProxyHandler(socketserver.DatagramRequestHandler):
    """
    Proxy server class.
    """
    METHODS = ['INVITE', 'ACK', 'BYE']

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            text = self.rfile.read()
            line = self.rfile.read()

            method = text.decode('utf-8').split(' ')[0]
            print("Hemos recibido tu peticion:", method, '\r\n\r\n')

            if not method in self.METHODS:
                self.wfile.write(b'SIP/2.0 405 Method Not Allowed\r\n\r\n')

            elif method == 'INVITE':
                to_send = b"SIP/2.0 100 Trying\r\n\r\n"
                to_send += b"SIP/2.0 180 Ring\r\n\r\n"
                to_send += b"SIP/2.0 200 OK\r\n\r\n"
                self.wfile.write(to_send)

            elif method == 'ACK':
            # aEjecutar es un string con lo que se ha de ejecutar en la shell
                aEjecutar = ('./mp32rtp -i 127.0.0.1 -p 23032 < ' + FICH)
                print ("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)

            elif method == 'BYE':
                self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')

            else:
                self.wfile.write(b'SIP/2.0 400 Bad Request\r\n\r\n')

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

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


if __name__ == "__main__":
    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP_PROXY, PORT_PROXY))

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((IP, PORT), ProxyHandler)
    print("Listening...")
    
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
