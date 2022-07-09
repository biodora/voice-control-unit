from vosk import Model, KaldiRecognizer
import os, json, sys
import pyaudio
import pyttsx3
import time

model = Model(".")
rec = KaldiRecognizer(model, 44100) # Обычный 8000, а маленький 44100
p = pyaudio.PyAudio()
stream = p.open(
	format=pyaudio.paInt16, 
	channels=1, 
	rate=44100, 
	input=True, 
	frames_per_buffer=44100,
	input_device_index=1
)

engine = pyttsx3.init()

def execute_command_with_name(command_name: str, *args: list):
	for key in commands.keys():
		if command_name in key:
			try:
				commands[key](*args)
			except:
				commands[key]()

def TextToSpeech(text):
	global engine
	engine.say(text)
	engine.runAndWait()

	#pyttsx3.speak("Говорить в одну строку со стандартными параметрами")

# Функции команд
def Exit():
	sys.exit(0)

def Device():
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	for i in range(0, numdevices):
			if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
				print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

def Selcect_Device(args):
	digits = {'ноль': 0, 'один': 1, 'два': 2, 'три': 3, 'четыре': 4}

	global stream
	stream.stop_stream()

	stream = p.open(
	format=pyaudio.paInt16, 
	channels=1, 
	rate=44100, 
	input=True, 
	frames_per_buffer=44100,
	input_device_index=digits.get(args[0])
	)

	TextToSpeech("Выбран микрофон с индексом " + str(digits.get(args[0])))

	stream.start_stream()

def Say_Text(args):
	TextToSpeech(' '.join(args))
# Команды
commands = {
	("выход", "стоп"): Exit,
	("девайс", "микрофон", "девайсы", "микрофоны"): Device,
	("выбрать", "выбор"): Selcect_Device,
	("скажи"): Say_Text,
}

Alias = "королева"

# Старт
pyttsx3.speak("Голосовой ассистент запущен")
stream.start_stream()

while True:
	data = stream.read(4000, exception_on_overflow=False)
	if len(data) == 0:
		break
	if rec.AcceptWaveform(data):
		x=json.loads(rec.Result())
		if x["text"] != "":
			voice_input = x["text"]
			voice_input = voice_input.split(" ")

			if voice_input.index('да') != -1:
				voice_input = voice_input[voice_input.index('да')+1:]

				print(' '.join(voice_input))

				command = voice_input[0]
				command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]

				execute_command_with_name(command, command_options)