from machine import I2C, Pin
import time
import ustruct


# 三轴传感器
class MSA301():
    def __init__(self, i2cs=None, sda=21, scl=22):
        if i2cs == None:
            self.i2cxy = I2C(scl=Pin(scl), sda=Pin(sda), freq=400000)
            print(self.i2cxy.scan())
        else:
            self.i2cxy = i2cs
        self.addr = 38

        self.i2cxy.writeto(self.addr, b'\x0F\x08')
        self.i2cxy.writeto(self.addr, b'\x11\x00')

    def get_x(self):
        retry = 0
        if (retry < 5):
            try:
                self.i2cxy.writeto(self.addr, b'\x02', False)
                buf = self.i2cxy.readfrom(self.addr, 2)
                x = ustruct.unpack('h', buf)[0]
                return x / 4 / 4096
            except:
                retry = retry + 1
        else:
            raise Exception("i2c read/write error!")

    def get_y(self):
        retry = 0
        if (retry < 5):
            try:
                self.i2cxy.writeto(self.addr, b'\x04', False)
                buf = self.i2cxy.readfrom(self.addr, 2)
                y = ustruct.unpack('h', buf)[0]
                return y / 4 / 4096
            except:
                retry = retry + 1
        else:
            raise Exception("i2c read/write error!")

    def get_z(self):
        retry = 0
        if (retry < 5):
            try:
                self.i2cxy.writeto(self.addr, b'\x06', False)
                buf = self.i2cxy.readfrom(self.addr, 2)
                z = ustruct.unpack('h', buf)[0]
                return z / 4 / 4096
            except:
                retry = retry + 1
        else:
            raise Exception("i2c read/write error!")
