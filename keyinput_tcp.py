#!/usr/bin/python

import socket
import curses
import signal
import sys
from time import sleep
from netconstants import *

		
#handle SIGINT (pressing ^C on the keyboard)
def signal_handler(signal, frame):
	curses.endwin()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)



#TODO: open a TCP socket to localhost


class BlimpClient:

	class MotorStatus:
		def __init__(self, name):
			self.name = name;
			self.dir= DIR_IGNORE;
			self.percent = 0;

		def set(dir, percent):
			if dir == DIR_FWD: self.dir = dir
			elif dir == DIR_REV: self.dir = dir
			self.percent = percent;
		
		def __str__(self):
			s = str(self.percent) + "%"
			if dir == DIR_FWD: s += " FORWARD"
			if dir == DIR_REV: s += " REVERSE"
			return name + ": " + s;

	motors = [
		MotorStatus("Fan1"), 
		MotorStatus("Fan2"), 
		MotorStatus("Servo1"), 
		MotorStatus("Servo1") 
		]

	def __enter__(self):
		self.sock = socket.socket()
		self.sock.connect(("localhost", PORT_NUM))

	def __init__(self):
		self.data=bytearray(PACKET_LENGTH);

	def setMotor(num, percent, dir):
		self.data[num*WORD_LENGTH] = num;
		self.data[(num*WORD_LENGTH) + 1] = dir
		self.data[(num*WORD_LENGTH) + 2] = percent;
		BlimpClient.motors[i].set(dir,percent)
		self._send(TYPE_SET_PWM)

	#handles the getPWM packet
	def getStatus():
		for i in range(WORD_LENGTH,PACKET_LENGTH-WORD_LENGTH,WORD_LENGTH):
			BlimpClient.motors[self.data[i*WORD_LENGTH]].set(
					   self.data[(i*WORD_LENGTH) + 1],
					   self.data[(i*WORD_LENGTH) + 2])

	def _send(self, type):
		self.data[0] = type;
		self.data[PACKET_LENGTH-1] = PACKET_DELIM;
		self.sock.sendall(self.data);

		#clear data
		for i in range(0,PACKET_LENGTH-1):
			self.data[i] = 0;

	def cleanup():
		self._send(TYPE_CONN_CLOSE)
		self.sock.close()

	def __exit__(self, type, value, traceback):
		self.cleanup()
		

class UI:

	def __enter__(self):
		print "enter"

		self.stdscr = curses.initscr()
		curses.noecho()
		self.stdscr.move(10,0);
		self.stdscr.insstr("q: exit | w,a,s,d: fwd,left,rev,right | u: tilt up | j: tilt down | o: faster | l: slower")
		
		'''
		self.curMotor = 1       #current motor to use
		self.stdscr.move(3,0)
		self.stdscr.deleteln()
		self.stdscr.insertln()
		self.stdscr.insstr('Using Motor: ', curMotor)
		'''

	def __init__(self, client):
		print "init"
		self.stdscr = None
		self.client = client

	def __exit__(self, type, value, traceback):
		print "exit"
		curses.endwin()
		print "exit"

bc = BlimpClient()
with UI(bc) as ui:
	sleep(5)


'''	
stdscr = curses.initscr()
curses.noecho()
stdscr.move(10,0);
stdscr.insstr("q: exit | w: max | s: min | h: half | p: off | 0-9: select output")
#stdscr.insertln()
#stdscr.insertln()
#stdscr.insertln()
#stdscr.insertln()
#stdscr.insertln()

curMotor = 1       #current motor to use
stdscr.move(3,0)
stdscr.deleteln()
stdscr.insertln()
stdscr.insstr('Using Motor: ', curMotor)

'''

		


'''
with BlimpClient() as client:

	while True:
		c = stdscr.getch()
		
		#go to first line, replace it with the key pressed
		stdscr.move(0,0)
		stdscr.deleteln()
		stdscr.insertln()
		#stdscr.insstr('you pressed %s (code %s)' % (chr(c), c))


		if (chr(c) == 'q'):
			#TODO: close socket
			curses.endwin()
			break;
		elif (chr(c) == 'w'):
			#go to second line. Replace it with current command
			stdscr.move(1,0)
			stdscr.deleteln()
			stdscr.insertln()
			stdscr.insstr('SETING SERVO MAX')
			#curMotor.goMax();

		elif (chr(c) == 's'):
			#go to second line. Replace it with current command
			stdscr.move(1,0)
			stdscr.deleteln()
			stdscr.insertln()
			stdscr.insstr('SETING SERVO MIN')
			#curMotor.goMin();
		elif (chr(c) == 'p'):
			#go to second line. Replace it with current command
			stdscr.move(1,0)
			stdscr.deleteln()
			stdscr.insertln()
			stdscr.insstr('ALL SERVOS OFF')
			#Motor.allOff();
		elif (chr(c) == 'h'):
			#go to second line. Replace it with current command
			stdscr.move(1,0)
			stdscr.deleteln()
			stdscr.insertln()
			stdscr.insstr('SETING SERVO HALF')
			#curMotor.goHalf();
		elif (c == 65):
			#go to second line. Replace it with current command
			stdscr.move(1,0)
			stdscr.deleteln()
			stdscr.insertln()

			#if (curMotor.incr() != 0):
			#	stdscr.insstr('Already at maximum duty cycle!')
			#else:
			#	stdscr.insstr('Increasing to: %d (%d %%)' % (curMotor.getValue(), curMotor.getPercent()))
				
		elif (c == 66):
			#go to second line. Replace it with current command
			stdscr.move(1,0)
			stdscr.deleteln()
			stdscr.insertln()

			#if (curMotor.decr() != 0):
			#	stdscr.insstr('Already at minimum duty cycle!')
			#else:
			#	stdscr.insstr('Decreasing to: %d (%d %%)' % (curMotor.getValue(), curMotor.getPercent()))
		
		elif (c >= 49 and c <= 57): #number 1

			invalid = False;
			stdscr.move(1,0)
			stdscr.deleteln()
			stdscr.insertln()

			if (c == 49):
				curMotor = fan1;
			elif (c == 50):
				curMotor = fan2;
			elif (c == 51):
				curMotor = servo1;
			elif (c == 52):
				curMotor = servo2;
			else:
				invalid=True
			if(invalid):
				curMotor=fan1;
				stdscr.insstr('INVALID SELECTION')
			else:
				stdscr.insstr('SELECTING MOTOR %s %s' % (chr(c), curMotor.getName()))
				stdscr.move(3,0)
				stdscr.deleteln()
				stdscr.insertln()
				stdscr.insstr('Using Motor: %s (%s)'% (chr(c), curMotor.getName()))



		




curses.endwin()
'''
