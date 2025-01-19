import RPi.GPIO as GPIO    
from time import sleep

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)

while True:
    ch=input("enter your choice:")
    if(ch=="1"):
        import headshots
    elif(ch=="a"):
        GPIO.output(8, GPIO.HIGH)
        sleep(3)
        GPIO.output(8, GPIO.LOW)
    elif(ch=="b"):
        GPIO.output(8, GPIO.HIGH)
        sleep(3)
        GPIO.output(8, GPIO.LOW)
    elif(ch=="c"):
        GPIO.output(8, GPIO.HIGH)
        sleep(3)
        GPIO.output(8, GPIO.LOW)
    elif(ch=="go"):
        GPIO.output(6, True)
        GPIO.output(19, False)
        GPIO.output(13, False)
        time.sleep(4)
    elif(ch=="right"):
        GPIO.output(13, False)
        GPIO.output(13, False)
        GPIO.output(13, False)
        time.sleep(4)
    elif(ch=="left"):
        GPIO.output(13, False)
        GPIO.output(13, False)
        GPIO.output(13, False)
        time.sleep(4)
    else:
        print("choose another choice")
        
        
        
        
