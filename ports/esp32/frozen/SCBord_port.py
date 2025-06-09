# 科创板的接口库。只适合科创板系列版本
import machine
import time

class SCBord_port():
    def __init__(self,mmm):

        self.i2c_pin_sda = [5, 4 ,21,13]
        self.i2c_pin_scl = [18,15,22,14]

        self.sensor = {87:[0,0,"max301-血氧"],80:[0,0,"AT24c256-eeprom"],38:[0,0,"msa301-三轴"],98:[0,0,"msa301-三轴"],60:[0,0,"oled-屏幕"],64:[0,0,"sht20-温湿度"],104:[0,0,"ds3231-时钟模块"],36:[0,0,"TM1650-四路数码管"],119:[0,0,"bmp280-气压传感器"]}

        self.versions = "SCB_v2.0x"
        
        for i in range(0, len(self.i2c_pin_scl), 1):
            
            i2c = machine.I2C(scl = machine.Pin(self.i2c_pin_scl[i]), sda = machine.Pin(self.i2c_pin_sda[i]), freq = 400000)
            i2cscan = i2c.scan()
            #print(i2cscan)
            
            
            if len(i2cscan) < 5:
                for j in range(0, len(i2cscan), 1):
                    try:
                        self.sensor[i2cscan[j]][0] = self.i2c_pin_sda[i]
                        self.sensor[i2cscan[j]][1] = self.i2c_pin_scl[i]
                        
                        if mmm == 0:
                            print("加载成功--" + self.sensor[i2cscan[j]][2] + str(self.sensor[i2cscan[j]][0]) + ":" + str(self.sensor[i2cscan[j]][1]))
                        
                        if self.i2c_pin_sda[i] == 13 and i2cscan[j] == 80:
                            self.versions = "SCB_v2.0j"
                            #i2c.writeto_mem(80, 3000, b'SCB_v2.0j', addrsize=16)
                            #time.sleep_ms(100)
                            #data = i2c.readfrom_mem(80, 3000,15,addrsize=16)
                            #print(data)
                        elif self.i2c_pin_sda[i] == 21 and i2cscan[j] == 80:
                            self.versions = "SCB_v2.0x"
                            #i2c.writeto_mem(80, 3000, b'SCB_v2.0j', addrsize=16)
                    except:
                        print("error_i2c:" + str(i2cscan[j]))
        if mmm == 0:
            #print(self.sensor)
            print("欢迎使用科创板---" + self.versions)
    
    def get_sen_i2c(self,add):
        return machine.I2C(scl = machine.Pin(self.sensor[add][1]), sda = machine.Pin(self.sensor[add][0]), freq = 400000)
        
    def get_sen_pin(self,add):
        return self.sensor[add][0],self.sensor[add][1]
        
    def get_scb_version(self):
        return self.versions
        





















