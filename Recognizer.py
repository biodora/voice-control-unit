from vosk import Model, KaldiRecognizer
import os, json, sys
from fuzzywuzzy import process
from fuzzywuzzy import utils
from text_to_num import text2num

class Recognizer(object):
	accepted = False

	def __init__(self, keyWord="", path="."):
		self.set_settings(keyWord, path)

	def set_settings(self, keyWord, path):
		model = Model(path)
		self.rec = KaldiRecognizer(model, 44100) # Обычный 8000, а маленький 44100
		self.keyWord = keyWord

	def speach2text(self, data):
		self.accepted = False
		if self.rec.AcceptWaveform(data):
			self.accepted = True
			voice_input=json.loads(self.rec.Result())
			if voice_input["text"] != "":
				text = voice_input["text"]
				if self.keyWord != "" and self.keyWord != None:
					if text.find(self.keyWord) != -1:
						return text[text.find(self.keyWord)+len(self.keyWord)+1:]
				else:
					return text

	def find_word(self, commands, text, one_word=True):
		for i in commands:
			j = i
			text.replace(i, j.replace(' ', ''))

		textList = text.split(" ")
		bestWord= ""
		word_index = -1
		MaxConsilience = 0
		s_indexs = []
		s_words = []
		for i in range(len(textList)):
			if utils.full_process(textList[i]):
				a, b = process.extractOne(textList[i], commands)
				if b > MaxConsilience:
					s_words = []
					s_indexs = []
					MaxConsilience = b
					bestWord = a
					word_index = i
					s_words.append(a)
					s_indexs.append(i)
				elif b == MaxConsilience:
					s_words.append(a)
					s_indexs.append(i)

		if len(bestWord) > 2:
			testWord = bestWord[:len(bestWord)//2]
		else:
			testWord = bestWord

		if text.find(testWord) != -1 and word_index != -1:
			if len(s_words) >1:
				if one_word:
					return (s_words[0], s_indexs[0])
				else:
					return (s_words, s_indexs)
			else:
				if one_word:
					return (bestWord, word_index)
				else:
					return ([bestWord], [word_index])
		else:
			return (None, None)

	def find_num(self, text, lang):
		text_list = text.split(" ")
		end_one = False
		end_two = False
		s1 = []
		s2 = []
		for i in text_list:
			try:
				text2num(i, lang)
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
						text2num(i_whith_last, lang)
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
			s1 = text2num(' '.join(s1), lang)
			s2 = text2num(' '.join(s2), lang)
			s = float(f'{s1}.{s2}')
			return s
		except ValueError:
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