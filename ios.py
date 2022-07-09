import pyaudio
import requests
import json
import wave
import os
import time

class IO(object):
	def __init__(self, **kwargs):
		self.p = pyaudio.PyAudio()

		if "input_device_index" in kwargs.keys():
			self.__open_stream(kwargs["input_device_index"])
		else:
			self.__open_stream(1)

		if 'UID' in kwargs.keys():
			self.UID = kwargs['UID']

		if 'say_server' in kwargs.keys():
			self.say_server = kwargs['say_server']

		if 'lang' in kwargs.keys():
			self.lang = kwargs['lang']

	def get_data(self):
		data = self.stream.read(4000, exception_on_overflow=False)
		return data

	def start_stream(self):
		self.stream.start_stream()

	def stop_stream(self):
		self.stream.stop_stream()

	def __open_stream(self, input_device_index):
		input_device_index = 0
		mic_info = self.p.get_device_info_by_index(input_device_index)['defaultSampleRate']
		#print(mic_info)

		self.stream = self.p.open(
			format=pyaudio.paInt16,
			channels=1,
			rate=int(mic_info),#44100,
			input=True,
			#frames_per_buffer=44100,
			input_device_index=input_device_index
		)

	def get_microphones(self):
		info = self.p.get_host_api_info_by_index(0)
		numdevices = info.get('deviceCount')

		Devices = {}

		for i in range(0, numdevices):
			if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
				Devices[i] = self.p.get_device_info_by_host_api_device_index(0, i).get('name')

		return Devices

	def selcect_device(self, id: int):
		self.stream.stop_stream()
		self.__open_stream(id)

	def say(self, text):
		r = self.request_to_server({'text': text, 'UID': self.UID, 'lang': self.lang}, self.say_server)

		if r != None:
			data = bytes.fromhex(r.json()['data'])

			name = 'speach'
			self.save_wav(name, data)
			self.speach_wav(name, data)
			os.remove(f'./audios/speach.wav')

	def request_to_server(self, data, http):
		try:
			return requests.post(http, json=data)
		except:
			print('Server Connection Error')

	def save_wav(self, name, data):
		b = os.path.abspath(__file__).replace(os.path.basename(__file__), '')
		with open(f"{b}/audios/{name}.wav", 'wb') as file:
			file.write(data)
			file.close()

	def speach_wav(self, name, data):
		b = os.path.abspath(__file__).replace(os.path.basename(__file__), '')
		with wave.open(f'{b}/audios/{name}.wav', 'rb') as wf:
			FORMAT = self.p.get_format_from_width(wf.getsampwidth())
			CHANNELS = wf.getnchannels()
			RATE = wf.getframerate()
			CHUNK = 1024

			data = wf.readframes(CHUNK)

			stream = self.p.open(format=FORMAT,
							channels=CHANNELS,
							rate=RATE,
							frames_per_buffer=CHUNK,
							output=True)
			while len(data) > 0:
				stream.write(data)
				data = wf.readframes(CHUNK)
			wf.close()