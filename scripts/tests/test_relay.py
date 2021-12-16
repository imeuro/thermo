import RPi.GPIO as GPIO
import time

def manageHeater():
	try:

		in1 = 16

		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(in1, GPIO.OUT)
		GPIO.output(in1, False)

		from thermo_read import returnData
		d=returnData()

		print('current temp: '+str(d.tempNow))
		print('desired temp:'+str(d.setTemp))

		if (d.tempNow < d.setTemp):
			GPIO.output(in1, True)
			print('better switch heating on.')
		else:
			GPIO.output(in1, False)
			print('that\'s ok i can turn off now')

	except KeyboardInterrupt:
		GPIO.cleanup()



manageHeater()