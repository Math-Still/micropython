import time
from machine import Pin,I2C

# 使用的传感器为SPL06，程序仅为测试使用，仅读取关键传感器数值。

class SPL06():

    def __init__(self,I2Cd=None,SDA=21,SCL=22,addr=118):
    
        if I2Cd == None:
            self.i2c = I2C(scl = Pin(SCL), sda = Pin(SDA), freq = 200000)
        else:
            self.i2c = I2Cd
        
        self.address = addr  # 传感器默认地址
        self.i2c.writeto_mem(self.address, 0x06, b'\x03\x83\x07\x00')
        
        self.c0 = 0
        self.c1 = 0
        self.c00 = 0
        self.c10 = 0
        self.c01 = 0
        self.c11 = 0
        self.c20 = 0
        self.c21 = 0
        
        self.get_c() # 初始化一些不知道啥东西
        
    def get_c(self):
        byte = self.i2c.readfrom_mem(self.address, 0x10, 27)
        
        # c0
        self.c0 = (byte[0] << 4) | (byte[1] >> 4) 
        if self.c0 & (1<<11):# 如果数值最左位为1，则为负数，进行取反计算
            self.c0 = (self.c0 & 0X7FF) - 2048
        
        # c1
        self.c1 = (( ( byte[1] & 0x0F ) | 0XF0) << 8) + byte[2] 
        if self.c1 & (1<<11):
            self.c1 = (self.c1 & 0X7FF) - 2048
        
        # c00
        self.c00 = (((byte[3] << 8) | byte[4] ) << 4 ) | ( byte[5] >> 4)
        if self.c00 & (1<<19): # 如果数值最左位为1，则为负数，进行取反计算
            self.c00 = (self.c00 & 0X7FFFF) - 524288
        
        # c10
        self.c10 = ( ( ( byte[5] << 8 ) | byte[6] ) << 8 ) | byte[7]
        if self.c10 & (1<<19):
            self.c10 = (self.c10 & 0X7FFFF) - 524288
            
        # c01
        self.c01 = ((  byte[8] << 8) | byte[9] )
        if self.c01 & (1<<15):
            self.c01 = (self.c01 & 0X7FFF) - 32768
        
        # c11
        self.c11 = ( ( byte[10] << 8 ) | byte[11] ) 
        if self.c11 & (1<<15):
            self.c11 = (self.c11 & 0X7FFF) - 32768
            
        # c20
        self.c20 = ((  byte[12] << 8) | byte[13] )
        if self.c20 & (1<<15):
            self.c20 = (self.c20 & 0X7FFF) - 32768
        
        # c21
        self.c21 = ( ( byte[14] << 8 ) | byte[15] ) 
        if self.c21 & (1<<15):
            self.c21 = (self.c21 & 0X7FFF) - 32768
            
        # c30
        self.c30 = ( ( byte[16] << 8 ) | byte[17] ) 
        if self.c30 & (1<<15):
            self.c30 = (self.c30 & 0X7FFF) - 32768
            
        
        # print(byte)
        # print("c0:" + str(self.c0))
        # print("c1:" + str(self.c1))
        # print("c00:" + str(self.c00))
        # print("c10:" + str(self.c10))
        # print("c01:" + str(self.c01))
        # print("c11:" + str(self.c11))
        # print("c20:" + str(self.c20))
        # print("c21:" + str(self.c21))
        # print("c30:" + str(self.c30))
        
    
    def get_sc(self,add,fadd):
        byte = self.i2c.readfrom_mem(self.address, add, 3)
        traw = ( ( ( byte[0] << 8 ) | byte[1] ) << 8 ) | byte[2]
        if traw & (1<<23):
            traw = (traw & 0X7FFFFF) - 8388608
        
        return traw / self.get_scale_factor(fadd)
    
    def get_scale_factor(self,add):
        byte = self.i2c.readfrom_mem(self.address, add, 1)
        traw = byte[0] & 0x07
        if traw == 0:
            traw = 524288
        elif traw == 1:
            traw = 1572864
        elif traw == 2:
            traw = 3670016
        elif traw == 3:
            traw = 7864320
        elif traw == 4:
            traw = 253952
        elif traw == 5:
            traw = 516096
        elif traw == 6:
            traw = 1040384
        elif traw == 7:
            traw = 2088960
        return traw
    
        
    # 获取温度
    def getTemp(self):
        temp = self.get_sc(0x03,0x07)
        temp = (self.c0 * 0.5) + (self.c1 * temp)
        
        return temp
        
        
        
    # 获取大气压
    def getpcomp(self):
        temp = self.get_sc(0x03,0x07)
        pcomp = self.get_sc(0x00,0x06)
        pcomp = self.c00 + pcomp * (self.c10 + pcomp * (self.c20 + pcomp * self.c30)) + temp * self.c01 + temp * pcomp * ( self.c11 + pcomp * self.c21)
        
        return pcomp
    
    # convert to mb
    def get_pressure(self):
        return self.getpcomp() / 100
    
    
    # 进行计算海拔值    海拔越高，温度越低，每升高1km，气温下降6℃；任意地的气压值均随海拔高度的升高而降低
    def get_altitude(self,seaLevelhPa = 1011.3):  # seaLevelhPa: 在谷歌上查找当地海平面压力 // 来自机场网站的当地压力 8/22
        altitude = 44330 * (1.0 - pow(self.get_pressure() / seaLevelhPa, 0.1903 ) )
        
        return altitude
        
        
        
        