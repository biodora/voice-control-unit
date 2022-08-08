FROM python:latest

###build
### docker build --tag "text2speach-server:1.0" .

###run
### docker run -itd --rm --name "text2speach-server" -p 8080:8080 --mount type=bind,source="$(pwd)"/audios,target=/audios text2speach-server:1.0

#Python packages installation
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

#RHVoice installation
RUN apt-get update && apt-get install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y
RUN git clone --recursive https://github.com/RHVoice/RHVoice.git
RUN cd RHVoice && scons languages=Russian,English && scons install && cd ../ && rm -rf RHVoice

#Application copy
COPY ./app.py .

#Server run
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]