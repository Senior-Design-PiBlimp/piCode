Pi-Code
=======

Code for onboard the Pi

Implemented as a TCP server accepting only 1 connection at a time.
A keep-alive packet must be recieved every second, or connection
is assumed to be lost. 

On connection lost, blimp enters an auto-landing mode. 


