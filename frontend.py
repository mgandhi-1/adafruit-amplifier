import midas
import midas.frontend
import midas.event
import time
import board 
import busio
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_mcp9600 import MCP9600

class MyPeriodicEquipment(midas.frontend.EquipmentBase):
    
    def __init__(self, client):
        equip_name = "MyPeriodicEquipment"
        default_common = midas.frontend.InitialEquipmentCommon()
        default_common.equip_type = midas.EQ_PERIODIC
        default_common.buffer_name = "SYSTEM"
        default_common.trigger_mask = 0
        default_common.event_id = 1
        default_common.period_ms =  1000
        default_common.read_when = midas.RO_RUNNING
        default_common.log_history = 1

        midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common)

        self.set_status("Initialized")
    
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA, frequency=200000)
            self.device = MCP9600(self.i2c)
            self.set_status("Sensor detected, ready.")
        except ValueError:
            self.device = None
            self.set_status('Sensor not detected')
        
        # Buffers to store 100 temperature values
        self.ambient_buffer = []
        self.hot_buffer = []
        self.delta_buffer = []

    def readout_func(self):
        if self.device is None:
            return None
        
        ambient_temp = self.device.ambient_temperature
        hot_temp = self.device.temperature
        delta_temp = self.device.delta_temperature
        
        self.ambient_buffer.append(ambient_temp)
        self.hot_buffer.append(hot_temp)
        self.delta_buffer.append(delta_temp)
        
        print(ambient_temp, hot_temp, delta_temp)
        
        if len(self.ambient_buffer) < 100:
            return None
        
        event = midas.event.Event()
        
        event.create_bank('AMBT', midas.TID_FLOAT, self.ambient_buffer)
        event.create_bank('HOTJ', midas.TID_FLOAT, self.hot_buffer)
        event.create_bank('DTMP', midas.TID_FLOAT, self.delta_buffer)
        
        self.ambient_buffer = []
        self.hot_buffer = []
        self.delta_buffer = []
    
        return event

class MyFrontend(midas.frontend.FrontendBase):
    def __init__(self):
        midas.frontend.FrontendBase.__init__(self, 'myfe_name')
        self.add_equipment(MyPeriodicEquipment(self.client))
    
    def begin_of_run(self, run_number):
        self.set_all_equipment_status('Running', 'greenLight')
        self.client.msg('Frontend has seen start of run number %d' % run_number)
        return midas.status_codes['SUCCESS']
    
    def end_of_run(self, run_number):
        self.set_all_equipment_status('Finished', 'greenLight')
        self.client.msg('Frontend has seen end of run number %d' % run_number)
        return midas.status_codes['SUCCESS']
    
    def frontend_exit(self):
        print('Exiting Frontend ...')
        
if __name__ == '__main__':
    with MyFrontend() as my_fe:
        my_fe.run()
