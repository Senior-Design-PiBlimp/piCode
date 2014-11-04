#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import curses
import signal
import sys

from motor import Motor


		
#handle SIGINT (pressing ^C on the keyboard)
def signal_handler(signal, frame):
	curses.endwin()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)



fan1   = Motor(0, 1300, 2600, 1300,  4, "Fan 1");
fan2   = Motor(1, 1300, 2600, 1300,  5, "Fan 2");
servo1 = Motor(2, 1025, 2750, 1025, -1, "Servo 1");
servo2 = Motor(3, 1025, 2750, 1025, -1, "Servo 2");



stdscr = curses.initscr()
curses.noecho()
stdscr.move(10,0);
stdscr.insstr("q: exit | w: max | s: min | h: half | p: off | 0-9: select output")
#stdscr.insertln()
#stdscr.insertln()
#stdscr.insertln()
#stdscr.insertln()
#stdscr.insertln()

curMotor = fan1;
stdscr.move(3,0)
stdscr.deleteln()
stdscr.insertln()
stdscr.insstr('Using Motor: 1 (%s)'% curMotor.getName())



while True:
	c = stdscr.getch()
	
	#go to first line, replace it with the key pressed
	stdscr.move(0,0)
	stdscr.deleteln()
	stdscr.insertln()
	#stdscr.insstr('you pressed %s (code %s)' % (chr(c), c))


	if (chr(c) == 'q'):
		Motor.allOff();
		curses.endwin()
		break;
	elif (chr(c) == 'w'):
		#go to second line. Replace it with current command
		stdscr.move(1,0)
		stdscr.deleteln()
		stdscr.insertln()
		stdscr.insstr('SETING SERVO MAX')
		curMotor.goMax();

	elif (chr(c) == 's'):
		#go to second line. Replace it with current command
		stdscr.move(1,0)
		stdscr.deleteln()
		stdscr.insertln()
		stdscr.insstr('SETING SERVO MIN')
		curMotor.goMin();
	elif (chr(c) == 'p'):
		#go to second line. Replace it with current command
		stdscr.move(1,0)
		stdscr.deleteln()
		stdscr.insertln()
		stdscr.insstr('ALL SERVOS OFF')
		Motor.allOff();
	elif (chr(c) == 'h'):
		#go to second line. Replace it with current command
		stdscr.move(1,0)
		stdscr.deleteln()
		stdscr.insertln()
		stdscr.insstr('SETING SERVO HALF')
		curMotor.goHalf();
	elif (c == 65):
		#go to second line. Replace it with current command
		stdscr.move(1,0)
		stdscr.deleteln()
		stdscr.insertln()

		if (curMotor.incr() != 0):
			stdscr.insstr('Already at maximum duty cycle!')
		else:
			stdscr.insstr('Increasing to: %d (%d %%)' % (curMotor.getValue(), curMotor.getPercent()))
			
	elif (c == 66):
		#go to second line. Replace it with current command
		stdscr.move(1,0)
		stdscr.deleteln()
		stdscr.insertln()

		if (curMotor.decr() != 0):
			stdscr.insstr('Already at minimum duty cycle!')
		else:
			stdscr.insstr('Decreasing to: %d (%d %%)' % (curMotor.getValue(), curMotor.getPercent()))
	
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
