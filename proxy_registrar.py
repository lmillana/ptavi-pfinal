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
    
    def Check_Passwd(self, PATH, PASSWD, UA, IP, PORT):
        Found = 'False'
        fich = open(PATH, 'r')
        line = fich.readlines()
        
        #USER1 + PASSWD1:
        USER1 = line[1].split(' ')[1]
        PASSWD1 = line[1].split(' ')[3]
        
        #USER2 + PASSWD2:
        USER2 = line[2].split(' ')[1]
        PASSWD2 = line[2].split(' ')[3]
        
        NONCE = str(self.NONCE)
        m = haslib.md5()
        m.update(b'PASSWD')
        m.update(b'NONCE')
        
        response = m.hexdigest()
        if USER1 == UA or USER2 == UA:
            if response == PASSWD1 or response==PASSWD2:
                Found = 'True'
                answer = 'SIP/2.0 200 OK\r\n\r\n'
        else:
            answer = 'Access denied: incorrect password\r\n'
            self.wfile.write(bytes(answer, 'utf-8'))
            #Escribimos en el fich LOG:
        
        FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT, PORT_CLIENT, answer)

        fich.close()
        return Found    

    METHODS = ['REGISTER', 'INVITE', 'ACK', 'BYE']

    #Variable pseudoaletoria NONCE:
    NONCE = random.getrandbits(100)
    
    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP_CLIENT = str(self.client_address[0])
        PORT_CLIENT = int(self.client_address[1])

        #Metodo que gestiona las peticiones:
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente/servidor
            text = self.rfile.read()
            LINE = line.decode('utf-8')

            if not LINE:
            	break
            
            method = text.decode('utf-8').split(' ')[0]
            #Añadimos mensajes de recepcion en el fichero LOG:
            FICH_LOG(PATH_LOG, 'Received from', IP_CLIENT, PORT_CLIENT, LINE)

            if not method in self.METHODS:
                answer = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'

            elif method == 'REGISTER':
                #Comprobamos Autenticacion: 
                response = LINE.split(' ')
                if len(response) == 4:
                    answer = 'SIP/2.0 401 Unauthorized\r\n'
                    answer += 'WWW Authenticate: Digest nonce= '
                    answer += str(self.NONCE) + '\r\n\r\n'
                    #Enviamos Register sin Autenticacion:
                    sel.wfile.write(bytes(answer, 'utf-8'))
                    #Escribimos en el fichero LOG:
                    FICH_LOG(PATH_LOG, 'Send to', IP_CLIENT, PORT_CLIENT, answer)
                elif len(response) == 5:
                    data = LINE.split('\r\n')[2].split('=')[1]
                    #Comprobamos contraseña:
                    
                else:
                    print("Something it's wrong, baby") 
                
            elif method == 'INVITE':
                #Añadimos al fichero LOG:
                print("Respuesta a un INVITE")
                
                #Enviamos al destino:
                    #Primero tenemos que comprobar si es un usuario registrado
            
            elif method == 'ACK':
				try:
		        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
		        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		        my_socket.connect((IP, int(PORT)))

		        #Enviando:
		        print("Sending: \r\n" + LINE)
		        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
		        #Escribimos en el fichero LOG:
		        FICH_LOG(PATH_LOG, 'Send to', IP_PROXY, PORT_PROXY, LINE)
		    
		    except socket.error:
		        sys.exit('ERROR: No Proxy/registrar listening at '+ IP_PROXY + 'Port: '+ PORT_PROXY)
		        #Escribimos en el fichero LOG:
		        FICH_LOG(PATH_LOG, 'Error', IP, PORT, '')
		        sys.exit(FICH_LOG)

		    try:
		        #Recibimos datos:
		        data = my_socket.recv(int(PORT))
		        print("Receiving: \r\n" + data.decode('utf-8'))

		    except socket.error:
		        #Escribimos en el fichero LOG:
		        FICH_LOG(PATH_LOG, 'Error', IP_PROXY, PORT_PROXY, '')
        		sys.exit(FICH_LOG)

¡¡¡

                #Añadimos al fichero LOG:
                print("Respuesta a un ACK")
                #Enviamos al destino:
                    #Primero tenemos que comprobar si es un usuario registrado
            elif method == 'BYE':
                #Añadimos al fichero LOG:
                print("Respuesta a un BYE")
                #Enviamos al destino:
                    #Primero tenemos que comprobar si es un usuario registrado
            
            else:
                answer = 'SIP/2.0 Bad Request\r\n\r\n'
                self.wfile.write(bytes(answer, 'utf-8'))
                #Añadimos al fichero LOG:
                FICH_LOG(PATH_LOG, 'Error', IP, PORT, '')
                


if __name__ == "__main__":
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

    #SERVER-PROXY, NAME + IP + PORT:
    SERVER_NAME = line[4].split('>')[1].split('<')[0]
    SERVER_IP = line[5].split('>')[1].split('<')[0]
    SERVER_PORT = line[6].split('>')[1].split('<')[0]

    #DATABASE, PATH + PASSWORD:
    DATA_PATH = line[9].split('>')[1].split('<')[0]
    DATA_PASSW = line[10].split('>')[1].split('<')[0]

    #LOG:
    PATH_LOG = line[13].split('>')[1].split('<')[0]

    print("Server " + SERVER_NAME + " listening at port " + SERVER_PORT + "...")
    #Escribimos en el fichero LOG:
    FICH_LOG(PATH_LOG, 'Starting...', '','','')

    serv = socketserver.UDPServer((SERVER_IP,int(SERVER_PORT)), ProxyRegistrarHandler)

    try:
        serv.serve_forever()
    except:
        FICH_LOG(PATH_LOG, 'Error', SERVER_IP, SERVER_PORT, '')
        sys.exit(" Ended Proxy")
