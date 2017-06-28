#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa Proxy Registrar."""

import os
import sys
from uaclient import FICH_LOG
import socket
import socketserver
import random
from xml.sax.handler import ContentHandler
import hashlib
import json
import time


class XMLHandler(ContentHandler):
    """Configuramos el XML."""

    def __init__(self):
        #Diccionario delos datos de las etiquetas:
        self.tag_dic = {}
        #Lista donde guardar los diccionarios:
        self.list_dic = []


def Find_Passwd(USER, FICH):
    """Comprueba la contraseña para cada USER."""
    file = open(FICH, "r")
    LINES = file.readlines()
    PASSWORD = ''
    for line in LINES:
        USER_LINE = line.split(" ")[1]
        if USER == USER_LINE:
            PASSWORD = line.split(" ")[3]
    return PASSWORD


class ProxyRegistrarHandler(socketserver.DatagramRequestHandler):
    """Proxy-Registrar server class."""

    #Diccionario de clientes:
    client_dic = {}

    def json2registered(self):
        """Metodo que comprueba si hay fichero JSON."""
        try:
            with open("registered.json", "r") as client_file:
                #Lee su contenido y lo usa como dic de USER.
                self.client_dic = json.load(client_file)
                self.file_exists = True
        except:
            self.file_exists = False

    def register2json(self):
        """Fichero JSON: user + dic + time"""
        with open("registered.json", "w") as jsonfile:
            json.dump(self.client_dic, jsonfile, indent=4, sort_keys=True,
                      separators=(',', ':'))

    METHODS = ['REGISTER', 'INVITE', 'ACK', 'BYE']

    #Variable pseudoaletoria NONCE:
    NONCE = []

    def handle(self):
        """Metodo que gestiona las peticiones."""
        self.json2registered()

        #Escribe dirección y puerto del cliente (de tupla client_address)
        IP_CLIENT = str(self.client_address[0])
        PORT_CLIENT = str(self.client_address[1])

        #Metodo que gestiona las peticiones:
        while 1:
        #Leyendo línea a línea lo que nos envía el cliente/servidor
            text = self.rfile.read()
            LINE = text.decode('utf-8')

            if not LINE:
                break

            method = text.decode('utf-8').split(' ')[0]

            #Escribimos en el fichero LOG:
            FICH_LOG(PATH_LOG, 'Received from', IP_CLIENT, PORT_CLIENT, LINE)

            print('-----RECEIVED:\r\n' + LINE)

            if not method in self.METHODS:
                answer = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                #Enviamos el mensaje de respuesta:
                self.wfile.write(bytes(answer, 'utf-8'))
                #Añadimos al fichero LOG:
                FICH_LOG(PATH_LOG, 'Error', IP_CLIENT, PORT_CLIENT, answer)

                print('-----SENDING:\r\n' + answer)

            elif method == 'REGISTER':
                #Comprobamos VERIFICACION:
                line_slices = text.decode('utf-8').split()
                expires = text.decode('utf-8').split()[4]

                if 'Digest' not in line_slices:
                    self.NONCE.append(str(random.randint(00000000000000000000,
                                                         9999999999999999999)))

                    answer = 'SIP/2.0 401 Unauthorized\r\n'
                    answer += 'WWW-Authenticate: Digest nonce='
                    answer += self.NONCE[0] + '\r\n\r\n'

                    #Enviamos el mensaje de respuesta:
                    self.wfile.write(bytes(answer, 'utf-8'))
                    #Escribimos en el fichero LOG:
                    FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT,
                             PORT_CLIENT, answer)

                    print('-----SENDING:\r\n' + answer)

                elif int(expires) == 0:
                    self.USER = text.decode('utf-8').split()[1].split(':')[1]
                    self.PORT = text.decode('utf-8').split()[1].split(':')[2]
                    self.json2registered()

                    answer = 'SIP/2.0 200 OK'
                    #Escribimos mensaje de respuesta:
                    self.wfile.write(bytes(answer, 'utf-8'))

                    try:
                        del self.client_dic[USER]
                    except:
                        print('-----USER NOT FOUND')

                    self.Client_Expired()
                    self.json2registered()

                else:
                    #Guardamos la peticion REGISTER:
                    self.USER = text.decode('utf-8').split()[1].split(':')[1]
                    self.PORT = text.decode('utf-8').split()[1].split(':')[2]
                    self.EXPIRES = text.decode('utf-8').split()[4]
                    hresponse = text.decode('utf-8').split()[-1].split('=')[1]

                    #Comparamos CONTRASEÑAS:
                    my_digest = hashlib.md5()
                    my_digest.update(bytes(self.NONCE[0], 'utf-8'))
                    my_digest.update(bytes(Find_Passwd(self.USER, DATA_PASSW),
                                           'utf-8'))
                    my_digest.digest

                    if hresponse == my_digest.hexdigest():
                        self.client_list = []
                        self.client_list.append(IP_CLIENT)
                        self.client_list.append(self.PORT)
                        self.client_list.append(self.EXPIRES)

                        self.client_dic[self.USER] = self.client_list
                        #Vaciamos:
                        self.client_list = []

                        self.Client_Expired()
                        self.register2json()

                        answer = 'SIP/2.0 200 OK\r\n\r\n'
                        #Enviamos el mensaje de respuesta:
                        self.wfile.write(bytes(answer, 'utf-8'))
                        #Añadimos al fichero LOG:
                        FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT,
                                 str(self.PORT), answer)

                        print('-----SENDING:\r\n' + answer)

                    else:
                        print('-----BAD PASSWORD FROM CLIENT')
                        answer = 'SIP/2.0 400 Bad Request'
                        self.wfile.write(bytes(answer, 'utf-8'))
                        #Añadimos al fichero LOG:
                        FICH_LOG(PATH_LOG, 'Error', IP_CLIENT,
                                 str(self.PORT), '')

                    self.NONCE.clear()

            elif method == 'INVITE':
                self.json2registered()
                self.Client_Expired()

                #Definimos las variables:
                USER = text.decode('utf-8').split()[1].split(':')[1]
                RTP_PORT = text.decode('utf-8').split()[-2]

                if USER in self.client_dic.keys():
                    #Buscamos del DIC: IP y PORT:
                    IP_SERV = self.client_dic[USER][0]
                    PORT_SERV = self.client_dic[USER][1]

                    try:
                        #Creamos socket, configuramos y atamos:
                        my_socket = socket.socket(socket.AF_INET,
                                                  socket.SOCK_DGRAM)
                        my_socket.setsockopt(socket.SOL_SOCKET,
                                             socket.SO_REUSEADDR, 1)
                        my_socket.connect((IP_SERV, int(PORT_SERV)))

                        #Enviando:
                        print("-----SENDING: \r\n" + LINE)
                        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                        #Escribimos en el fichero LOG:
                        FICH_LOG(PATH_LOG, 'Send to', IP_SERV, PORT_SERV, LINE)

                        #Recibimos datos:
                        data = my_socket.recv(int(PORT_SERV))
                        LINE = data.decode('utf-8')
                        self.wfile.write(bytes(LINE, 'utf-8'))

                        #Escribimos en el fichero LOG:
                        FICH_LOG(PATH_LOG, 'Received from', IP_SERV,
                                 PORT_SERV, LINE)
                        print('-----RECEIVED: \r\n', LINE)

                    except ConnectionRefusedError:
                        print('ERROR: No server listening at ' + str(IP_SERV) +
                              ' at port: ' + str(PORT_SERV) + '\r\n\r\n')
                        #Escribimos en el fichero LOG:
                        FICH_LOG(PATH_LOG, 'Error', IP_SERV, PORT_SERV, '')
                else:
                    answer = 'SIP/2.0 404 User Not Found\r\n\r\n'
                    self.wfile.write(bytes(answer, 'utf-8'))
                    #Escribimos en el fichero LOG:
                    FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT, PORT_CLIENT,
                             answer)

                    print("-----SENDING: \r\n" + LINE)

            elif method == 'ACK':
                self.json2registered()
                self.Client_Expired()

                USER = text.decode('utf-8').split()[1].split(':')[1]
                #Buscamos del DIC: IP y PORT:
                IP_SERV = self.client_dic[USER][0]
                PORT_SERV = self.client_dic[USER][1]

                #Escribimos en el fichero LOG:
                FICH_LOG(PATH_LOG, 'Received from', IP_SERV, PORT_SERV, LINE)

                try:
                    # Creamos socket, configuramos y atamos:
                    my_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((IP_SERV, int(PORT_SERV)))

                    #Enviando:
                    print("-----SENDING: \r\n" + LINE)
                    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                    #Escribimos en el fichero LOG:
                    FICH_LOG(PATH_LOG, 'Send to', IP_SERV, PORT_SERV, LINE)

                except ConnectionRefusedError:
                    print('ERROR: No server listening at ' + str(IP_SERV) +
                          ' at port: ' + str(PORT_SERV) + '\r\n\r\n')
                    #Escribimos en el fichero LOG:
                    FICH_LOG(PATH_LOG, 'Error', IP_SERV, PORT_SERV, '')

            elif method == 'BYE':
                self.json2registered()
                self.Client_Expired()

                #Buscamos del DIC: IP y PORT:
                USER = text.decode('utf-8').split()[1].split(':')[1]
                IP_SERV = self.client_dic[USER][0]
                PORT_SERV = self.client_dic[USER][1]

                try:
                    #Creamos socket, configuramos y atamos:
                    my_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((IP_SERV, int(PORT_SERV)))

                    #Enviando al SERVER:
                    print("-----SENDING: \r\n" + LINE)
                    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                    #Escribimos en el fichero LOG:
                    FICH_LOG(PATH_LOG, 'Send to', IP_SERV, PORT_SERV, LINE)

                    #Recibimos datos:
                    data = my_socket.recv(int(PORT_SERV))
                    LINE = data.decode('utf-8')
                    self.wfile.write(bytes(LINE, 'utf-8'))
                    #Escribimos en el fichero LOG:
                    FICH_LOG(PATH_LOG, 'Received from', IP_SERV, PORT_SERV,
                             LINE)
                    #Añadimos al fichero LOG:
                    FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT, '', LINE)
                    #Enviando al CLIENT:
                    print('-----SENDING:\r\n' + LINE)
                except ConnectionRefusedError:
                    print('ERROR: No server listening at ' + str(IP_SERV) +
                          ' at port: ' + str(PORT_SERV) + '\r\n\r\n')
                    #Escribimos en el fichero LOG:
                    FICH_LOG(PATH_LOG, 'Error', IP_SERV, PORT_SERV, '')

            else:
                self.json2registered()
                self.Client_Expired()

                answer = 'SIP/2.0 400 Bad Resquest\r\n\r\n'
                self.wfile.write(bytes(answer, 'utf-8'))

                #Escribimos en el fichero LOG:
                FICH_LOG(PATH_LOG, 'Error', IP_SERV, PORT_SERV, '')

    def Client_Expired(self):
        """Comprueba si un antiguo cliente sigue en el diccionario."""
        now = time.strftime("%Y-%m-%d %H:%M:%S",
                            time.gmtime(time.time()))
        expired_dic = []
        for client in self.client_dic:
            if self.client_dic[client][2] < now:
                expired_dic.append(client)
        for client in expired_dic:
            del self.client_dic[client]

        return self.client_dic

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 proxy_registrar.py config")

    try:
        CONFIG = sys.argv[1]

        if not os.path.exists(CONFIG):
            print("File doesnt exist!")
            sys.exit("Usage: python3 proxy_registrar.py config")

    except IndexError:
        sys.exit("Usage: python3 proxy_registrar.py config")

    #Abrimos el fichero XML
    fich = open(CONFIG, 'r')
    line = fich.readlines()
    fich.close()

    #SERVER-PROXY, NAME + IP + PORT:
    SERVER_NAME = line[4].split('>')[1].split('<')[0]
    SERVER_IP = line[5].split('>')[1].split('<')[0]
    SERVER_PORT = line[6].split('>')[1].split('<')[0]

    #DATABASE, PATH + PASSWORD:
    DATA_PATH = line[9].split('>')[1].split('<')[0]
    DATA_PASSW = line[10].split('>')[1].split('<')[0]

    #LOG:
    PATH_LOG = line[13].split('>')[1].split('<')[0]

    try:
        serv = socketserver.UDPServer((SERVER_IP, int(SERVER_PORT)),
                                      ProxyRegistrarHandler)
        print('Proxy-Server ' + SERVER_NAME + ' listening at port ' +
              SERVER_PORT + '...')
        #Escribimos en el fichero LOG:
        FICH_LOG(PATH_LOG, 'Starting...', '', '', '')
        serv.serve_forever()

    except KeyboardInterrupt:
        FICH_LOG(PATH_LOG, 'Error', SERVER_IP, SERVER_PORT, '')
        sys.exit("\r\nEnded Proxy")
