import Adafruit_DHT
import time
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

while True:
	h,t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
	time.sleep(4)

	if h is not None and t is not None:
		print("T={0:0.1f}*C H={1:0.1f}%".format(t,h))
	else:
		print("Failed to retrieve data")

