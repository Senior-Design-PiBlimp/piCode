#!/usr/bin/python

DEBUG             = True

WORD_LENGTH	  = 4
PACKET_LENGTH     = (WORD_LENGTH*32)     #4 bytes * 32 words
PACKET_DELIM      = ord('?')   #convert '?' to ASCII value

PORT_NUM          = 2619

TYPE_SET_PWM      = 100
TYPE_GET_PWM      = 101
TYPE_CONN_ESTAB   = 200
TYPE_CONN_CLOSE   = 201
TYPE_KEEP_ALIVE   = 1
TYPE_VID_CTRL     = 50

MOTOR_IGNORE      = 0
MOTOR_LEFT        = 1
MOTOR_RIGHT       = 2
MOTOR_LEFT_SERVO  = 3
MOTOR_RIGHT_SERVO = 4

DIR_IGNORE        = 0
DIR_FWD           = 1
DIR_REV           = 2

VID_STOP          = 0
VID_START         = 1
VID_RESTART       = 2

TIMEOUT_SLEEP     = 3  #seconds to wait before decending 
DECEND_PERCENT    = 15 #motor speed when in auto_decend



STREAM_ENV        = {"LD_LIBRARY_PATH":, "."}
STREAM_PATH       = "/usr/src/mjpg-streamer/mjpg-streamer-experimental/"
STREAM_CMD        = "mjpg_streamer -o 'output_http.so -w ./www' -i 'input_raspicam.so -x 640 -y 480 -fps 20  -ex sports -quality 10 -mm matrix -rot 90'"


