#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa User Agent Server.
"""
import sys
import socket
import socketserver
import os
from uaclient import FICH_LOG
from xml.sax.handler import ContentHandler

class XMLHandler(ContentHandler):
	def __init__(self):
	# Iniciamos variables

		#Diccionario delos datos de las etiquetas:
		self.tag_dic = {}
		#Lista donde guardar los diccionarios:
		self.list_dic = []

	def startElement(self,name,attrs):
		if name == 'account':
			self.tag_dic['username'] = attrs.get('username','--')
			self.tag_dic['passwd'] = attrs.get('passwd','--')
			#Añadimos:
			self.list_dic.append(self.tag_dic)
			#Vaciamos el diccionario:
			self.tag_dic = {}

		elif name == 'uaserver':
			self.tag_dic['UAS_IP'] = attrs.get('ip', '--')
			self.tag_dic['UAS_Port'] = attrs.get('port','--')
			#Añadimos:
			self.list_dic.append(self.tag_dic)
			#Vaciamos el diccionario:
			self.tag_dic = {}

		elif name == 'rtpaudio':
			self.tag_dic['RTP_Port'] = attrs.get('port', '--')
			#Añadimos:
			self.list_dic.append(self.tag_dic)
			#Vaciamos el diccionario:
			self.tag_dic = {}

		elif name == 'regproxy':
			self.tag_dic['Reg_IP'] = attrs.get('ip', '--')
			self.tag_dic['Reg_Port'] = attrs.get('port','--')
			#Añadimos:
			self.list_dic.append(self.tag_dic)
			#Vaciamos el diccionario:
			self.tag_dic = {}

		elif name == 'log':
			self.tag_dic['PATH'] = attrs.get('path','--')
			#Añadimos:
			self.list_dic.append(self.tag_dic)
			#Vaciamos el diccionario:
			self.tag_dic = {}

		elif name == 'audio':
			self.tag_dic['Audio_PATH'] = attrs.get('path','--')
			#Añadimos:
			self.list_dic.append(tag_dic)
			#Vaciamos el diccionario:
			self.tag_dic = {}

	def getData(self):
		return self.list_dic

class ProxyHandler(socketserver.DatagramRequestHandler):
    """
    Proxy server class.
    """
    RTP = {'IP': '',
           'PORT': []}

    METHODS = ['INVITE', 'ACK', 'BYE']

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP_CLIENT = str(self.client_address[0])
        PORT_CLIENT = int(self.client_address[1])

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            text = self.rfile.read()
            LINE = line.decode('utf-8')

            #Para salir del bucle (si no hay mas lineas):
            if not LINE:
            	break

            method = text.decode('utf-8').split(' ')[0]
            #print("Hemos recibido tu peticion:\r\n", LINE)

            #RECEPTOR_IP = LINE[4].split(' ')[1].split('\r\n')[0]
            #RECEPTOR_PORT = LINE[7].split(' ')[1].split(' ')[0]

            if not method in self.METHODS:
                answer = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                #Enviamos el mensaje de respuesta:
                self.wfile.write(bytes(answer, 'utf-8'))
                #Añadimos al fichero LOG:
                FICH_LOG(PATH_LOG, 'Error', IP_CLIENT, PORT_CLIENT, '')

            elif method == 'INVITE':
            	FICH_LOG(PATH_LOG,'Received from',RECEPTOR_IP,RECEPTOR_PORT,LINE)
                
                answer = 'SIP/2.0 100 Trying\r\n\r\n'
                answer += 'SIP/2.0 180 Ring\r\n\r\n'
                answer += 'SIP/2.0 200 OK\r\n\r\n'
                #Añadimos las cabeceras: Header + Separator:
                answer += 'Content-Type: application/sdp\r\n\r\n'
                #Message Body:
                answer += 'v=0\r\n' + 'o=' + USERNAME + ' ' + IP + '\r\n'
                answer += 's=Prueba' + '\r\n' + 't=0' + '\r\n'
                answer += 'm=audio' + PORT_AUDIO + 'RTP' + '\r\n'

                #Enviamos el mensaje de respuesta:
                self.wfile.write(bytes(answer, 'utf-8'))
                #Añadimos al diccionario RTP:

                #INCOMPLETO!!!!

                #Añadimos al fichero LOG:
                response = answer.split('\r\n')
                LINE = ' '.join(response)
                FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT, PORT_CLIENT, LINE)

            elif method == 'ACK':
            	FICH_LOG(PATH_LOG, 'Received from', RECEPTOR_IP, RECEPTOR_PORT, LINE)

            #Envio RTP:
            # aEjecutar es un string con lo que se ha de ejecutar en la shell
                aEjecutar = './mp32rtp -i ' + self.RTP['IP']
                aEjecutar += '-p' + self.RTP['PORT']
                aEjecutar += '< ' + PATH_AUDIO
                print ("Let's run ", aEjecutar)
                os.system(aEjecutar)
                FICH_LOG(PATH_LOG, 'Send to', self.RTP['IP'], self.RTP['PORT'],'Audio File')

                print('Finished transfer!')
                FICH_LOG(PATH_LOG, 'Finished audio transfer','','','')

            elif method == 'BYE':
            	FICH_LOG(PATH_LOG, 'Received from', RECEPTOR_IP, RECEPTOR_PORT, LINE)

                answer = 'SIP/2.0 200 OK\r\n\r\n'
                #Enviamos el mensaje de respuesta:
                self.wfile.write(bytes(answer, 'utf-8'))
                #Añadimos al fichero LOG:
                response = answer.split('\r\n')
                LINE = ' '.join(response)
                FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT, PORT_CLIENT, LINE)

            else:
            	FICH_LOG(PATH_LOG, 'Received from', RECEPTOR_IP, RECEPTOR_PORT, LINE)

                answer = 'SIP/2.0 400 Bad Request\r\n\r\n'
                #Enviamos el mensaje de respuesta:
                self.wfile.write(bytes(answer, 'utf-8'))
                #Añadimos al fichero LOG:
                response = answer.split('\r\n')
                LINE = ' '.join(response)
                FICH_LOG(PATH_LOG, 'Error', IP_CLIENT, PORT_CLIENT, '')


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
    print("Listening...")

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        FICH_LOG(PATH_LOG, 'Error', IP_PROXY, PORT_PROXY, '')
        sys.exit('\r\nEnded server')
