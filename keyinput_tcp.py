#!/usr/bin/python

import socket
import curses
import signal
import sys
from time import sleep
from netconstants import *
import atexit

		
#handle SIGINT (pressing ^C on the keyboard)
def signal_handler(signal, frame):
	curses.endwin()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)



#TODO: open a TCP socket to localhost


class BlimpClient:

	class MotorStatus:
		def __init__(self, name, percent=0):
			self.name = name;
			self.dir= DIR_IGNORE;
			self.percent = percent;

		def set(self, dir, percent):
			if dir == DIR_FWD: self.dir = dir
			elif dir == DIR_REV: self.dir = dir
			self.percent = percent;

		def getDir(self):
			return self.dir
		def getPercent(self):
			return self.percent
		
		def __str__(self):
			s=""
			if self.dir == DIR_FWD: s = " FORWARD"
			if self.dir == DIR_REV: s = " REVERSE"
			
			return "{:^10} | {:>3d}% | {}".format(self.name, self.percent, s);

	motors = [
		MotorStatus("Fan1"), 
		MotorStatus("Fan2"), 
		MotorStatus("Servo1",100), 
		MotorStatus("Servo1",100) 
		]


	def __init__(self):
		self.data=bytearray(PACKET_LENGTH);
		self.sock = socket.socket()
		self.sock.connect(("localhost", PORT_NUM))

		self.vid_on = False
		

		#TODO: spawn off a thread to send keepalive packets to the blimp

	def setMotor(self,num, percent, dir):

		if percent == -1: percent = BlimpClient.motors[num-1].getPercent()
		if dir == -1: dir = DIR_IGNORE

		self.data[num*WORD_LENGTH] = num;
		self.data[(num*WORD_LENGTH) + 1] = dir
		self.data[(num*WORD_LENGTH) + 2] = percent;
		BlimpClient.motors[num-1].set(dir,percent)
		self._send(TYPE_SET_PWM)

	def vidCtrl(self, cmd):
		if cmd == VID_START or cmd == VID_RESTART: self.vid_on = True
		elif cmd == VID_STOP: self.vid_on = False
		else: return False
		self.data[WORD_LENGTH] = cmd
		self._send(TYPE_VID_CTRL)
	
	def isVidOn(self): return self.vid_on

	#handles the getPWM packet
	def getStatus(self):
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

	def __del__(self):
		try:
			self._send(TYPE_CONN_CLOSE)
			self.sock.close()
		except:
			pass
		

class UI:
	
	stdscr = None

	def __init__(self, screen):
		print "init"

		self.client = BlimpClient()


		UI.stdscr = screen

		curses.curs_set(0);
		curses.noecho()
		UI.stdscr.move(10,0);
		UI.stdscr.insstr("\t| w,a,s,d: fwd,left,rev,right | u: tilt up | j: tilt down | o: faster | l: slower")
		UI.stdscr.move(11,0);
		UI.stdscr.insstr("\t| q: exit | b: begin video | n: end video")
		self.showStatus()

	def showStatus(self):
		#print the current motor statuses on the screen
		for i in range(0,len(BlimpClient.motors)):
			UI.stdscr.addstr(i,0,str(BlimpClient.motors[i]))

		UI.stdscr.move(6,0)
		UI.stdscr.clrtoeol()
		if self.client.isVidOn():
			UI.stdscr.addstr(6,0,"Video: On")
		else:
			UI.stdscr.addstr(6,0,"Video: Off")

		UI.stdscr.noutrefresh()
		curses.doupdate()
		
	def wait(self):

		c = UI.stdscr.getch()

		if c >= 256: return True
		if (chr(c) == 'q'):
			return False 
		elif (chr(c) == 'w'):
			#forward
			self.client.setMotor(1,-1,DIR_FWD)
			self.client.setMotor(2,-1,DIR_FWD)
		elif (chr(c) == 's'):
			#rev
			self.client.setMotor(1,-1,DIR_REV)
			self.client.setMotor(2,-1,DIR_REV)
		elif (chr(c) == 'a'):
			#left
			self.client.setMotor(1,-1,DIR_FWD)
			self.client.setMotor(2,-1,DIR_REV)
		elif (chr(c) == 'd'):
			#right
			self.client.setMotor(1,-1,DIR_REV)
			self.client.setMotor(2,-1,DIR_FWD)
		elif (chr(c) == 'o'):
			#faster
			speed = BlimpClient.motors[0].getPercent() + 2;
			if speed > 100: speed = 100
			self.client.setMotor(1,speed,DIR_IGNORE)

			speed = BlimpClient.motors[1].getPercent() + 2;
			if speed > 100: speed = 100
			self.client.setMotor(2,speed,DIR_IGNORE)
		elif (chr(c) == 'l'):
			#slower
			speed = BlimpClient.motors[0].getPercent() - 2;
			if speed < 0: speed = 0
			self.client.setMotor(1,speed,DIR_IGNORE)

			speed = BlimpClient.motors[1].getPercent() - 2;
			if speed < 0: speed = 0
			self.client.setMotor(2,speed,DIR_IGNORE)
		elif (chr(c) == 'u'):
			#up
			speed = BlimpClient.motors[2].getPercent() + 2;
			if speed > 100: speed = 100
			self.client.setMotor(3,speed,DIR_IGNORE)

			speed = BlimpClient.motors[3].getPercent() + 2;
			if speed > 100: speed = 100
			self.client.setMotor(4,speed,DIR_IGNORE)
		elif (chr(c) == 'j'):
			#up
			speed = BlimpClient.motors[2].getPercent() - 2;
			if speed < 0: speed = 0
			self.client.setMotor(3,speed,DIR_IGNORE)

			speed = BlimpClient.motors[3].getPercent() - 2;
			if speed < 0: speed = 0
			self.client.setMotor(4,speed,DIR_IGNORE)
		elif (chr(c) == 'b'):
			#begin video
			self.client.vidCtrl(VID_START)
		elif (chr(c) == 'n'):
			#end video
			self.client.vidCtrl(VID_STOP)

		self.showStatus()
		return True;


	def __del__(self):
		pass
		#curses.endwin()




#for i in range(0,len(BlimpClient.motors)):
#	print str(BlimpClient.motors[i])

def main(screen):
	ui = UI(screen)
	while ui.wait(): pass

curses.wrapper(main)






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
