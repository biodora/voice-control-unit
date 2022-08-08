#!/bin/bash
rfkill block bluetooth
rfkill unblock bluetooth
sudo systemctl stop bluetooth.service
sudo systemctl start bluetooth.service

docker run -itd --rm --name "text2speach-server" -p 8080:8080 --mount type=bind,source=/home/pi/Desktop/Projects/va/main/audios,target=/audios text2speach-server:1.1
docker run -itd --rm --name "gateway-server" -p 8000:8000 gateway-server:1.3.1

cd "/home/pi/Desktop/Projects/va/main"
source venv/bin/activate
python3 app.py