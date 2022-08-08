from vosk import Model, KaldiRecognizer	# translate audio to json with text
import json								# to get text from json
from fuzzywuzzy import process			# word match recognition
from fuzzywuzzy import utils
from text_to_num import text2num		# converting numbers from text to float

class Recognizer(object):
	accepted = False

	def __init__(self, key_word:str="", path:str="."):
		"""

		Args:
			key_word (str, list): START word. Defaults to "".
			path (str): path to vosk model. Defaults to ".".
		"""		
		self.set_settings(key_word, path)

	def set_settings(self, key_word:str, path:str):
		""" setup settings

		Args:
			key_word (str): I set the START word. (Sort of like "Ok, google")
			path (str): path to the folder with Vosk voice recognition model
		"""		
		model = Model(path)
		self.rec = KaldiRecognizer(model, 44100) # Regular 8000 | Small 44100
		self.key_word = key_word

	def speech2text(self, data:bytes):
		""" Converts an array of bytes to text

		Args:
			data (bytes): byte array (I personally used it with pyaudio)

		Returns:
			(str): returns the text spoken by the person after the START word, which is specified when the class is initialized. If there is no word START, it returns the entire text without slices.
		"""		
		self.accepted = False
		if self.rec.AcceptWaveform(data): # Accumulate data until ready to process it
			self.accepted = True
			voice_input=json.loads(self.rec.Result()) # we remake the received processed data from a string (of the json type) to json
			if voice_input["text"] != "":
				text = voice_input["text"]
				if self.key_word != "" and self.key_word != None:
					if isinstance(self.key_word, str):
						if text.find(self.key_word) != -1:
							return text[text.find(self.key_word)+len(self.key_word)+1:] # Return text starting with the START word (not inclusive)
					
					elif isinstance(self.key_word, list):
						for word in self.key_word:
							if text.find(word) != -1:
								return text[text.find(word)+len(word)+1:] # Return text starting with the START word (not inclusive)

				else:
					return text

	def find_word(self, commands:list, text:str, one_word:bool=True, second_check:bool=False):
		""" Search for words from "commands" in "text" with the highest match percentage.

		Args:
			commands (List): list of key_words. Among them, the word with the highest percentage of coincidence in the text is selected.
			text (str): Text
			one_word (bool, optional): If True, then return 1 word, and if False, then return a list. Defaults to True.
			second_check (bool, optional): If True, then the 2nd check is in progress (if there is no suitable word in the text, it will return "None"), and if False, then there is no 2nd check of the word (if there are no matches, it will return the first word from the "commands" list). Defaults to False.

		Returns:
			(str or bool): depending on the "one_word" parameter, it will return either a list of the most likely words (from "commands"), or only 1 word.
			If "second_check" is True, it will return "None" if there are no matching words in the text
		"""
		for i in commands: # in case the key_word consists of 2 words, I combine 2 words (if I find them) into 1 (Since I break the text into words next)
			j = i
			text.replace(i, j.replace(' ', ''))

		text_list = text.split(" ") # Breaking text into words
		best_word= ""
		word_index = -1
		max_consilience = 0 # maximum match percentage
		s_indexs = []
		s_words = []
		for i in range(len(text_list)):
			if utils.full_process(text_list[i]):
				a, b = process.extractOne(text_list[i], commands) # a - the word with the maximum match (The word is taken from the commands list). b - is its match percentage.
				if b > max_consilience:
					s_words = []
					s_indexs = []
					max_consilience = b
					best_word = a
					word_index = i
					s_words.append(a)
					s_indexs.append(i)
				elif b == max_consilience:
					s_words.append(a)
					s_indexs.append(i)

		if len(best_word) > 2:
			testWord = best_word[:len(best_word)//2] # I divide the word with the highest match percentage by 2 and then check it against the word I am comparing against.
		else:
			testWord = best_word
		if (second_check and text.find(testWord) != -1 and word_index != -1) or not(second_check): # here it’s shorter depending on the one word parameter, I pass either 1 word or a list of words
			if len(s_words) >1:
				if one_word:
					return (s_words[0], s_indexs[0])
				else:
					return (s_words, s_indexs)
			else:
				if one_word:
					return (best_word, word_index)
				else:
					return ([best_word], [word_index])
		else:
			return (None, None)

	def find_num(self, text:str, lang:str):
		""" Finding digits in text (One, two...) and converting them to floats (1.2)

		Args:
			text (str): Just plain text
			lang (str): Language (en, ru ...): English - en, Russian - ru, Spanish - es, Portuguese - pt, German - de, Catalan - ca.

		Returns:
			[float]: return a floating point digit from text ("Three whole points and six tenths" in 3.6)
		"""				
		text_list = text.split(" ") # I break the text into words, then I go through them
		end_one = False
		end_two = False
		s1 = [] # First I populate this list with words and after the following errors I populate the following list
		s2 = []
		for i in text_list:
			try:
				text2num(i, lang) # if the word is not a digit, then an error occurs. And if not, then we take the word and add it to the list.
				if end_one == False:
					i_whith_last = ' '.join(s1) + ' ' + i
					try:
						text2num(i_whith_last, lang)
						s1.append(i)
					except ValueError:
						s2.append(i)
				elif end_two == False:
					i_whith_last = ' '.join(s2) + ' ' + i
					try:
						text2num(i_whith_last, lang) # I check if the current word is related to the previous one. (234 or 23.4)
					except ValueError:
						s2.append(i)
					s2.append(i)
			except ValueError:
				if len(s1) != 0:
					if end_one == False:
						end_one = True
				if end_two != 0:
					if end_two == False:
						end_two = True
		try:
			if len(s1) > 0:
				s1 = text2num(' '.join(s1), lang) # I turn the words before the dot into text. Then I translate this text into numbers
				s2 = text2num(' '.join(s2), lang) # I turn the words after the dot into text. Then I translate this text into numbers
				s = float(f'{s1}.{s2}') # concatenate everything into a single floating point number
				return s
			else:
				return None
		except ValueError: # In case something goes wrong
			if len(s2) == 0:
				end_one = False
				text_num = ''
				for i in range(len(s1)):
					try:
						text_num += f' {s1[i]}'
						text2num(text_num, lang)
					except ValueError:
						s2 = text2num(' '.join(s1[i::]), lang)
						s1 = text2num(' '.join(s1[:i]), lang)
						s = float(f'{s1}.{s2}')
						return s