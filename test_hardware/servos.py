from gpiozero import Servo
from time import sleep
 
myGPIO=17
servo = Servo(myGPIO) #,min_pulse_width=minPW,max_pulse_width=maxPW)
 
while True:
    servo.max()
    print("max")
    sleep(10)
    servo.min()
    print("min")
    sleep(10)


