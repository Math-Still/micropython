import machine
import ustruct


class I2CInit(object):
    def __init__(self):

        self.i2c_pin_sda = [5, 4, 21, 13]
        self.i2c_pin_scl = [18, 15, 22, 14]

        self.sensor = {87: [0, 0, "max301-血氧"], 80: [0, 0, "AT24c256-eeprom"], 38: [0, 0, "msa301-三轴"],
                       60: [0, 0, "oled-屏幕"], 64: [0, 0, "sht20-温湿度"], 104: [0, 0, "ds3231-时钟模块"],
                       36: [0, 0, "TM1650-四路数码管"], 119: [0, 0, "bmp280-气压传感器"]}

        for i in range(0, len(self.i2c_pin_scl), 1):
            i2c = machine.I2C(scl=machine.Pin(self.i2c_pin_scl[i]), sda=machine.Pin(self.i2c_pin_sda[i]), freq=400000)
            i2cscan = i2c.scan()
            if len(i2cscan) < 5:
                for j in range(0, len(i2cscan), 1):
                    self.sensor[i2cscan[j]][0] = self.i2c_pin_sda[i]
                    self.sensor[i2cscan[j]][1] = self.i2c_pin_scl[i]
                    #
                    # if mmm == 0:
                    #     print("加载成功--" + self.sensor[i2cscan[j]][2] + str(self.sensor[i2cscan[j]][0]) + ":" + str(
                    #         self.sensor[i2cscan[j]][1]))

    def get_sen_i2c(self, add):
        return machine.I2C(scl=machine.Pin(self.sensor[add][1]), sda=machine.Pin(self.sensor[add][0]), freq=400000)

    def get_sen_pin(self, add):
        return self.sensor[add][0], self.sensor[add][1]


# 科创板按钮
class Button(object):
    def __init__(self):
        self.adc36 = machine.ADC(machine.Pin(36))
        self.adc36.atten(machine.ADC.ATTN_11DB)
        self.pin16 = machine.Pin(16, machine.Pin.IN)
        self.pin19 = machine.Pin(19, machine.Pin.IN)
        self.pin12 = machine.Pin(12, machine.Pin.IN)
        self.pin2 = machine.Pin(2, machine.Pin.IN)
        self.pin23 = machine.Pin(23, machine.Pin.IN)

        self.pin13 = machine.Pin(13, machine.Pin.IN)
        self.pin14 = machine.Pin(14, machine.Pin.IN)
        self.pin18 = machine.Pin(18, machine.Pin.IN)
        self.pin5 = machine.Pin(5, machine.Pin.IN)
        self.btnMap = {"上": self.pin12, "下": self.pin13, "左": self.pin14, "右": self.pin18, "确认": self.pin5, "返回": self.pin19}

    def value(self, but):
        return self.btnMap.get(but).value() if self.btnMap.get(but) else 0


#三轴传感器
class MSA301(object):
    def __init__(self):
        self.addr = 38
        self.I2C = I2CInit()
        self.i2cxy = self.I2C.get_sen_i2c(self.addr)
        self.i2cxy.writeto(self.addr, b'\x0F\x08')
        self.i2cxy.writeto(self.addr, b'\x11\x00')
    def get_x(self):
        retry = 0
        if retry < 5:
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
        if retry < 5:
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
        if retry < 5:
            try:
                self.i2cxy.writeto(self.addr, b'\x06', False)
                buf = self.i2cxy.readfrom(self.addr, 2)
                z = ustruct.unpack('h', buf)[0]
                return z / 4 / 4096
            except:
                retry = retry + 1
        else:
            raise Exception("i2c read/write error!")
