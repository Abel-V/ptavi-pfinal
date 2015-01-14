#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import socket
import sys
import os.path
import SocketServer
import os
import time

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import XMLHandler


def WriteLog(Mensaje):
    hora = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    log.write(hora + " " + Mensaje + "\r\n")



class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """
    RTP = {'port': 0, 'ip': '0'}

    def handle(self):

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break
            print "El proxy nos manda " + line
            method = line.split(" ")[0]
            method_list = ['Invite', 'Ack', 'Bye']
            head = line.split("\r\n")[0]
            head_list = head.split(" ")
            sip = head_list[1].split(":")[0]
            sip20 = head_list[2]
            aLog = "Received from " + self.client_address[0] + ":"
            aLog += str(self.client_address[1]) + ":" + head
            WriteLog(aLog)
            if len(head_list) == 3 and sip20 == "SIP/2.0" and sip == "sip":
                if method in method_list:
                    if method == 'Invite':
                        self.RTP['port'] = line.split(" ")[-2]
                        self.RTP['ip'] = line.split(" ")[-3].split("\r\n")[0]
                        if not list_tags[1]['ip']:
                            list_tags[1]['ip'] = '127.0.0.1'
                        SDP = 'v=0\r\no=' + list_tags[0]['username'] + ' '
                        SDP += list_tags[1]['ip'] + '\r\ns=misesion\r\nt=0\r\n'
                        SDP += 'm=audio ' + list_tags[2]['puerto']
                        SDP += ' RTP\r\n\r\n'
                        new_line = 'SIP/2.0 100 Trying\r\n\r\n'
                        new_line += "SIP/2.0 180 Ringing"
                        new_line += '\r\n\r\nSIP/2.0 200 OK\r\n'
                        new_line += 'Content-Type: aplication/sdp\r\n\r\n'
                        new_line += SDP
                        mens = new_line.split("\r\n")
                        aLog = "Sent to "
                        aLog += self.client_address[0] + ":"
                        aLog += str(self.client_address[1])
                        aLog += ": " + mens[0] + " "
                        aLog += mens[1] + " " + mens[2]
                        WriteLog(aLog)
                        self.wfile.write(new_line)
                    if method == 'Ack':
                        print 'Audio RTP a ', self.RTP['port'], '-',
                        print self.RTP['ip']
                        aEjecutar = "./mp32rtp -i " + self.RTP['ip'] + " -p "
                        aEjecutar += self.RTP['port'] + " < "
                        aEjecutar += list_tags[5]['path']
                        print "Vamos a ejecutar ", aEjecutar
                        os.system(aEjecutar)
                        print "Envio de RTP terminado"
                    if method == 'Bye':
                        aEnviar = "SIP/2.0 200 OK"
                        self.wfile.write(aEnviar + '\r\n\r\n')
                        aLog = "Sent to " + self.client_address[0] + ":"
                        aLog += str(self.client_address[1]) + ": " + aEnviar
                        WriteLog(aLog)
                elif not method in method_list:
                    self.wfile.write('SIP/2.0 405 Method Not Allowed\r\n\r\n')
            else:
                self.wfile.write('SIP/2.0 400 Bad Request\r\n\r\n')


if __name__ == "__main__":
    # Comprobación de la linea de argumentos
    if len(sys.argv) != 2:
        sys.exit('Usage: python uaclient.py config method option')

    if not os.path.exists(sys.argv[1]):
        sys.exit("El archivo " + sys.argv[1] + " no existe")

    # Obtención de datos del fichero xml
    fich = open(sys.argv[1])
    parser = make_parser()
    sHandler = XMLHandler()
    parser.setContentHandler(sHandler)
    parser.parse(fich)
    list_tags = sHandler.get_tags()

    # Fichero log
    log = open(list_tags[4]['path'], 'a')

    # Servidor
    serv = SocketServer.UDPServer(("", int(list_tags[1]['puerto'])), \
    EchoHandler)
    print "Listening..."
    serv.serve_forever()
