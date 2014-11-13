

from time import sleep

#grab DEBUG
import netconstants 


#grab Adafruit library
from Adafruit_PWM_Servo_Driver import PWM


class Motor:
	
	pwm = PWM(0x40, debug=False)
	init = False;

	freq=300 #PWM frequency
	FORWARD = 1
	REVERSE = 2
	STOPTIME = .5 #time it takes for motor to come to complete stop

	@staticmethod
	def allOff():
		Motor.pwm.setAllPWM(0,0)
	
	@staticmethod
	def initPWM():
		if (Motor.init == False):
			Motor.pwm.setPWMFreq(Motor.freq)
			Motor.init = True

	def __init__(self, pwmport, setMin, setMax, startVal=0, revPort=-1, name="", inv=False):
		if (netconstants.DEBUG): print "Init Motor: ", name, " on ", pwmport
		Motor.initPWM();

		self.port = pwmport;
		self.revPort = revPort;
		self.invert = inv; #invert the percentage (100 <-> 0)

		self.name = name;

		self.startValue = startVal;
		self.pwmmin = setMin;
		self.pwmmax = setMax;

		#for documentation purposes, note these vars are available
		self.direction = Motor.FORWARD;
		self.value = 0;
		self.resting = False;   #true if motors are 'reversed' but off
	
		self.reset();

	#reset to default state
	def reset(self):
		self.setDir(Motor.FORWARD);
		self.setPercent(self.startValue);

	def getName(self):
		return self.name;
	def setName(self, newname):
		self.name=newname;

	def getValue(self):
		return self.value;

	def getPercent(self):
		
		p = (float(self.value - self.pwmmin) / 
			float(self.pwmmax - self.pwmmin)) * 100;
		if self.invert: return 100-p
		else: return p

	#percent is an integer [0-100]
	def setPercent(self, percent):

		if self.invert: percent = 100 - percent

		if percent < 0 or percent > 100:
			return -1

		return self._setValue(self.pwmmin + 
			int(float(self.pwmmax - self.pwmmin) *
			 float(float(percent)/float(100))))

	def _setValue(self, newvalue):

		ret = 0 ;
		if(newvalue < self.pwmmin):
			self.value = self.pwmmin;
			ret = -1;
		elif(newvalue > self.pwmmax):
			self.value = self.pwmmax;
			ret = 1;
		else:
			self.value=newvalue;

		Motor.pwm.setPWM(self.port, 0, self.value)

	        return ret;

	def getMax(self):
		return self.pwmmax;
	def setMax(self, newmax):
		self.pwmmax = newmax;
	def goMax(self):
		return self.setPercent(100);
	def getMin(self):
		return self.pwmmin;
	def setMin(self, newmin):
		self.pwmmin = newmin;
	def goMin(self):
		return self.setPercent(0);
	def goHalf(self):
		return self.setPercent(50);

	def incr(self, incr=10):
		return self._setValue(self.value + incr);

	def decr(self, decr=10):
		return self._setValue(self.value - decr);

	def setFreq(self, freq):
		return Motor.pwm.setPWMFreq(freq);
	


	#TODO: IMPLEMENT HARDWARE DIRECTION CHANGE
	#0 - no change
	#1 - forward
	#2 - reverse
	#as a safety feature, the motors are stopped before changing direction
	def setDir(self, d):

		if (netconstants.DEBUG):
			print "setDir: ", d
			print "revPort: ", self.revPort

		if(self.revPort < 0 or self.revPort > 15):
			return -1; #we cannot reverse this motor

		prevval = self.getValue()


		if (d==Motor.FORWARD):
			if (netconstants.DEBUG): print "\tFORWARD"
			if(self.direction == Motor.REVERSE and prevval != self.getMin()):
				self.goMin();
				sleep(Motor.STOPTIME);
				self._forwardRelay()
				self.direction = Motor.FORWARD
				self._setValue(prevval);
			else:
				self._forwardRelay()
				self.direction = Motor.FORWARD
		elif (d==Motor.REVERSE):
			if (netconstants.DEBUG): print "\tREVERSE"
			if(self.direction == Motor.FORWARD and prevval != self.getMin()):
				self.goMin();
				sleep(Motor.STOPTIME);
				self._revRelay()
				self.direction = Motor.REVERSE
				self._setValue(prevval);
			else:
				self._revRelay()
				self.direction = Motor.REVERSE
		elif (d==0):
			if (netconstants.DEBUG): print "\tNO CHANGE"
		else:
			if (netconstants.DEBUG): print "\tERROR"

	def _revRelay(self):
			Motor.pwm.setPWM(self.revPort, 4096, 0)
	def _forwardRelay(self):
			Motor.pwm.setPWM(self.revPort,0,0)

	def getDir(self):
		return self.direction




