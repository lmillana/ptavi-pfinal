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
    RTP = {'IP': '',
           'PORT': 0}
    METHODS = ['INVITE', 'ACK', 'BYE']

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP_CLIENT = str(self.client_address[0])
        PORT_CLIENT = int(self.client_address[1])
        
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            text = self.rfile.read()
            LINE = line.decode('utf-8')

            method = text.decode('utf-8').split(' ')[0].upper()
            print("Hemos recibido tu peticion:\r\n\", LINE)
            
            #Escribimos los mensajes de recepción en el fichero LOG:
            FICH_LOG(PATH_LOG, 'Received', IP_PROXY, PORT_PROXY,

            if not method in self.METHODS:
                answer = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'

            elif method == 'INVITE':
                asnwer = 'SIP/2.0 100 Trying\r\n\r\n'
                answer += 'SIP/2.0 180 Ring\r\n\r\n'
                answer += 'SIP/2.0 200 OK\r\n\r\n'
                #Añadimos las cabeceras: Header + Separator:
                answer += 'Content-Type: application/sdp\r\n\r\n'
                #Message Body:
                answer += 'v=0\r\n' + 'o=' + USERNAME + IP + '\r\n'
                answer += 's=Prueba' + '\r\n' + 't=0' + '\r\n'
                answer += 'm=audio' + PORT_AUDIO + 'RTP' + '\r\n'
                print("Codigo de respuesta a INVITE: \r\n", answer)

            elif method == 'ACK':
            # aEjecutar es un string con lo que se ha de ejecutar en la shell
                aEjecutar = './mp32rtp -i ' +  self.RTP['IP']
                aEjecutar += '-p' +  self.RTP['PORT']
                aEjecutar +=  '< ' + PATH_AUDIO)
                print ("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)

            elif method == 'BYE':
                answer = 'SIP/2.0 200 OK\r\n\r\n'
                print("Codigo de respuesta a BYE: \r\n", answer)

            else:
                answer = 'SIP/2.0 400 Bad Request\r\n\r\n')

            #Enviamos el mensaje de respuesta:
            self.wfile.write(bytes(answer, 'utf-8'))
            FICH_LOG(PATH_LOG, 'Sent to', IP_CLIENT, PORT_CLIENT, '')

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
    except:
        FICH_LOG(PATH_LOG, 'Error', IP_PROXY, PORT_PROXY, '')
        sys.exit("ERROR: No server listening")
