import time
from machine import Pin,I2C

# 使用的传感器为AHT20，程序仅为测试使用，仅读取关键传感器数值。

class AHT20():

    def __init__(self,I2Cd=None,SDA=21,SCL=22):
    
        if I2Cd == None:
            self.i2c = I2C(scl = Pin(SCL), sda = Pin(SDA), freq = 200000)
        else:
            self.i2c = I2Cd
        
        self.address = 56  # 传感器默认地址
        self.i2c.writeto_mem(self.address, 0xee, b'\x80\x00')
        
    def getTemperature(self):
        self.i2c.writeto_mem(self.address, 0xac, b'\x33\x00')
        time.sleep_ms(200)
        byte = self.i2c.readfrom_mem(self.address, 0, 6)
        temp = byte[3] * 65535 + byte[4] * 255 + byte[5] & ~(0xfff00000)
        return (((temp)/1048576)*200-50)
        
    def getHumidity(self):
        self.i2c.writeto_mem(self.address, 0xac, b'\x33\x00')
        time.sleep_ms(200)
        byte = self.i2c.readfrom_mem(self.address, 0, 6)
        hum = byte[1] * 65535 + byte[2] * 255 + byte[3]
        return (((hum/16)/1048576)*100)
        
    def getTemperatureandHumidity(self):
        self.i2c.writeto_mem(self.address, 0xac, b'\x33\x00')
        time.sleep_ms(200)
        byte = self.i2c.readfrom_mem(self.address, 0, 6)
        hum = byte[1] * 65535 + byte[2] * 255 + byte[3]
        temp = byte[3] * 65535 + byte[4] * 255 + byte[5] & ~(0xfff00000)
        return ((((temp)/1048576)*200-50),(((hum/16)/1048576)*100))
