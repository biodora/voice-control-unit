from pyModbusTCP.client import ModbusClient
from utils import two_int_to_float, float_to_two_int

class BioreactorClient:
    def __init__(self, ip) -> None:
        self.ip = str(ip)
        self.__mb_client = ModbusClient(host=self.ip, port=502,unit_id=0, timeout=1.0, debug=False, auto_open=True)

    def get_password(self):
        password = self.__mb_client.read_input_registers(18, 1)
        if password:
            return password[0]
        else:
            return None

    def enter_status_ok(self):
        value = [1]
        return self.__mb_client.write_multiple_registers(27, value)        
    
    def enter_status_error(self):
        value = [2]
        return self.__mb_client.write_multiple_registers(27, value)      

    def read_temperature_value(self):
        data = self.__mb_client.read_input_registers(0, 2)
        return two_int_to_float(data)

    def read_temperature_status(self):
        data = self.__mb_client.read_input_registers(4, 1)
        if data:
            return data[0]
        else:
            return None

    def read_ph_value(self):
        data = self.__mb_client.read_input_registers(2, 2)
        return two_int_to_float(data)

    def read_ph_status(self):
        data = self.__mb_client.read_input_registers(5, 1)
        if data:
            return data[0]
        else:
            return None

    def read_heater_status(self):
        data = self.__mb_client.read_input_registers(14, 1)
        if data:
            return data[0]
        else:
            return None

    def write_heater_setpoint(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(22, value)

    def write_heater_hysteresis(self, hysteresis):
        value = float_to_two_int(hysteresis)
        return self.__mb_client.write_multiple_registers(24, value)

    def read_mixer_speed_value(self):
        data = self.__mb_client.read_input_registers(8, 2)
        return two_int_to_float(data)

    def read_mixer_status(self):
        data = self.__mb_client.read_input_registers(10, 1)
        if data:
            return data[0]
        else:
            return None

    def write_mixer_start(self):
        value = [1]
        return self.__mb_client.write_multiple_registers(16, value)
    
    def write_mixer_stop(self):
        value = [2]
        return self.__mb_client.write_multiple_registers(16, value)

    def write_mixer_setpoint(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(17, value)
    
    def set_hwt(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(0, value)
    
    def set_hat(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(2, value)

    def set_lat(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(4, value)
    
    def set_lwt(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(6, value)

    def set_hwph(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(8, value)
    
    def set_haph(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(10, value)

    def set_lwph(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(14, value)
    
    def set_laph(self, setpoint):
        value = float_to_two_int(setpoint)
        return self.__mb_client.write_multiple_registers(12, value)
        
    def ph_status_text(self):
        ph = self.read_ph_status()   
        return ph    
    
    def temp_status_text(self):
        temp = self.read_temperature_status()
        return temp

    def mixer_status_text(self):
        mixer = self.read_mixer_status()
        return mixer


        