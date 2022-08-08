FROM python:latest

RUN apt-get update
RUN apt-get install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y
COPY ./pips.txt ./pips.txt
RUN pip install -r pips.txt

COPY /audios /audios
COPY ./config.ini   ./config.ini
COPY ./ios ./ios
COPY ./main.py ./main.py
COPY ./Recognizer.py ./Recognizer.py
COPY /RNNoise_Wrapper /RNNoise_Wrapper
COPY /ru /ru

CMD [ "python", "./test.py" ]