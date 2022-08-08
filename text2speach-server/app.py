from fastapi import FastAPI
from pydantic import BaseModel
import os
import time

app = FastAPI()

class text_format(BaseModel):
	text: str
	UID: str
	lang: str

def text2speach(text, id_client, voice):
	b = os.path.abspath(__file__).replace(os.path.basename(__file__), '')
	os.system(f'echo «{text}» | LD_LIBRARY_PATH=/usr/local/lib RHVoice-test -o "{b}audios/{id_client}.wav" -p {voice}')
	time.sleep(0.3)
	with open(f'{b}audios/{id_client}.wav', 'rb') as file:
		data = file.read()
	file.close()
	os.remove(f'{b}audios/{id_client}.wav')
	return {'data': data.hex()}

@app.post("/")
async def get_text(text_data: text_format):
	lang = text_data.lang
	if lang == 'ru':
		responce = text2speach(text_data.text, text_data.UID, 'tatiana')
	elif lang == 'en':
		responce = text2speach(text_data.text, text_data.UID, 'Alan')
	return responce

@app.get("/")
def healthcheck():
    return "Server is stilling alive, arghhhh"