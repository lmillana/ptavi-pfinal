#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa User Agent Server."""

import sys
import socket
import socketserver
import os
from uaclient import FICH_LOG
from xml.sax.handler import ContentHandler


class XMLHandler(ContentHandler):

    def __init__(self):
        #Diccionario delos datos de las etiquetas:
        self.tag_dic = {}
        #Lista donde guardar los diccionarios:
        self.list_dic = []


class ProxyHandler(socketserver.DatagramRequestHandler):
    """Proxy server class."""

    RTP_LIST = []

    METHODS = ['INVITE', 'ACK', 'BYE']

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP_CLIENT = str(self.client_address[0])
        PORT_CLIENT = int(self.client_address[1])

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            text = self.rfile.read()
            LINE = text.decode('utf-8')

            #Para salir del bucle (si no hay mas lineas):
            if not LINE:
                break

            method = text.decode('utf-8').split(' ')[0]
            print('-----RECEIVED:\r\n' + LINE)

            if not method in self.METHODS:
                answer = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                #Enviamos el mensaje de respuesta:
                self.wfile.write(bytes(answer, 'utf-8'))
                #Añadimos al fichero LOG:
                FICH_LOG(PATH_LOG, 'Error', IP_CLIENT, PORT_CLIENT, '')

            elif method == 'INVITE':
                #Escribimos en el fichero LOG:
                FICH_LOG(PATH_LOG, 'Received from', IP_PROXY, PORT_PROXY, LINE)

                answer = 'SIP/2.0 100 Trying\r\n\r\n'
                answer += 'SIP/2.0 180 Ringing\r\n\r\n'
                answer += 'SIP/2.0 200 OK\r\n\r\n'
                #Añadimos las cabeceras: Header + Separator:
                answer += 'Content-Type: application/sdp\r\n\r\n'
                #Message Body:
                answer += 'v=0\r\n' + 'o=' + USERNAME + ' ' + IP + '\r\n'
                answer += 's=Prueba' + '\r\n' + 't=0' + '\r\n'
                answer += 'm=audio ' + PORT_AUDIO + ' RTP' + '\r\n\r\n'

                #Enviamos el mensaje de respuesta:
                self.wfile.write(bytes(answer, 'utf-8'))

                #Añadimos al diccionario RTP:
                self.RTP_LIST.append(USERNAME)
                self.RTP_LIST.append(IP)
                self.RTP_LIST.append(PORT_AUDIO)

                #Añadimos al fichero LOG:
                FICH_LOG(PATH_LOG, 'Send to', IP_PROXY, PORT_PROXY, answer)

                print('-----SENDING:\r\n' + answer)

            elif method == 'ACK':
                #Escribimos en el fichero LOG:
                FICH_LOG(PATH_LOG, 'Received from', IP_PROXY, PORT_PROXY, LINE)

                #Envio RTP:
                aEjecutar = './mp32rtp -i ' + self.RTP_LIST[1]
                aEjecutar += ' -p ' + self.RTP_LIST[2]
                aEjecutar += ' < ' + PATH_AUDIO
                print ("LET'S RUN! ", aEjecutar)
                os.system(aEjecutar)

                print('Finished transfer!')
                #Escribimos en el fichero LOG:
                FICH_LOG(PATH_LOG, 'Finished audio transfer', '', '', '')

            elif method == 'BYE':
                #Añadimos al fichero LOG:
                FICH_LOG(PATH_LOG, 'Received from', IP_PROXY, PORT_PROXY, LINE)

                answer = 'SIP/2.0 200 OK\r\n\r\n'
                #Enviamos el mensaje de respuesta:
                self.wfile.write(bytes(answer, 'utf-8'))

                #Añadimos al fichero LOG:
                FICH_LOG(PATH_LOG, 'Send to', IP_PROXY, PORT_PROXY, answer)

                print('-----SENDING:\r\n' + answer)

            else:
                FICH_LOG(PATH_LOG, 'Received from',
                         RECEPTOR_IP, RECEPTOR_PORT, LINE)

                answer = 'SIP/2.0 400 Bad Request\r\n\r\n'
                #Enviamos el mensaje de respuesta:
                self.wfile.write(bytes(answer, 'utf-8'))
                #Añadimos al fichero LOG:
                response = answer.split('\r\n')
                print(response)
                FICH_LOG(PATH_LOG, 'Error', IP_CLIENT, PORT_CLIENT, '')

                print('-----SENDING:\r\n' + answer)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit("Usage: python3 uaserver.py config")

    try:
        CONFIG = sys.argv[1]

        if not os.path.exists(CONFIG):
            print("File doesn't exist!")
            sys.exit("Usage: python3 uaserver.py config")

    except IndexError:
        sys.exit("Usage: python3 uaserver.py config")

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

    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP_PROXY, int(PORT_PROXY)))

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((IP, int(PORT)), ProxyHandler)
    print('Listening...')

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        FICH_LOG(PATH_LOG, 'Finising...', IP_PROXY, PORT_PROXY, '')
        sys.exit('\r\nEnded server')
