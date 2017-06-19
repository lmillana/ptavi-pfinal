#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa Proxy Registrar
"""

import os
import sys
from uaclient import FICH_LOG
import socket
import socketserver
import random
from xml.sax.handler import ContentHandler

class XMLHandler(ContentHandler):
	def __init__(self):
	# Iniciamos variables

		#Diccionario delos datos de las etiquetas:
		self.tag_dic = {}
		#Lista donde guardar los diccionarios:
		self.list_dic = []

	def startElement(self,name,attrs):
		#Almacena en un dic los datos del XML:
		if name == 'server':
			self.tag_dic['username'] = attrs.get('username','--')
			self.tag_dic['IP'] = attrs.get('ip','--')
			self.tag_dic['PORT'] = attrs.get('port', '--')
			#Añadimos:
			self.list_dic.append(self.tag_dic)
			#Vaciamos el diccionario:
			self.tag_dic = {}

		elif name == 'database':
			self.tag_dic['PATH'] = attrs.get('path', '--')
			self.tag_dic['passwdpath'] = attrs.get('passwdpath','--')
			#Añadimos:
			self.list_dic.append(self.tag_dic)
			#Vaciamos el diccionario:
			self.tag_dic = {}

		elif name == 'log':
			self.tag_dic['path'] = attrs.get('path', '--')
			#Añadimos:
			self.list_dic.append(self.tag_dic)
			#Vaciamos el diccionario:
			self.tag_dic = {}

	def getData(self):
		return self.list_dic

class ProxyRegistrarHandler(socketserver.DatagramRequestHandler):
	"""
	Proxy-Registrar server class
	"""

	#Diccionario de clientes:
	client_dic = {}

	def register2json(self):
		#Fichero JSON: user + dic + time
		json.dump(self.client_dic, open('registered.json', 'w'))

	def json2registered(self):
		#Metodo que comprueba si hay fichero JSON.
		try:
			with open('registered.json') as client_file:
				#Lee su contenido y lo usa como dic de user.
				self.client_dic = json.load(client_file)
				self.file_exists = True
		except:
			#Actua como si no hubiera fichero JSON
			self.file_exists = False

	METHODS = ['REGISTER', 'INVITE', 'ACK', 'BYE']

    #Variable pseudoaletoria NONCE:
    #NONCE = random.getrandbits(100)

	def handle(self):
		#Escribe dirección y puerto del cliente (de tupla client_address)
		IP_CLIENT = str(self.client_address[0])


		#Metodo que gestiona las peticiones:
		while 1:
		#Leyendo línea a línea lo que nos envía el cliente/servidor
			text = self.rfile.read()
			LINE = text.decode('utf-8')

			if not LINE:
				break

			method = text.decode('utf-8').split(' ')[0]

			print('-----RECEIVED:\r\n' +  LINE)

			if not method in self.METHODS:
				answer = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
				self.wfile.write(bytes(answer, 'utf-8'))
				#Añadimos al fichero LOG:
				FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT, str(self.PORT), answer)

			elif method == 'REGISTER':
				#Guardamos la peticion REGISTER:
				self.PORT = text.decode('utf-8').split()[1].split(':')[2]
				self.USER = text.decode('utf-8').split()[1].split(':')[1]
				self.EXPIRES = text.decode('utf-8').split()[4]

				self.client_list = []
				self.client_list.append(IP_CLIENT)
				self.client_list.append(self.PORT)
				self.client_list.append(self.EXPIRES)

				self.client_dic[self.USER] = self.client_list
				#Vaciamos:
				#self.delete()
				self.client_list = []

				answer = 'SIP/2.0 200 OK\r\n\r\n'
				#Enviamos el mensaje de respuesta:
				self.wfile.write(bytes(answer, 'utf-8'))
				#Añadimos al fichero LOG:
				FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT, str(self.PORT), answer)

				print('-----SENDING:\r\n' + answer)

			elif method == 'INVITE':
				
				#Definimos las variables:
				USER = text.decode('utf-8').split()[1].split(':')[1]
				RTP_PORT = text.decode('utf-8').split()[-2]
				#Buscamos del DIC: IP y PORT:
				IP_SERV = self.client_dic[USER][0]
				PORT_SERV = self.client_dic[USER][1]

				try:
					# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
					my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
					FICH_LOG(PATH_LOG, 'Received from', IP_SERV, PORT_SERV, LINE)
					print('-----RECEIVED: \r\n', LINE)

				except ConnectionRefusedError:
					print('ERROR: No server listening at '+ str(IP_SERV) + ' at port: ' + str(PORT_SERV) + '\r\n\r\n')
					#Escribimos en el fichero LOG:
					FICH_LOG(PATH_LOG, 'Error', IP_SERV, PORT_SERV, '')

			elif method == 'ACK':
				answer = 'ACK RECEIVED\r\n\r\n'
				self.wfile.write(bytes(answer, 'utf-8'))

				#Escribimos en el fichero LOG:
				FICH_LOG(PATH_LOG, 'Received from', IP_SERV, PORT_SERV, answer)

			elif method == 'BYE':
				answer = 'SIP/2.0 200 OK\r\n\r\n'
				self.wfile.write(bytes(answer, 'utf-8'))

				#Escribimos en el fichero LOG:
				FICH_LOG(PATH_LOG, 'Finishing...', IP_SERV, PORT_SERV, '')
			
			else:
				answer = 'Something its wrong, baby\r\n\r\n'
				self.wfile.write(bytes(answer, 'utf-8'))

				#Escribimos en el fichero LOG:
				FICH_LOG(PATH_LOG, 'Error', IP_SERV, PORT_SERV, '')


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
		serv = socketserver.UDPServer((SERVER_IP,int(SERVER_PORT)), ProxyRegistrarHandler)
		print('PROXY ' + SERVER_NAME + ' listening at port ' + SERVER_PORT + '...')
		#Escribimos en el fichero LOG:
		FICH_LOG(PATH_LOG, 'Starting...', '','','')
		serv.serve_forever()

	except KeyboardInterrupt:
		FICH_LOG(PATH_LOG, 'Error', SERVER_IP, SERVER_PORT, '')
		sys.exit("\r\nEnded Proxy")
