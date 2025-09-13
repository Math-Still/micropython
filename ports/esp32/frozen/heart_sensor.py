import machine
import time

# ==================== 硬件配置定义 ====================
# 所有的硬件定义都封装在此文件中，主程序无需关心。
# 如果您的硬件引脚不同，只需修改这里即可。
DEFAULT_SCL_PIN = 22
DEFAULT_SDA_PIN = 21
DEFAULT_I2C_ADDRESS = 0x57
# ====================================================

class _HeartRateSensor:
    REG_MODE_CONFIG = 0x09
    REG_SPO2_CONFIG = 0x0A
    REG_LED1_PA = 0x0C
    REG_FIFO_DATA = 0x07

    def __init__(self, scl_pin, sda_pin, i2c_addr):
        self.i2c_addr = i2c_addr
        self.i2c = machine.SoftI2C(scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))
        self._setup_sensor()

    def _setup_sensor(self):
        devices = self.i2c.scan()
        if self.i2c_addr not in devices:
            raise OSError("Sensor not found at I2C address: 0x{:02X}".format(self.i2c_addr))

        self.i2c.writeto_mem(self.i2c_addr, self.REG_MODE_CONFIG, bytes([0x03]))
        self.i2c.writeto_mem(self.i2c_addr, self.REG_SPO2_CONFIG, bytes([0x27]))
        self.i2c.writeto_mem(self.i2c_addr, self.REG_LED1_PA, bytes([0x2F]))
        time.sleep_ms(100)

    def read_ir_value(self):
        fifo_data = self.i2c.readfrom_mem(self.i2c_addr, self.REG_FIFO_DATA, 6)
        ir_value = (fifo_data[3] << 16) | (fifo_data[4] << 8) | fifo_data[5]
        return ir_value

    def shutdown(self):
        try:
            self.i2c.writeto_mem(self.i2c_addr, self.REG_MODE_CONFIG, bytes([0x00]))
        except Exception:
            pass


def get_ir_reading():
    sensor_instance = None
    try:
        sensor_instance = _HeartRateSensor(
            scl_pin=DEFAULT_SCL_PIN,
            sda_pin=DEFAULT_SDA_PIN,
            i2c_addr=DEFAULT_I2C_ADDRESS
        )
        heart_tmp = sensor_instance.read_ir_value()
        if heart_tmp < 100.0:
            if heart_tmp > 35.0:
                return 2.0*heart_tmp
            else:
                return 0.0
        else:
            return 0.0

    except Exception as e:
        print("Failed to read sensor:", str(e))
        return None
    finally:
        if sensor_instance:
            sensor_instance.shutdown()