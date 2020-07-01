import time, pyaudio,string,serial
from multiprocessing import Process
import requests
import getmac
import pynmea2
import speech_recognition as sr
import Adafruit_DHT
from gtts import gTTS as s2t

# DHT22
SERVER_IP = '192.168.0.104'
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
API_URL = 'http://' + SERVER_IP
SEND_DATA = '/insertData'
RAISE_ALERT = '/raiseAlert'
GET_ALERTS = '/getalerts'

# NEO 6M GPS
PORT = '/dev/ttyS0'
SERIAL = serial.Serial(PORT,baudrate=9600,timeout=0.5)

# Speech Recognition
RECOGNIZER = sr.Recognizer()

def getData_NEO6M():
	serialRow = SERIAL.readline().decode('utf-8')
	if (serialRow[0:6] == '$GPRMC'):
		parsedSerialRow = pynmea2.parse(serialRow)
		return {
			'latitude' : parsedSerialRow.latitude,
			'longitude': parsedSerialRow.longitude
		}

def getData_DHT22():
	h,t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
	return {'temperature':t,'humidity':h}

def parallelRun(*procs):
  thread = []
  for process in procs:
    p = Process(target=process).start()
    thread.append(p)
  for p in thread:
    p.join()

def p1(): # Data aquire , server communication
	idx = 0
	postData = {
		'device_key' : getmac.get_mac_address(),
		'data' : {
			'temperature': None,
			'humidity': None,
			'latitude': None,
			'longitude': None
		}
	}
	while True:
		print("Data aquire process active !")

		tmp = getData_DHT22()
		#gps = getData_NEO6M()
		print(gps)
		postData['data']['temperature'] = tmp['temperature']
		postData['data']['humidity'] = tmp['humidity']
		'''
		try:
			postData['data']['latitude'] = gps['latitude']
			postData['data']['longitude'] = gps['longitude']
		except:
			pass
		'''
		#requests.post(API_URL+SEND_DATA,json=postData) # Send data and reset for next data set
		response = requests.get(API_URL+GET_ALERTS)
		content = response.content.decode('utf-8')
		print(content)
		for item in content['data']:
			f = s2p(item['desc'],lang='ro')
			f.save(item['cod']+'.mp3')
			os.system('mpg321 -a plughw ' + item['cod'] +'.mp3')
		time.sleep(60) # Acquire data every 60 seconds, send them every 10 minutes
	

def p2(): # Voice managing
	try:
		with sr.Microphone as ainput:
			while True:
				RECOGNIZER.adjust_for_ambient_noise(ainput,duration=5)
				voiceSignal = RECOGNIZER.listen(ainput)
				message = RECOGNIZER.recognize_google(voiceSignal,language='ro-RO')
				if (message == 'ajutor'):
					bodyMessage = {
						'device_key': getmac.get_mac_address(),
					}
					requests.post(API_URL+RAISE_ALERT,json=bodyMessage)
	except:
		# Raise no mic detected alert
		pass

if __name__ == '__main__':
	parallelRun(p1,p2)