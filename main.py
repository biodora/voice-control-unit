from ios import IO
from Recognizer import Recognizer

import sys
from datetime import datetime
import hashlib
import random

import yaml
from yaml import Loader

with open('config.yaml', 'r', encoding="utf-8") as f:
	config = f.read()
	config = yaml.load(config, Loader=Loader)

lang = config['lang']
UID = config['UID']
say_server = config['say_server']
gateway_protocol = config['gateway_protocol']
auth_protocol = config['auth_protocol']

UID = hashlib.md5(str(UID).encode()).hexdigest()

last_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
last_time = datetime.timestamp(datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S'))

with open(f'./{lang}/lang.yaml', 'r', encoding="utf-8") as f:
	lang_config = f.read()
	lang_config = yaml.load(lang_config, Loader=yaml.FullLoader)

appIO = IO(UID=UID, say_server=say_server, lang=lang)
appRecognizer = Recognizer(lang_config['name'], f"./{lang}/")
appIO.start_stream()

appIO.say(lang_config['ready message'])

def set_temperature(text):
	global lang_config
	send_command = {}
	value = appRecognizer.find_num(text, lang)
	if value != None:
		words_list = lang_config['set temperature words']
		command_name, _ = appRecognizer.find_word(words_list, text, False)
		try:
			if command_name[-1] in words_list:
				send_command["command_id"] = 0
				send_command["action"] = 0
				send_command["value"] = value
			else:
				return None

		except TypeError:
			return None

		return send_command
	else:
		return None

def sing_in(text=''):
	global UID
	global lang_config
	global authentication
	connect_code_say = ''
	connect_code = ''
	for i in range(4):
		a = random.randint(0, 9)
		connect_code_say += f'{a} '
		connect_code += str(a)
	appIO.say(connect_code_say)
	r = appIO.request_to_server({'UID': UID, 'code': int(connect_code)}, auth_protocol)
	if r.json()['status'] == "OK":
		authentication = True
		appIO.say(lang_config['Signed in'])
	else:
		authentication = False
		appIO.say(lang_config['Failed to login'])
	return -1

def sing_out(text='', mess=True):
	global authentication
	authentication = False
	if mess:
		appIO.say(lang_config['agree message'])
	return -1

def help_commands(text=''):
	global lang_config
	appIO.say(lang_config['help'])
	return -1

commands = [
[lang_config['commands']['temperature'], lang_config['commands']['sign in'], lang_config['commands']['sign out'], lang_config['commands']['help']],
[set_temperature, sing_in, sing_out, help_commands]
]

sing_out('', False)

# with open(f'./{lang}/lang.yaml', 'w', encoding='utf-8') as file:
#     yaml.dump(lang_config, file)

while True:
	data = appIO.get_data()
	text = appRecognizer.speach2text(data)
	if text != None:
		list_commands = commands[0][0] + commands[0][1] + commands[0][2] + commands[0][3]
		command_name, _ = appRecognizer.find_word(list_commands, text)
		print(text)
		if command_name != None:
			for key in range(len(commands[0])):
				if command_name in commands[0][key]:
					if authentication == True:
						response = commands[1][key](text)
						if response == None:
							appIO.say(lang_config['repeat message'])
						elif response == -1:
							pass
						else:
							if response["command_id"] == 0:
								responce_action = lang_config['set temperature message']
							ask = f'{command_name} {responce_action} {response["value"]}, {lang_config["confirmation message"]}'
							appIO.say(ask)
							reply_user = True
							while reply_user:
								data = appIO.get_data()
								text = appRecognizer.speach2text(data)
								if text != None:
									list_commands = lang_config['answ']['agree'] + lang_config['answ']['revocation'] + lang_config['commands']['repeat']
									command_name, _ = appRecognizer.find_word(list_commands, text)
									if command_name != None:
										if command_name in lang_config['answ']['agree']:
											response['UID'] = UID
											request = appIO.request_to_server(response, gateway_protocol)
											if request.ok:
												appIO.say(lang_config['agree message'])
											else:
												print(request.status_code)
											reply_user = False
										elif command_name in lang_config['answ']['revocation']:
											appIO.say(lang_config['revocation message'])
											reply_user = False
										elif command_name in lang_config['commands']['repeat']:
											appIO.say(ask)
					else:
						if command_name in lang_config['commands']['sign in']:
							sing_in()
						else:
							appIO.say(lang_config['sign in message'])

	else:
		now_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
		now_time = datetime.timestamp(datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S'))

		if (now_time - last_time) >= config['poll rate']:
			last_time = now_time
			request = {'command_id':4, 'action':0, 'value':0, 'UID': UID}
			r = appIO.request_to_server(request, gateway_protocol)
			if not(r.ok):
				print(r.text)