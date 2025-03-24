import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_mcp9600 import MCP9600

i2c = busio.I2C(board.SCL, board.SDA, frequency=200000)

try:
	device = MCP9600(i2c)
	print("Version: ", device.version)
	while True:
		print ((device.ambient_temperature, device.temperature))
		time.sleep(1)
except ValueError:
	print("MCP9600 sensor not detected")



