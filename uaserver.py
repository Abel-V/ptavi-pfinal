#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor SIP
"""

import SocketServer
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class DtdXMLHandler(ContentHandler):
    """
    Clase que lee DTD
    """
    def __init__(self):
        self.diccionario = {}

    def startElement(self, name, attrs):
        if name == "account":
            self.guardar(attrs)
        elif name == "uaserver":
            self.guardar(attrs)
        elif name == "rtpaudio":
            self.guardar(attrs)
        elif name == "regproxy":
            self.guardar(attrs)
        elif name == "log":
            self.guardar(attrs)
        elif name == "audio":
            self.guardar(attrs)
        elif name =="server":
            self.guardar(attrs)
        elif name =="database":
            self.guardar(attrs)

    def guardar(self, attrs):
        #Guarda en un diccionario los atributos de cada etiqueta
        atributos = attrs.keys()
        n = 0
        while n < len(atributos):
            self.diccionario[str(atributos[n])] = str(attrs.get(atributos[n], ""))
            n = n + 1


class SIPHandler(SocketServer.DatagramRequestHandler):
    """
    SIP server class
    """
    lista = [0,1]

    def procesar(self, line, HOST):
        """
        Procesa los mensajes recibidos
        """
        # Extraemos el metodo que nos envia el cliente
        linea = line.split(" ")
        metodo = linea[0]
        IP = str(self.client_address[0])
        if metodo == "INVITE":
            #Obtenemos la informacion contenida en SDP
            informacion=line.split('\r\n')
            self.lista[0] = informacion[4].split(" ")[1]
            self.lista[1] = informacion[7].split(" ")[1]
            #Creamos los mensajes de respuesta
            line = 'SIP/2.0 100 Trying' + '\r\n' + '\r\n'
            line += 'SIP/2.0 180 Ringing' + '\r\n' + '\r\n'
            line += 'SIP/2.0 200 OK' + '\r\n'
            line += 'Content-Type:apliccation/SDP\r\n\r\nv=0\r\no=' + registro['username']
            line += " " + registro['uaserver_ip'] + '\r\ns=misesion\r\nt=0\r\n'
            line += 'm=audio ' + registro['rtpaudio_puerto'] + ' RTP\r\n'
            self.wfile.write(line)
        elif metodo == "ACK":
            #Enviamos el audio
            AUDIO = registro['audio_path']
            aEjecutar = './mp32rtp -i ' + self.lista[0] + ' -p ' + self.lista[1] + ' < ' + AUDIO
            os.system(aEjecutar)
            print "audio enviado"
        elif metodo == "BYE":
            line = 'SIP/2.0 200 OK' + '\r\n'
            line += 'Content-Type:apliccation/SDP\r\n\r\nv=0\r\no=' + registro['username']
            line += " " + registro['uaserver_ip'] + '\r\ns=misesion\r\nt=0\r\n'
            line += 'm=audio ' + registro['rtpaudio_puerto'] + ' RTP\r\n' 
            self.wfile.write(line)
        elif metodo != "INVITE" or "ACK" or "BYE":
            line = "SIP/2.0 405 Method Not Allowed" + '\r\n' + '\r\n'
            self.wfile.write(line)
        else:
            line = "SIP/2.0 400 Bad Request" + '\r\n' + '\r\n'
            self.wfile.write(line)

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        while 1:
                # Leyendo línea a línea lo que nos envía el cliente
                line = self.rfile.read()
                if not line:
                    break

                print "El cliente nos manda " + line
                self.procesar(line, HOST)
                # Si no hay más líneas salimos del bucle infinito


if __name__ == "__main__":
try:
    CONFIG= sys.argv[1]
    #Leemos la DTD usando la clase definida en client.py
    parser = make_parser()
    sHandler = DtdXMLHandler()
    parser.setContentHandler(sHandler)
    parser.parse(open(CONFIG))
    registro = sHandler.diccionario
    HOST = registro["uaserver_ip"]
    PORT = int(registro["uaserver_puerto"])
    serv = SocketServer.UDPServer((HOST, PORT), SIPHandler)
    print "Listening..."
    serv.serve_forever()
except IndexError:
    print "Usage: python uaserver.py config"
