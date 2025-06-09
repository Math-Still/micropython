import machine


DS3231_ADDR       = 104
DS3231_REG_SEC    = b'\x00'
DS3231_REG_MIN    = b'\x01'
DS3231_REG_HOUR   = b'\x02'
DS3231_REG_WEEKDAY= b'\x03'
DS3231_REG_DAY    = b'\x04'
DS3231_REG_MONTH  = b'\x05'
DS3231_REG_YEAR   = b'\x06'
DS3231_REG_A1SEC  = b'\x07'
DS3231_REG_A1MIN  = b'\x08'
DS3231_REG_A1HOUR = b'\x09'
DS3231_REG_A1DAY  = b'\x0A'
DS3231_REG_A2MIN  = b'\x0B'
DS3231_REG_A2HOUR = b'\x0C'
DS3231_REG_A2DAY  = b'\x0D'
DS3231_REG_CTRL   = b'\x0E'
DS3231_REG_STA    = b'\x0F'
DS3231_REG_OFF    = b'\x10'
DS3231_REG_TEMP1   = b'\x11'
DS3231_REG_TEMP2   = b'\x12'

class DS3231(object):
    def __init__(self, sdas ,scls):
        #self.i2c = I2C(i2c_num, I2C.MASTER, baudrate = 100000)
        self.i2c = machine.I2C(scl = machine.Pin(scls), sda = machine.Pin(sdas), freq = 10000)

    def DATE(self, dat=[]):
        if dat==[]:
            t = []
            t.append(self.year())
            t.append(self.month())
            t.append(self.day())
            return t
        else:
            self.year(dat[0])
            self.month(dat[1])
            self.day(dat[2])

    def TIME(self, dat=[]):
        if dat==[]:
            t = []
            t.append(self.hour())
            t.append(self.min())
            t.append(self.sec())
            # t = ""
            # t+=self.hour()+":"
            # t+=self.min()+":"
            # t+=self.sec()
            return t
        else:
            self.hour(dat[0])
            self.min(dat[1])
            self.sec(dat[2])

    def DateTime(self, dat=[]):
        if dat==[]:
            return self.DATE() + self.TIME()
        else:
            self.year(dat[0])
            self.month(dat[1])
            self.day(dat[2])
            self.hour(dat[3])
            self.min(dat[4])
            self.sec(dat[5])

    def dec2hex(self, dat):
        return (int(dat/10)<<4) + (dat%10)

    def setREG(self, dat, reg):
        #buf = bytearray(2)
        #buf[0] = reg
        #buf[1] = dat
        #self.i2c.send(buf, DS3231_ADDR)
        print(reg)
        x = int.from_bytes(reg,'little')
        y = dat.to_bytes(2,'little')
        print(y)
        self.i2c.writeto_mem(DS3231_ADDR, x, y, addrsize=16)
        
    def getREG_DEC(self, reg):
        #self.i2c.send(reg, DS3231_ADDR)
        #t = self.i2c.recv(1, DS3231_ADDR)[0]
        self.i2c.writeto(DS3231_ADDR, reg)
        t = self.i2c.readfrom(DS3231_ADDR, 1)
        t = int.from_bytes(t,'little')
        return (t>>4)*10 + (t%16)

    def sec(self, sec=''):
        if sec == '':
            return self.getREG_DEC(DS3231_REG_SEC)
        else:
            self.setREG(self.dec2hex(sec), DS3231_REG_SEC)

    def min(self, min=''):
        if min == '':
            return self.getREG_DEC(DS3231_REG_MIN)
        else:
            self.setREG(self.dec2hex(min), DS3231_REG_MIN)

    def hour(self, hour=''):
        if hour=='':
            return self.getREG_DEC(DS3231_REG_HOUR)
        else:
            self.setREG(self.dec2hex(hour), DS3231_REG_HOUR)

    def day(self, day=''):
        if day=='':
            return self.getREG_DEC(DS3231_REG_DAY)
        else:
            self.setREG(self.dec2hex(day), DS3231_REG_DAY)

    def month(self, month=''):
        if month=='':
            return self.getREG_DEC(DS3231_REG_MONTH)
        else:
            self.setREG(self.dec2hex(month), DS3231_REG_MONTH)

    def year(self, year=''):
        if year=='':
            return self.getREG_DEC(DS3231_REG_YEAR)
        else:
            self.setREG(self.dec2hex(year), DS3231_REG_YEAR)

    def TEMP(self):
        #self.i2c.send(DS3231_REG_TEMP, DS3231_ADDR)
        #t1 = self.i2c.recv(1, DS3231_ADDR)[0]
        #self.i2c.send(DS3231_REG_TEMP+1, DS3231_ADDR)
        #t2 = self.i2c.recv(1, DS3231_ADDR)[0]

        self.i2c.writeto(DS3231_ADDR, DS3231_REG_TEMP1)
        t1 = self.i2c.readfrom(DS3231_ADDR, 1)
        
        self.i2c.writeto(DS3231_ADDR, DS3231_REG_TEMP2)
        t2 = self.i2c.readfrom(DS3231_ADDR, 1)

        t1 = int.from_bytes(t1,'big')
        t2 = int.from_bytes(t2,'big')

        if t1>0x7F:
            return t1 - t2/256 -256
        else:
            return t1 + t2/256


