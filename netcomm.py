#!/usr/bin/python

from netconstants import *	 #constants for message types, etc

from thread import *
import socket
import select

import signal
import sys

def signal_handler(signal, frame):
	try:
		sock.close()
	except:
		print "could not close socket"	
	Motor.allOff();
	sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  ,1) #avoid time_wait states
#sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE  ,1) #keepalive connection
#sock.setsockopt(socket.SOL_TCP,    socket.TCP_KEEPIDLE  ,1) #no activity for 1 sec
#sock.setsockopt(socket.SOL_TCP,    socket.TCP_KEEPCNT   ,2) #try 2 times to reach
#sock.setsockopt(socket.SOL_TCP,    socket.TCP_KEEPINTVL ,1) #wait 1 sec between tries


#bind 
try:
	sock.bind(('',PORT_NUM))
except socket.error as msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1];
	sys.exit()



#only allow one connection at a time
sock.listen(1)
while True:
	global connCount
	
	print "Listening..."
	(conn,addr) = sock.accept()
        connCount.set();
	print 'Connected with '+ addr[0] + ':' + str(addr[1]);

 	inpacket = CommHandler(conn);
	while True:
		try:
			inpacket.process();
		except PacketProcessingError as e:
			print "Processing Exception: ",e.value
		except ConnectionDroppedError as e:
			print "Connection Dropped: ",e.value
			break;

	conn.close()
        connCount.clear();
	print 'disnected from '+ addr[0] + ':' + str(addr[1]);


	#now we are in a disconnected state. Spwan off a thread
	#who takes care of the "stop and decend" behaviour.
	#if we reestablish a connection, the thread kills itself
        start_new_thread(CommHandler.stop_and_decend,())


sock.close()
	
'''
#handles connections
def clientthread(conn,addr):

 	inpacket = CommHandler(conn);
	#inpacket.send_conn_established();


	while True:
		try:
			inpacket.process();
		except PacketProcessingError as e:
			print "Processing Exception: ",e.value
		except ConnectionDroppedError as e:
			print "Connection Dropped: ",e.value
			break;

	conn.close()
	print 'disnected from '+ addr[0] + ':' + str(addr[1]);



while 1:
	#accept connections
	(conn,addr) = sock.accept()
	print 'Connected with '+ addr[0] + ':' + str(addr[1]);
	start_new_thread(clientthread, (conn,addr))

sock.close()

'''






