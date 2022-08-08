FROM python:latest

###build
### docker build --tag "gateway-server:1.3.1" .

###run
### docker run -itd --rm --name "gateway-server" -p 8000:8000 gateway-server:1.3.1

#Python packages installation
COPY ./requirements.txt ./requirements.txt
COPY ./config.yml ./config.yml
RUN pip install -r requirements.txt

#Application copy
COPY ./app.py .
COPY ./bioreactor_client.py .
COPY ./utils.py .

#Server run
EXPOSE 8000
CMD ["uvicorn", "app:app", "--reload", "--host" , "0.0.0.0", "--port", "8000"]