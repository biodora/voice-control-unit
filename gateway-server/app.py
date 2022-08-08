from http.client import OK
from pydantic import BaseModel
from fastapi import FastAPI
from bioreactor_client import BioreactorClient
import yaml

app = FastAPI()
bcs = []
with open(f'./config.yml', 'r', encoding="utf-8") as f: # открываю конфиг выбраного языка
	ip_config = f.read()
	ip_config = yaml.load(ip_config, Loader=yaml.FullLoader)

for i in range(len(ip_config['ip'])):
    bcs.append(BioreactorClient(str(ip_config['ip'][i])))

plc_conn_list = {}
#bc = BioreactorClient(str(ip_config['ip'][0]))

class Auth(BaseModel):
    UID: str
    code: int
    auth_id: int


class Command(BaseModel):
    UID: str
    command_id: int
    action: int
    value: float

class Health(BaseModel):
    check:str

@app.post('/gateaway')
def command(cmd: Command) -> Command:
    if cmd.UID not in plc_conn_list:
        return "Authorization error"
    for b in bcs:
        if b.ip == plc_conn_list[cmd.UID]:
            bc = b
            break
    if cmd.command_id == 0: 
        if cmd.action == 0:
            if bc.write_heater_setpoint(cmd.value):
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 8:
            if bc.write_heater_hysteresis(cmd.value):
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 3:
            data = bc.read_temperature_value()
            return data
        elif cmd.action == 4:
            if bc.set_lat(cmd.value):
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 5:
            if bc.set_lwt(cmd.value):
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 6:
            if bc.set_hat(cmd.value):
                return "OK"
            else:
                return "Connection error"                
        elif cmd.action == 7:
            if bc.set_hwt(cmd.value):
                return "OK"
            else:
                return "Connection error"
    elif cmd.command_id == 1: 
        if cmd.action == 1:
            if bc.write_mixer_start():
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 2:
            if bc.write_mixer_stop():
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 0:
            if bc.write_mixer_setpoint(cmd.value):
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 3:
            data = bc.read_mixer_speed_value()
            return data
    elif cmd.command_id == 2:
        if cmd.action == 3:
            data = bc.read_ph_value()
            return data
        elif cmd.action == 4:
            if bc.set_laph(cmd.value):
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 5:
            if bc.set_lwph(cmd.value):
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 6:
            if bc.set_haph(cmd.value):
                return "OK"
            else:
                return "Connection error"
        elif cmd.action == 7:
            if bc.set_hwph(cmd.value):
                return "OK"
            else:
                return "Connection error"
    elif cmd.command_id == 3:
        return {
            "mixer_status" : bc.mixer_status_text(),
            "ph_status": bc.ph_status_text(),
            "temp_status": bc.temp_status_text()
        }
    else:
        return "Error, command not found. Please try again."

@app.post('/auth')
def auth(auth: Auth) -> Auth:
    if auth.auth_id == 0 :
        for bc in bcs:
            if bc.get_password() == auth.code:
                bc.enter_status_ok()
                plc_conn_list[auth.UID] = bc.ip
                return {'status':'OK'}    
        return ({'status':'Connection error'})
    elif auth.auth_id == 1:
        for bc in bcs:
            if plc_conn_list[auth.UID] == bc.ip: 
                bc.enter_status_error()
                del plc_conn_list[auth.UID]
                return {'status':'OK'}

@app.get("/")
def healthcheck():
    return "Server is stilling alive, arghhhh"
