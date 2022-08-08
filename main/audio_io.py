import pyaudio	# working with a microphone
import requests	# sending/receiving data to the server
import wave		# work with audio stream
import os		# to delete unwanted audio files

class AudioInputOutput(object):
	def __init__(self, **kwargs): # accept all parameters and set them to variables
		"""
			kwargs:
			input_device_index (int): set up microphone
			UID (str): User ID
			say_server (str): IP server for "text to speech"
			lang (str): lang (ru, en ...)

		"""				
		self.pa = pyaudio.PyAudio()

		if 'input_device_index' in kwargs.keys():
			self.__open_stream(kwargs['input_device_index'])
		else:
			self.__open_stream(self.pa.get_default_input_device_info()['index'])

		if 'UID' in kwargs.keys():
			self.UID = kwargs['UID']

		if 'say_server' in kwargs.keys():
			self.say_server = kwargs['say_server']

		if 'lang' in kwargs.keys():
			self.lang = kwargs['lang']

	def get_data(self): # I give out data from the microphone
		data = self.stream.read(4000, exception_on_overflow=False)
		return data

	def start_stream(self):
		self.stream.start_stream()

	def stop_stream(self):
		self.stream.stop_stream()

	def __open_stream(self, input_device_index:int): # I open the stream with the microphone installed
		mic_info = self.pa.get_device_info_by_index(input_device_index)['defaultSampleRate']

		self.stream = self.pa.open(
			format=pyaudio.paInt16,
			channels=1,
			rate=int(mic_info),
			input=True,
			input_device_index=input_device_index
		)

	def get_microphones(self): # give out a list of microphones
		""" returns a dictionary of microphones available for connection.

		Returns:
			dictionary: id:name | id is the id of the microphone, which is specified in __init__ and selcect_device
		"""	
		info = self.pa.get_host_api_info_by_index(0)
		num_devices = info.get('deviceCount')

		devices = {}

		for i in range(0, num_devices):
			if (self.pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
				devices[i] = self.pa.get_device_info_by_host_api_device_index(0, i).get('name')

		return devices

	def selcect_device(self, id:int=None): # I close the stream, after which I set the microphone by id
		self.stream.stop_stream()
		self.stream.close()
		if id is None:
			self.__open_stream(self.pa.get_default_input_device_info()['index'])
		else:
			self.__open_stream(id)

	def	close_stream(self):
		self.stream.close()
	
	def stream_is_active(self):
		return self.stream.is_active()

	def say(self, text:str):
		""" Text voice acting

		Args:
			text (str): the text to be spoken.
		"""		
		r = self.request_to_server({'text': text, 'UID': self.UID, 'lang': self.lang}, self.say_server)

		if r != None:
			data = bytes.fromhex(r.json()['data'])  # data (byte) to HEX

			name = 'speach'
			self.save_wav(name, data)
			self.play_wav(name, data)
			os.remove(f'./audios/speach.wav')

	def request_to_server(self, data, http:str): # return request result
		try:
			return requests.post(http, json=data)
		except:
			print('Server Connection Error')

	def save_wav(self, name:str, data:bytes): # I save an array of bytes (data) in an audio .wav file
		""" saves an audio file in the "audios" folder with a specific name

		Args:
			name (str): name for future .wav audio file
			data (bytes): audio stream bytes
		"""		
		b = os.path.abspath(__file__).replace(os.path.basename(__file__), '')
		with open(f"{b}/audios/{name}.wav", 'wb') as file:
			file.write(data)
			file.close()

	def play_wav(self, name:str, data:bytes):
		""" *.wav audio file playback

		Args:
			name (str): .wav audio file name | in the "audios" folder
			data (bytes): audio stream bytes
		"""		
		b = os.path.abspath(__file__).replace(os.path.basename(__file__), '')
		with wave.open(f'{b}/audios/{name}.wav', 'rb') as wf:
			FORMAT = self.pa.get_format_from_width(wf.getsampwidth())
			CHANNELS = wf.getnchannels()
			RATE = wf.getframerate()
			CHUNK = 1024

			data = wf.readframes(CHUNK)

			pa = pyaudio.PyAudio()
			stream = pa.open(format=FORMAT,
							channels=CHANNELS,
							rate=RATE,
							frames_per_buffer=CHUNK,
							output=True)
			while len(data) > 0:
				stream.write(data)
				data = wf.readframes(CHUNK)
			wf.close()
			stream.close()
	