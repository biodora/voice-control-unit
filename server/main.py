from fastapi import Request, FastAPI
from pydantic import BaseModel
import requests
import os

import time

app = FastAPI()

class text_format(BaseModel):
	text: str
	UID: str
	lang: str

class data_format(BaseModel):
	command_id: int
	action: int
	value: float
	UID: str

class auth_format(BaseModel):
	UID: str
	code: int

def text2speach(text, id_client):
	b = os.path.abspath(__file__).replace(os.path.basename(__file__), '')	
	try:
		os.remove(f'{b}/audios/{id_client}.wav')
	except FileNotFoundError:
		pass
	os.system(f'echo «{text}» | LD_LIBRARY_PATH=/usr/local/lib RHVoice-test -o "{b}audios/{id_client}.wav" -p tatiana')

	with open(f'{b}/audios/{id_client}.wav', 'rb') as file:
		data = file.read()
	file.close()
	os.remove(f'{b}/audios/{id_client}.wav')
	return {'data': data.hex()}

@app.post("/")
async def get_text(text_data: text_format):
	text = text_data.text
	UID = text_data.UID

	responce = text2speach(text, UID)
	return responce

@app.post("/rts")
async def get_data(data: data_format):
	value = data.value
	return value

@app.post("/auth")
async def get_data(auth: auth_format):
	value = auth.code

	time.sleep(1)
	return ({'status':'OK'})