#!/usr/bin/python

from motor import Motor
from time import sleep
#from thread import *
from netconstants import *

import shlex, subprocess, signal #for spawning the streaming service

import threading 
import socket
import atexit

import psutil
import os


connCount         = threading.Event();
connCount.clear()

class ConnectionDroppedError(Exception):
  def __init__(self,value):
    self.value = value;
  def __str__(self):
    return repr(self.value);


class PacketProcessingError(Exception):
  def __init__(self,value):
    self.value = value;
  def __str__(self):
    return repr(self.value);


#class which handles incoming/outgoing packets
class CommHandler:
  
  stream_process = None;
  atexit_registered = False;
  #DEVNULL = os.open(os.devnull, os.O_RDWR)

  

  motorDict = {                   #port  min   max  start rev   name       inv
       str(MOTOR_LEFT       ) : Motor(0, 1300, 2600, 0,   4, "Fan Left"),
       str(MOTOR_RIGHT      ) : Motor(1, 1300, 2600, 0,   5, "Fan Right"),
       str(MOTOR_LEFT_SERVO ) : Motor(2, 1065, 2320, 100,-1, "Servo Left", False),
       str(MOTOR_RIGHT_SERVO) : Motor(3, 1365, 2620, 100,-1, "Servo Right", True),
       str(MOTOR_PAN        ) : Motor(6, 1065, 2620, 50, -1, "Tilt"),
       str(MOTOR_TILT       ) : Motor(7, 1065, 2620, 50, -1, "Pan")
        }


  #don't allow more than 1 thread to interact with motors
  motor_lock = threading.Lock() 

  @staticmethod
  def stop_and_decend():
    #stop the motors. Wait a few seconds, and decend.
    #this should be run in a seperate thread

    fanleft    = CommHandler.motorDict[str(MOTOR_LEFT)]
    fanright   = CommHandler.motorDict[str(MOTOR_RIGHT)]
    servoleft  = CommHandler.motorDict[str(MOTOR_LEFT_SERVO)]
    servoright = CommHandler.motorDict[str(MOTOR_RIGHT_SERVO)]

    #stop the fans (and release the relays)
    CommHandler.motor_lock.acquire(True);
    fanleft.goMin();
    fanright.goMin();
    fanleft.setDir(Motor.FORWARD)
    fanright.setDir(Motor.FORWARD)
    CommHandler.motor_lock.release()
    
    #wait a few seconds 
    sleep(TIMEOUT_SLEEP)
    
    #check to see if a connection has been established yet

    if DEBUG: print "thread connCount: ", connCount.isSet()

    if connCount.isSet():
      pass
    else:
      #set the servos to decend, and motors to match
      CommHandler.motor_lock.acquire(True);
      servoleft.goMin()
      servoright.goMin()
      fanleft.setDir(Motor.REVERSE)
      fanright.setDir(Motor.REVERSE)
      fanleft.setPercent(DECEND_PERCENT)
      fanright.setPercent(DECEND_PERCENT)
      CommHandler.motor_lock.release()
    

  @staticmethod
  def startVideo():

    #make sure we kill the process on exit
    if CommHandler.atexit_registered == False:
      atexit.register(CommHandler.stopVideo)
      CommHandler.atexit_registered = True
    
    if CommHandler.stream_process != None:
      #check to see if we have a streaming process
      if CommHandler.stream_process.poll() == None:
        if DEBUG: print "Video already running!"
        return False
    else:
      #check to see if an orphaned process exists
      for p in psutil.process_iter():
        if p.name == STREAM_PROC_NAME:
          if DEBUG: print "Orphaned process discovered!"
          return False
  
    CommHandler.stream_process = subprocess.Popen(
      shlex.split(STREAM_PATH + STREAM_CMD), 
      cwd=STREAM_PATH,
      env=STREAM_ENV)
      #sdout=CommHandler.DEVNULL,
      #sderr=CommHandler.DEVNULL,

  @staticmethod
  def stopVideo():
    if CommHandler.stream_process == None:
      #check to see if an orphaned process exists
      for p in psutil.process_iter():
        if p.name == STREAM_PROC_NAME:
          if DEBUG: print "Orphaned process discovered!"
          p.send_signal(signal.SIGINT)
          return True
      if DEBUG: print "no video process discovered"
      return False
    else:
      #simply send SIGINT
      CommHandler.stream_process.send_signal(signal.SIGINT)
      return True



  def __init__(self,s):
    self.data=bytearray(PACKET_LENGTH);
    self.socket = s;
    self.socket.settimeout(1); 
    self.send_conn_established();



  def process_set_pwm(self):

    #process each row of the packet, minus the header and footer
    if DEBUG: print "-------------------------------"

    CommHandler.motor_lock.acquire(True);
    threads = []
    for i in range(WORD_LENGTH,PACKET_LENGTH-WORD_LENGTH,WORD_LENGTH):
      try:
        m = CommHandler.motorDict[str(self.data[i])]

        m.setPercent(self.data[i+2])
        t = threading.Thread(target=m.setDir, 
                 args=(self.data[i+1],))
        t.start() 
        threads.append(t)
        #start_new_thread(m.setDir,(self.data[i+1],))
        #m.setDir(self.data[i+1])
        
        if DEBUG:
          print "seting motor: ", m.getName();
          print "\tdir: ",m.getDir();
          print "\tval: ",m.getPercent(),"%"
      except KeyError:
        pass
    #wait for reversing threads to join
    [t.join() for t in threads]
    CommHandler.motor_lock.release()

    if DEBUG:
      print "-------------------------------"
      
  def process_get_pwm(self):
    i = 0;
    for i in range(0,len(self.data)-1):
      self.data[i] = 0;

    if DEBUG: print "get pwm"
    for num, m in CommHandler.motorDict.iteritems():
      self.data[int(num)*WORD_LENGTH] = num;
      self.data[(int(num)*WORD_LENGTH) + 1] = m.getDir()
      self.data[(int(num)*WORD_LENGTH) + 2] = int(m.getPercent());
    self.send_get_pwm()
  def process_conn_established(self):
    if DEBUG: print "conn established"

  def process_conn_close(self):
    if DEBUG: print "conn closed" 
    raise ConnectionDroppedError("Expected"); 

  def process_keep_alive(self):
    pass


  def process_vid_ctrl(self):
    if DEBUG: print "vid_ctrl" 
    
    if self.data[WORD_LENGTH] == VID_STOP:
      if DEBUG: print "\tVID_STOP"
      CommHandler.stopVideo();
    elif self.data[WORD_LENGTH] == VID_START:
      if DEBUG: print "\tVID_START"
      CommHandler.startVideo();

    elif self.data[WORD_LENGTH] == VID_RESTART:
      if DEBUG: print "\tVID_RESTART"
      if CommHandler.stream_process != None:
        CommHandler.stopVideo();
        CommHandler.stream_process.wait()
      CommHandler.startVideo();
    else:
      raise PacketProcessingError("Invalid Video Command")

  def process_shutdown(self):
    #yah, so just turn off the computer
    os.system("sudo shutdown -h now")
    
  handlers = { str(TYPE_KEEP_ALIVE):process_keep_alive,
         str(TYPE_SET_PWM   ):process_set_pwm,
               str(TYPE_GET_PWM   ):process_get_pwm,
         str(TYPE_VID_CTRL  ):process_vid_ctrl,
               str(TYPE_CONN_ESTAB):process_conn_established,
         str(TYPE_CONN_CLOSE):process_conn_close,
         str(TYPE_SHUTDOWN  ):process_shutdown}
                  
  def send_conn_established(self):
    self.data[0] = TYPE_CONN_ESTAB;
    self.send();

  def send_get_pwm(self):
    self.data[0] = TYPE_GET_PWM;
    self.send();

  def process(self):
    #verify the message is valid
    
    bytes_rx = 0;
    b = bytearray(1);
    
    
    #inrdy,outrdy,exceptrdy = select.select([self.socket],[],[],1)



    #TODO: HANDLE RECIEVING END OF PACKET BYTE WHEN NOT EXPECTED
    try:
      while(bytes_rx < PACKET_LENGTH):
        if self.socket.recv_into(b,1)  == 0:
          raise ConnectionDroppedError("");
        else:
          self.data[bytes_rx] = b[0];
          bytes_rx += 1;

    except socket.timeout as err:
      #treat the same as a connection dropped
      #so - drop the connection and raise the error

      if DEBUG: print "Socket Timed Out"
      if ENFORCE_TIMEOUT:
        self.socket.shutdown(socket.SHUT_RDWR)
        raise ConnectionDroppedError("Timeout Disconnect");
      return;

    except socket.error as err:
      raise ConnectionDroppedError("Exexpected Disconnect");
    except ConnectionDroppedError:
      raise
      
      
    #is the last byte the delimiter?
    if(self.data[PACKET_LENGTH-1] != PACKET_DELIM):
      raise PacketProcessingError("Packet did not end with delimiter")


    #check to see if the message type is one we recognize
    try:
      CommHandler.handlers[str(self.data[0])](self)
    except KeyError:
      if DEBUG: print "Unknown Packet Type: ", self.data[0];
      raise PacketProcessingError("Unknown Packet Type")
    except ConnectionDroppedError as e:
      raise

    for i in range(0,PACKET_LENGTH-1):
      self.data[i] = 0;


  def send(self):
    self.data[PACKET_LENGTH-1] = PACKET_DELIM;
    self.socket.sendall(self.data);
      






