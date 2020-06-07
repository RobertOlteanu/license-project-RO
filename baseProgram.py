import time
from multiprocessing import Process
import requests

import Adafruit_DHT

SERVER_IP = '192.168.0.104'
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
API_URL = 'http://' + SERVER_IP + '/insertData'

def getData_DHT22():
	h,t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
	return {'temperature':t,'humidity':h}

def runInParallel(*fns):
  proc = []
  for fn in fns:
    p = Process(target=fn)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()

def p1():
	idx = 0
	postData = {'temperature':[],'humidity':[]}
	while True:
		print("P1")
		idx += 1
		tmp = getData_DHT22()
		postData['temperature'].append(tmp['temperature'])
		postData['humidity'].append(tmp['humidity'])
		if (idx >= 10):
			requests.post(API_URL,postData)
			idx = 0
			postData = {'temperature':[],'humidity':[]}
		time.sleep(60) # Acquire data every 60 seconds, send them every 10 minutes

def p2():
	while True:
		print("P2")
		time.sleep(30)

if __name__ == '__main__':
	runInParallel(p1,p2)