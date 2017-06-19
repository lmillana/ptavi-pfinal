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
		PORT_CLIENT = int(self.client_address[1])
		print (IP_CLIENT)
		print(PORT_CLIENT)

		
		#Metodo que gestiona las peticiones:
		while 1:
		#Leyendo línea a línea lo que nos envía el cliente/servidor
			text = self.rfile.read()
			LINE = line.decode('utf-8')

			if not LINE:
				break

			method = text.decode('utf-8').split(' ')[0]

			self.client_dic[USER] = 

			#Añadimos mensajes de recepcion en el fichero LOG:
			FICH_LOG(PATH_LOG, 'Received from', IP_CLIENT, PORT_CLIENT, LINE)

			if not method in self.METHODS:
				answer = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'

			elif method == 'REGISTER':
				#Comprobamos si hay fichero JSON:
				self.json2registered()

				#Comprobamos Autenticacion: 
				response = LINE.split(' ')

				#Guardamos la peticion REGISTER:
				self.client_dic[]

				if len(response) == 4:
					self.NONCE.append(str(random.randint(0000, 9999)))
					answer = 'SIP/2.0 401 Unauthorized\r\n'
					answer += 'WWW Authenticate: Digest nonce= '
					answer += str(self.NONCE[0]) + '\r\n\r\n'
					#Enviamos Register sin Autenticacion:
					sel.wfile.write(bytes(answer, 'utf-8'))
					#Escribimos en el fichero LOG:
					FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT, PORT_CLIENT, answer)
				else:
					data = LINE.split('\r\n')[2].split('=')[1]
					#Comprobamos contraseña:

					#Abrimos fichero para la contraseña:
					passwd_file = open(passwd_path,'r')

			else:
				print("Something it's wrong, baby")


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
		sys.exit(" Ended Proxy")
