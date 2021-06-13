from Camera import Camera
import urllib.request
import cv2
import numpy as np

from config import HOST, ONVIF_PORT, LOGIN, PASSWORD

print("start")

camera = Camera(HOST, ONVIF_PORT, LOGIN, PASSWORD)

print("SERVICES:", camera.get_available_services())

protocol, address, port, path = camera.get_stream_uri()
good_uri = f"{protocol}//{LOGIN}:{PASSWORD}@{address}:{port}/{path}"
print("valid url:", good_uri)


def CaptureFrontCamera(uri):
	_bytes = bytes()
	stream = urllib.request.urlopen(uri)
	while True:
		_bytes += stream.read(1024)
		a = _bytes.find(b'\xff\xd8')
		b = _bytes.find(b'\xff\xd9')
		if a != -1 and b != -1:
			jpg = _bytes[a:b + 2]
			_bytes = _bytes[b + 2:]
			filename = 'capture.jpeg'
			i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
			cv2.imwrite(filename, i)
			return filename


CaptureFrontCamera(good_uri)
