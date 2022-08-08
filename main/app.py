from audio_io import AudioInputOutput
from recognizer import Recognizer

from datetime import datetime
import random
import logging
from logging.handlers import RotatingFileHandler
import os
from uuid import getnode
import traceback

import yaml
import configparser

try:
	log_file_name = 'log_records.csv'

	configs = configparser.ConfigParser() # Открытие config файла
	configs.read('config.ini', encoding ="utf8")
	config = configs['config']

	lang = str(config['lang']) # Устанавливаю все нужные параметры из конфига
	UID = str(getnode())
	text2speach_url = str(config['text2speach_url'])
	gateway_url = str(config['gateway_url'])
	auth_url = str(config['auth_url'])
	poll_rate = float(config['poll_rate'])
	connect_code = ''

	if not(os.path.exists(log_file_name)):
		with open(log_file_name, 'a+', encoding='utf-8') as f:
			f.write('timestamp,user,status,"text"\n')

	logging.basicConfig(handlers=[RotatingFileHandler(filename=log_file_name, encoding='utf-8', mode='a+', maxBytes=1100000, backupCount=2)],
						format=f'%(asctime)s,{UID},%(levelname)s,"%(message)s"', 
						datefmt="%F %T", 
						level=logging.DEBUG)

	logging.info('setting start time')

	last_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') # Начинаю отсчёт времени (для диагностики)
	last_time = datetime.timestamp(datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S'))
	last_time_device = last_time

	logging.info('opening lang config')

	with open(f'./{lang}/lang.yaml', 'r', encoding="utf-8") as f: # открываю конфиг выбраного языка
		lang_config = f.read()
		lang_config = yaml.load(lang_config, Loader=yaml.FullLoader)

	logging.info('initing appIO')

	appIO = AudioInputOutput(UID=UID, say_server=text2speach_url, lang=lang) # инициализирую нужные классы
	appRecognizer = Recognizer(lang_config['name'], f"./{lang}/")
	appIO.start_stream() # Начинаю работу с микрофона

	logging.info('speeching ready message')
	appIO.say(lang_config['ready message']) # Озвучиваю начало работы голосового ассистента
	
except Exception:
	logging.critical(traceback.format_exc().replace('"', '\''))
	r = appIO.request_to_server({'UID': UID, 'code': 0, 'auth_id': 1}, auth_url)

def lang_swith(text):
	logging.info('starting lang swith command')
	global lang_config
	global appRecognizer
	words_list = []

	logging.info('lang list generating')
	for langs in lang_config['langs']:
		words_list.append(lang_config['langs'].get(langs))

	logging.info('searching key word')
	command_name, _ = appRecognizer.find_word(words_list, text, True) # получаю ключевое слово

	logging.info('selecting lang')
	for i in lang_config['langs']:
		if command_name == lang_config['langs'].get(i):
			global config
			logging.info('found lang')

			logging.info('rewriting config')
			global configs
			configs['config']['lang'] = i	# дальше я просто перезаписываю нужные данные
			global lang
			lang = i

			with open('config.ini', 'w', encoding ="utf8") as configfile:
				configs.write(configfile)
			
			with open(f'./{lang}/lang.yaml', 'r', encoding="utf-8") as f: # открываю конфиг выбраного языка
				lang_config = f.read()
			lang_config = yaml.load(lang_config, Loader=yaml.FullLoader)

			logging.info('opening config file')
			configs = configparser.ConfigParser() # Открытие config файла
			configs.read('config.ini', encoding ="utf8")
			config = configs['config']

			global UID
			global text2speach_url
			global gateway_url
			global auth_url
			global poll_rate
			
			logging.info('setuping config')
			UID = UID
			text2speach_url = str(config['text2speach_url'])
			gateway_url = str(config['gateway_url'])
			auth_url = str(config['auth_url'])
			poll_rate = float(config['poll_rate'])

			logging.info('setup recongnizer lang')

			global appIO

			appIO.close_stream()
			appIO = AudioInputOutput(UID=UID, say_server=text2speach_url, lang=lang)
			appRecognizer = Recognizer(lang_config['name'], f"./{lang}/")

			appIO.start_stream()

			logging.info('say ready message')
			appIO.say(lang_config['ready message'])
			
			return (-1, '')
	return (None, '')

def set_temperature(text):
	logging.info('starting temperature command')
	global lang_config
	global send_command
	send_command = {}
	logging.info('searching num')
	value = appRecognizer.find_num(text, lang)

	logging.info('searching key word set_settings')
	command_name, _ = appRecognizer.find_word(lang_config['min words'] + lang_config['max words'], text, False, True)
	if command_name != None and command_name[-1] in (lang_config['min words'] + lang_config['max words']):
		return set_setting(text)

	logging.info('searching key word')
	words_list = lang_config['dead zone'] + lang_config['set words'] + lang_config['value words']
	command_name, _ = appRecognizer.find_word(words_list, text, False)
	logging.info('selection of conditions')
	try:
		if command_name[-1] in lang_config['dead zone'] and value != None:
			send_command["command_id"] = 0
			send_command["action"] = 8
			send_command["value"] = value
			ask = f'{lang_config["temperature message"]} {lang_config["dead zone message"]} {lang_config["set message"]}, {lang_config["confirmation message"]}'

		elif command_name[-1] in lang_config['value words']:
			send_command["command_id"] = 0
			send_command["action"] = 3
			send_command["value"] = value
			ask = f'{lang_config["temperature message"]} {lang_config["value message"]}, {lang_config["confirmation message"]}'

		elif value != None or (command_name[-1] in lang_config['set words'] and value != None):
			send_command["command_id"] = 0
			send_command["action"] = 0
			send_command["value"] = value
			response_value = str(value).replace('.', f' {lang_config["and message"]} ')
			ask = f'{lang_config["temperature message"]} {lang_config["set message"]} {response_value}, {lang_config["confirmation message"]}'

		else:
			logging.info('no suitable condition')
			return (None, '')

	except TypeError:
		logging.error(traceback.format_exc().replace('"', '\''))
		return (None, '')

	return (send_command, ask)

def	set_setting(text):
	logging.info('starting set settings command')
	global lang_config
	global send_command
	send_command = {}
	ask = ''

	logging.info('searching num')
	value = appRecognizer.find_num(text, lang)

	if value != None:
		logging.info('searching threshold_value')
		words_list = lang_config['min words'] + lang_config['max words']
		threshold_value, _ = appRecognizer.find_word(words_list, text, True)

		logging.info('searching status_value')
		words_list = lang_config['warning words'] + lang_config['emergency words']
		status_value, _ = appRecognizer.find_word(words_list, text, True)

		logging.info('creating response_value')
		response_value = str(value).replace('.', f' {lang_config["and message"]} ')

		logging.info('searching operation')
		words_list = lang_config['commands']['temperature'] + lang_config['commands']['pH']
		operation, _ = appRecognizer.find_word(words_list, text, True)

		if operation in lang_config['commands']['temperature']:
			CID = 0
		elif operation in lang_config['commands']['pH']:
			CID = 2
		else:
			return (None, '')

		logging.info('selection of conditions')
		if threshold_value in lang_config['min words']:
			if status_value in lang_config['warning words']:
				send_command["command_id"] = CID
				send_command["action"] = 4
				send_command["value"] = value
				ask = f"{operation} {lang_config['min message']} {lang_config['warning message']} {lang_config['setting message']} {response_value}, {lang_config['confirmation message']}"
			elif status_value in lang_config['emergency words']:
				send_command["command_id"] = CID
				send_command["action"] = 5
				send_command["value"] = value
				ask = f"{operation} {lang_config['min message']} {lang_config['emergency message']} {lang_config['setting message']} {response_value}, {lang_config['confirmation message']}"
			else:
				return (None, '')
		
		elif threshold_value in lang_config['max words']:
			ask += lang_config['max message']
			if status_value in lang_config['warning words']:
				send_command["command_id"] = CID
				send_command["action"] = 6
				send_command["value"] = value
				ask = f"{operation} {lang_config['max message']} {lang_config['warning message']} {lang_config['setting message']} {response_value}, {lang_config['confirmation message']}"
			elif status_value in lang_config['emergency words']:
				send_command["command_id"] = CID
				send_command["action"] = 7
				send_command["value"] = value
				ask = f"{operation} {lang_config['max message']} {lang_config['emergency message']} {lang_config['setting message']} {response_value}, {lang_config['confirmation message']}"
			else:
				return (None, '')
		else:
			logging.info('no suitable condition')
			return (None, '')
		
		return (send_command, ask)
	
	else:
		return(None, '')

def mixer(text):
	logging.info('starting mixer command')
	global lang_config
	global send_command
	send_command = {}
	logging.info('searching num')
	value = appRecognizer.find_num(text, lang)

	logging.info('serching key word')
	words_list = lang_config['set words'] + lang_config['turn on words'] + lang_config['turn off words'] + lang_config['value words']
	command_name, _ = appRecognizer.find_word(words_list, text, False)
	try:
		logging.info('selection of conditions')
		if value != None or (command_name[-1] in lang_config['set words'] and value != None): 
			send_command["command_id"] = 1
			send_command["action"] = 0
			send_command["value"] = value
			response_value = str(value).replace('.', f' {lang_config["and message"]} ')
			ask = f'{lang_config["mixer message"]} {lang_config["set message"]} {response_value}, {lang_config["confirmation message"]}'

		elif command_name[-1] in lang_config['turn on words']:
			send_command["command_id"] = 1
			send_command["action"] = 1
			send_command["value"] = value
			ask = f'{lang_config["mixer message"]} {lang_config["turn on message"]}, {lang_config["confirmation message"]}'

		elif command_name[-1] in lang_config['turn off words']:
			send_command["command_id"] = 1
			send_command["action"] = 2
			send_command["value"] = value
			ask = f'{lang_config["mixer message"]} {lang_config["turn off message"]}, {lang_config["confirmation message"]}'

		elif command_name[-1] in lang_config['value words']:
			send_command["command_id"] = 1
			send_command["action"] = 3
			send_command["value"] = value
			ask = f'{lang_config["mixer message"]} {lang_config["value message"]} {lang_config["mixer speed message"]}, {lang_config["confirmation message"]}'
		
		else:
			logging.info('no suitable condition')
			return (None, '')

	except TypeError:
		logging.error(traceback.format_exc().replace('"', '\''))
		return (None, '')

	return (send_command, ask)

def pH(text):
	logging.info('starting ph command')
	global lang_config
	global send_command
	send_command = {}

	logging.info('searching num')
	value = appRecognizer.find_num(text, lang)

	logging.info('searching key word set_settings')
	command_name, _ = appRecognizer.find_word(lang_config['min words'] + lang_config['max words'], text, False, True)
	if command_name != None and command_name[-1] in (lang_config['min words'] + lang_config['max words']):
		return set_setting(text)
	
	logging.info('searching key word')
	words_list = lang_config['set words'] + lang_config['turn on words'] + lang_config['turn off words'] + lang_config['value words']
	command_name, _ = appRecognizer.find_word(words_list, text, False)
	try:
		logging.info('selection of conditions')
		if command_name[-1] in lang_config['value words']:
			send_command["command_id"] = 2
			send_command["action"] = 3
			send_command["value"] = value
			ask = f'{lang_config["pH message"]} {lang_config["value message"]}, {lang_config["confirmation message"]}'
		
		elif value != None or (command_name[-1] in lang_config['set words'] and value != None):
			send_command["command_id"] = 2
			send_command["action"] = 0
			send_command["value"] = value
			response_value = str(value).replace('.', f' {lang_config["and message"]} ')
			ask = f'{lang_config["pH message"]} {lang_config["set message"]} {response_value}, {lang_config["confirmation message"]}'
		
		else:
			logging.info('no suitable condition')
			return (None, '')

	except TypeError:
		logging.error(traceback.format_exc().replace('"', '\''))
		return (None, '')

	return (send_command, ask)

def sing_in(text=''):
	logging.info('starting sing in command')
	global UID
	global lang_config
	global authentication
	global connect_code

	if authentication == False and connect_code == '':
		return code()

	#authentication = True
	if connect_code != '':
		if authentication != True:
			logging.info('send auth request')
			r = appIO.request_to_server({'UID': UID, 'code': int(connect_code), 'auth_id': 0}, auth_url)

			if r.json()['status'] == "OK":
				authentication = True
				logging.info('sing in successfully')
				appIO.say(lang_config['Signed in'])
			else:
				authentication = False
				logging.info('sing in unsuccessfully')
				appIO.say(lang_config['Failed to sign in'])

			return (-1, '')
		else:
			return (-1, '')
	else:
		logging.info('need to generate code')
		appIO.say(lang_config['please generate code message'])
		return (-1, '')

def sing_out(text='', mess=True):
	logging.info('starting sing out command')
	global authentication
	global connect_code

	logging.info('send sing out request')
	r = appIO.request_to_server({'UID': UID, 'code': 0, 'auth_id': 1}, auth_url)
	if r.json()['status'] == "OK":
		connect_code = ''
		authentication = False
		logging.info('sing in successfully')
		if mess:
			appIO.say(lang_config['exit message'])

	else:
		logging.info('sing in unsuccessfully')
		appIO.say(lang_config['Failed to sing out'])
	return (-1, '')

def help_commands(text=''):
	logging.info('starting help command')
	global lang_config
	a = str(lang_config['help']).strip().replace('"', '')

	logging.debug(f'help message - {a}')

	appIO.say(a)
	return (-1, '')

def code(text=''):
	logging.info('starting code command')
	global connect_code
	global authentication
	connect_code_say = ''
	connect_code = ''

	if authentication != True:
		logging.info('generating code')
		for i in range(4):
			a = random.randint(0, 9)
			connect_code_say += f'{a} '
			connect_code += str(a)
		
		logging.info('speeching code')
		appIO.say(connect_code_say)
		return (-1, '')

	else:
		return (-1, '')

def pH_calibration(text):
	logging.info('starting pH calibration command')
	appIO.say(lang_config['agree message'])
	return (-1, '')

def dead_zone(text):
	logging.info('starting dead_zone command')
	global lang_config
	global send_command
	send_command = {}

	logging.info('searching key word')
	words_list = [' '] + lang_config['commands']['temperature'] + lang_config['commands']['pH']
	command_name, _ = appRecognizer.find_word(words_list, text, False)

	logging.info('seraching num')
	value = appRecognizer.find_num(text, lang)

	if value != None:
		logging.info('selection of conditions')
		if command_name in lang_config['commands']['temperature']:
			send_command["command_id"] = 0
			send_command["action"] = 8
			send_command["value"] = value
			ask = f'{lang_config["temperature message"]} {lang_config["dead zone message"]} {lang_config["value message"]}, {lang_config["confirmation message"]}'
		else:
			logging.info('no suitable condition')
			return (None, '')
		
		return (send_command, ask)
	else:
		return (None, '')

try:
	logging.info('setuping commands list')
	
	commands = [
	[lang_config['commands']['sign in'], lang_config['commands']['lang'], lang_config['commands']['temperature'], lang_config['commands']['sign out'], lang_config['commands']['help'], lang_config['commands']['mixer'], lang_config['commands']['code'], lang_config['commands']['pH'], lang_config['commands']['calibration']],
	[sing_in, lang_swith, set_temperature, sing_out, help_commands, mixer, code, pH, pH_calibration]
	] # список всех ключевых старт команд ([0]) с их функциями ([1])

	authentication = False # выхожу из системы
	#authentication = True
	logging.info('starting listening')

	while True:
		try:
			data = appIO.get_data() # получаю массив байт с микрофона
		except OSError:
			pass
		
		text = appRecognizer.speech2text(data) # превращяю этот массив в текст
		if text != None:
			list_commands = []
			for cfg in commands[0]: # загружаю все ключевые старт слова комманд в список
				list_commands.extend(cfg)
			command_name, _ = appRecognizer.find_word(list_commands, text, False) # получаю ключевое слово команды
			logging.debug(f'user saw - {text}')
			print(text)
			if command_name != None:
				command_name = command_name[0]
				for key in range(len(commands[0])):
					if command_name in commands[0][key]:
						if authentication == True: # проверяю авторизирован пользователь или нет
							response, ask = commands[1][key](text)

							if response == None:
								appIO.say(lang_config['repeat message']) # если не понял команды, то попросит повторить
							elif response == -1: # на случай, если озвучка к команды не нужна
								pass
							elif response['action'] == 3: # на случай, если подтверждение к команде не требуется
								response['UID'] = UID
								if response['value'] == None:
									response['value'] = -1
									
								logging.debug(f'send command request - {response}')
								request = appIO.request_to_server(response, gateway_url)

								if request.ok:
									logging.debug(request.text)
									if str(request.text).replace('"', '') != 'Connection error' and str(request.text).replace('"', '') != "Authorization error":
										if send_command["action"] == 3:
											if send_command["command_id"] == 0:
												ask = f"{lang_config['temperature message']} {round(float(request.text))}"
												appIO.say(ask.replace('.', f' {lang_config["and message"]} '))
											elif send_command["command_id"] == 1:
												print(request.text)
												ask = f"{lang_config['mixer speed message']} {round(float(request.text))}"
												appIO.say(ask)
											elif send_command["command_id"] == 2:
												ask = f"{lang_config['ph acidity message']} {round(float(request.text))}"
												appIO.say(ask)
									else:
										logging.debug('connection error')
										appIO.say(lang_config["connection error message"])
								else:
									logging.debug(f'Error {request.status_code}')
									appIO.say(f'Error {request.status_code}')
							else:
								appIO.say(ask)
								reply_user = True # переменна, которая означает статус подтверждения команды

								while reply_user:
									data = appIO.get_data()
									text = appRecognizer.speech2text(data)
									if text != None:
										list_commands = lang_config['answ']['agree'] + lang_config['answ']['revocation'] + lang_config['commands']['repeat']
										command_name, _ = appRecognizer.find_word(list_commands, text, True, True)
										logging.debug(f'user saw - {text}')
										print(text)

										if command_name != None:
											if command_name in lang_config['answ']['agree']: # если есть подтверждение
												response['UID'] = UID
												if response['value'] == None:
													response['value'] = -1
												logging.debug(f'send command request - {response}')
												request = appIO.request_to_server(response, gateway_url)
												
												if request.ok:
													logging.debug(request.text)
													if str(request.text).strip('"') == 'OK':
														appIO.say(lang_config['agree message'])
													else:
														logging.debug('connection error')
														appIO.say(lang_config["connection error message"])
												else:
													logging.debug(f'Error {request.status_code}')
													appIO.say(request.status_code)
												reply_user = False
											elif command_name in lang_config['answ']['revocation']:
												appIO.say(lang_config['revocation message'])
												reply_user = False
											elif command_name in lang_config['commands']['repeat']:
												appIO.say(ask)
						else:
							if command_name in lang_config['commands']['sign in']:
								sing_in()
							elif command_name in lang_config['commands']['code']:
								code()
							elif command_name in lang_config['commands']['help']:
								help_commands()
							else:
								appIO.say(lang_config['sign in message'])
		else:
			try:
				now_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
				now_time = datetime.timestamp(datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S'))

				if (now_time - last_time) >= poll_rate:
					last_time = now_time
					if authentication:
						request = {'command_id':3, 'action':-1, 'value':0, 'UID': UID} # вид команы
						r = appIO.request_to_server(request, gateway_url) # посылаю команду для диагностики системы в зависимости от времени (сколько прошло с прошлого раза)
						if not(r.ok):
							logging.error(f'bioreactor diagnostics request - {r.text}')
							appIO.say(r.text)
						else:
							response = r.json()
							logging.debug(f'bioreactor diagnostics request - {response}')
							if type(response) != str:
								if response['mixer_status'] == 0:
									appIO.say(lang_config['mixer device error'])
								elif response['mixer_status'] == 4:
									appIO.say(lang_config['An emergency stop of the mixer'])

								if response['ph_status'] == 0:
									appIO.say(lang_config['ph breakage occurred'])
								elif response['ph_status'] == 2:
									appIO.say(lang_config['ph min_ws'])
								elif response['ph_status'] == 3:
									appIO.say(lang_config['ph min_es'])
								elif response['ph_status'] == 4:
									appIO.say(lang_config['ph max_ws'])
								elif response['ph_status'] == 5:
									appIO.say(lang_config['ph max_es'])
								
								if response['temp_status'] == 0:
									appIO.say(lang_config['temperature breakage occurred'])
								elif response['temp_status'] == 2:
									appIO.say(lang_config['temperature min_ws'])
								elif response['temp_status'] == 3:
									appIO.say(lang_config['temperature min_es'])
								elif response['temp_status'] == 4:
									appIO.say(lang_config['temperature max_ws'])
								elif response['temp_status'] == 5:
									appIO.say(lang_config['temperature max_es'])
				
				elif (now_time - last_time_device) >= 5:
					last_time_device = now_time
					try:
						appIO.selcect_device()
						appIO.start_stream()
					except OSError as error:
						appIO = AudioInputOutput(UID=UID, say_server=text2speach_url, lang=lang)
						logging.debug(f'{error} - connected to new device')
						print(error)
				
			except AttributeError: 
				print('Server conection error')
				logging.error('starting listening')

except KeyboardInterrupt:
	logging.info('Graceful shutdown')
	r = appIO.request_to_server({'UID': UID, 'code': 0, 'auth_id': 1}, auth_url)
	print('Graceful shutdown')

except Exception:
	logging.critical(traceback.format_exc().replace('"', '\''))
	r = appIO.request_to_server({'UID': UID, 'code': 0, 'auth_id': 1}, auth_url)