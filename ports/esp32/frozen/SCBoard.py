import time
import machine
from framebuf import FrameBuffer as FB
import ustruct
import random

#中科四平屏幕控制
class zksp_oled_text():
    def __init__(self):
        self.f = Funs()

        fontsize24 = 24
        fontsize21 = 21
        zhong = "0000000070000070000070000070403FFFE03870E03870E03870E03870E03870E03FFFE03870E03070C0007000007000007000007000007000007000000000"
        self.zhong = FB(self.f.to_bytearray(zhong), fontsize24, fontsize21, 3)
        ke = "0000000181C007C1C07F01C00639C0061DC006CDC0FFE1C04601C00E19C00F9DC01FCDF01EC1F8367FC066E1C0C601C00601C00601C00601C00601C0000000"
        self.ke = FB(self.f.to_bytearray(ke), fontsize24, fontsize21, 3)
        si = "0000003FFFE039DCE039DCE039DCE039DCE039DCE039DCE0399CE0399CE03B9CE03B9CE03F1DE03F0FE03E00E03C00E03800E03FFFE03800E03800E0000000"
        self.si = FB(self.f.to_bytearray(si), fontsize24, fontsize21, 3)
        ping = "0000000000C03FFFE00070001C71C00E7380077300077600037C60FFFFF0407000007000007000007000007000007000007000007000007000007000000000"
        self.ping = FB(self.f.to_bytearray(ping), fontsize24, fontsize21, 3)

    def get_text(self,x):
        if(x==1):
            return self.zhong
        elif(x==2):
            return self.ke
        elif(x==3):
            return self.si
        elif(x==4):
            return self.ping
        return self.test0


class smartpoint():
    def __init__(self,xi,xa,yi,ya,speed):
        self.xa = xa
        self.xi = xi
        self.ya = ya
        self.yi = yi
        self.speed = speed


        self.xl = 0 # 步数
        self.yl = 0


        self.xf= 0 # 速度
        self.yf= 0


        self.xx = 64
        self.yy = 32

    def carry(self):
        self.xl -= 1
        if self.xl <= 0:
            self.xl = random.randint(int(self.xi), int(self.xa/2))
            self.xf = random.uniform(-self.speed, self.speed)

        self.yl -=1
        if self.yl <= 0:
            self.yl = random.randint(int(self.yi), int(self.ya/2))
            self.yf = random.uniform(-self.speed, self.speed)

        self.xx = self.xx + self.xl * self.xf
        self.yy = self.yy + self.yl * self.yf

        if self.xx >= self.xa:
            self.xl = random.randint(int(self.xi), int(self.xa/2))
            self.xf = random.uniform(-self.speed, 0)

        if self.xx <= self.xi:
            self.xl = random.randint(int(self.xi), int(self.xa/2))
            self.xf = random.uniform(0, self.speed)

        if self.yy >= self.ya:
            self.yl = random.randint(int(self.yi), int(self.ya/2))
            self.yf = random.uniform(-self.speed, 0)

        if self.yy <= self.yi:
            self.yl = random.randint(int(self.yi), int(self.ya/2))
            self.yf = random.uniform(0, self.speed)





    def get_x(self):
        return int(self.xx)

    def get_y(self):
        return int(self.yy)


# 移除SCBord_port依赖，使用原生I2C
#科创板血氧
class blood():
    def __init__(self):
        # 尝试不同的I2C引脚配置来寻找血氧传感器(地址87)
        self.i2c_configs = [
            (4, 15),   # SDA=4, SCL=15
            (5, 18),   # SDA=5, SCL=18  
            (21, 22),  # SDA=21, SCL=22
            (13, 14)   # SDA=13, SCL=14
        ]
        
        self.i2cxueyang = None
        self.version = "SCB_v2.0x"  # 默认版本
        
        try:
            self.xueyang = Xueyang()
            # 尝试找到血氧传感器
            for sda, scl in self.i2c_configs:
                try:
                    i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=400000)
                    devices = i2c.scan()
                    if 87 in devices:  # 血氧传感器地址
                        self.i2cxueyang = i2c
                        print(f"[BLOOD] 血氧传感器找到 - SDA:{sda}, SCL:{scl}")
                        break
                except:
                    continue
                    
            if not self.i2cxueyang:
                print("[BLOOD] 未找到血氧传感器")
                
        except Exception as e:
            print(f"[BLOOD] 初始化失败: {e}")
            pass
        self.bloodbool = True
        self.REG_FIFO_DATA = 7
        self.REG_INTR_STATUS_1 = 0
        self.REG_INTR_STATUS_2 = 1
        self.hehthr = 0
        self.lowehr = 0
        self.thisht = 8
        self.oldhr = 0
        self.frequency = 0
        self.frequency_time = []
        self.htnum = 0
        self.red = []
        self.ir = []
        self.spo2x = 0
        self.isstate = 0
        for l in range(0, 8, 1):
            self.frequency_time.append(0)
    def get_hrir(self):
        if self.isstate != 1:
            self.isstate  = 1
            self.xueyang.setup(self.i2cxueyang)
        reg_INTR1 = self.i2cxueyang.readfrom_mem(87, self.REG_INTR_STATUS_1,1,addrsize=8)
        reg_INTR2 = self.i2cxueyang.readfrom_mem(87, self.REG_INTR_STATUS_2,1,addrsize=8)
        d = self.i2cxueyang.readfrom_mem(87, self.REG_FIFO_DATA,6,addrsize=8)
        hr = ((((d[0]<<16)|(d[1]<<8))|d[2])&262143)
        ir = ((((d[3]<<16)|(d[4]<<8))|d[5])&262143)
        #time.sleep_ms(22)
        return (hr,ir)
    def start(self):
        if self.isstate  != 2:
            self.isstate  = 2
            self.xueyang.setup(self.i2cxueyang)
        while self.bloodbool:
            reg_INTR1 = self.i2cxueyang.readfrom_mem(87, self.REG_INTR_STATUS_1,1,addrsize=8)
            reg_INTR2 = self.i2cxueyang.readfrom_mem(87, self.REG_INTR_STATUS_2,1,addrsize=8)
            d = self.i2cxueyang.readfrom_mem(87, self.REG_FIFO_DATA,6,addrsize=8)
            time.sleep_ms(20)
            newhr = ((((d[0]<<16)|(d[1]<<8))|d[2])&262143)
            self.red.append(newhr)
            self.ir.append(((((d[3]<<16)|(d[4]<<8))|d[5])&262143))

            if(newhr>self.oldhr):
                self.hehthr = newhr
            if(newhr<self.oldhr):
                self.lowehr = newhr
            blood = self.hehthr-self.lowehr
            ddd = ((1024-blood)-458)/100
            #print(blood)
            if ddd>1.6:
                if self.frequency >=0:
                    self.frequency += 1
                    if self.frequency >3:
                        timedd = time.ticks_ms()
                        self.frequency_time[7] = timedd
                        self.frequency = -1
                        for j in range(0, 7, 1):
                            self.frequency_time[j] = self.frequency_time[j + 1]
                        #print(self.frequency_time)
                        hrtime = []
                        for k in range(0, 6, 1):
                            ahr = int(self.frequency_time[k+1]-self.frequency_time[k])
                            if 200 < ahr < 2000:
                                hrtime.append(ahr)
                        #print(hrtime)
                        try:
                            self.htnum = 60/(sum(hrtime)/6000)
                            print(str(round(self.htnum,2)))
                            return hrtime
                        except:
                            pass
            else :
                self.frequency = 0
            self.oldhr = newhr

            if len(self.red)>100:
                hr, hr_valid, spo2, spo2_valid = self.xueyang.calc_hr_and_spo2(self.ir, self.red)
                if spo2 >10:
                    self.spo2x = spo2
                    #print("spo2   " + str(spo2))
                self.red = []
                self.ir = []
        return ""
    def get_heart(self):
        #print("hert:   " + str(self.htnum))
        return self.htnum
    def get_blood(self):
        #print("spo2:   " + str(self.spo2x))
        return self.spo2x

    def get_temp(self):
        self.isstate  = 3
        self.i2cxueyang.writeto_mem(87, 12, b'\x00', addrsize=8)
        self.i2cxueyang.writeto_mem(87, 13, b'\x00', addrsize=8)
        self.i2cxueyang.writeto_mem(87, 33, b'\x01', addrsize=8)
        tempInt = self.i2cxueyang.readfrom_mem(87, 31,1,addrsize=8);
        tempFrac = self.i2cxueyang.readfrom_mem(87, 32,1,addrsize=8);
        tempi = ord(tempInt) + ord(tempFrac) * 0.0625

        return tempi
        #global maxtemp
        #if maxtemp <= tempi:
        #    maxtemp = tempi
        #if use >0:
        #    maxtemp = 0
        #temp = str(tempi)[0:4] + "℃"
        #print(temp)
        #oled.fill(0)
        #oled.framebuf.blit(tx.get_24_text("t7"),6,32)
        #for i in range(0, len(str(temp)), 1):
        #    oled.framebuf.blit(tx.get_24_text(str(temp[i])),36 + 16 * i,32)
        #
        #oled.text("max:" + str(maxtemp)[0:4] + "",32,8)
        #oled.show()




    def heart_rate_stop(self):
        self.bloodbool = False

    def calc_hr_and_spo2(self,ir,red):
        return self.xueyang.calc_hr_and_spo2(ir,red)


#血氧初始化
class Xueyang():
    def __init__(self):
        self.SAMPLE_FREQ = 25
        self.MA_SIZE = 4
        self.BUFFER_SIZE = 100
        self.funs = Funs()
        self.SAMPLE_FREQ = 25
        self.MA_SIZE = 4
        self.BUFFER_SIZE = 100
        self.I2C_WRITE_ADDR = 174
        self.I2C_READ_ADDR = 175
        self.REG_INTR_STATUS_1 = 0
        self.REG_INTR_STATUS_2 = 1
        self.REG_INTR_ENABLE_1 = 2
        self.REG_INTR_ENABLE_2 = 3
        self.REG_FIFO_WR_PTR = 4
        self.REG_OVF_COUNTER = 5
        self.REG_FIFO_RD_PTR = 6
        self.REG_FIFO_DATA = 7
        self.REG_FIFO_CONFIG = 8
        self.REG_MODE_CONFIG = 9
        self.REG_SPO2_CONFIG = 10
        self.REG_LED1_PA = 12
        self.REG_LED2_PA = 13
        self.REG_PILOT_PA = 16
        self.REG_MULTI_LED_CTRL1 = 17
        self.REG_MULTI_LED_CTRL2 = 18
        self.REG_TEMP_INTR = 31
        self.REG_TEMP_FRAC = 32
        self.REG_TEMP_CONFIG = 33
        self.REG_PROX_INT_THRESH = 48
        self.REG_REV_ID = 254
        self.REG_PART_ID = 255
        self.address = 87

    def setup(self,i2c):
        try:
            i2c.writeto_mem(self.address, self.REG_INTR_ENABLE_1, b'\xC0', addrsize=8)
        except:
            print("xye")

        try:

            i2c.writeto_mem(self.address, self.REG_INTR_ENABLE_1, b'\xC0', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_INTR_ENABLE_2, b'\x00', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_FIFO_WR_PTR, b'\x00', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_OVF_COUNTER, b'\x00', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_FIFO_RD_PTR, b'\x00', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_FIFO_CONFIG, b'\x4F', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_MODE_CONFIG, b'\x03', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_SPO2_CONFIG, b'\x27', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_LED1_PA, b'\x24', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_LED2_PA, b'\x24', addrsize=8)
            i2c.writeto_mem(self.address, self.REG_PILOT_PA, b'\x7f', addrsize=8)
        except:
            print("xye2")

    def calc_hr_and_spo2(self,ir_data, red_data):
        ir_mean = int((sum(ir_data) / len(ir_data)))
        x = []
        for k in ir_data:
            x.append((k - ir_mean) * -1)
            m = len(x) - self.MA_SIZE
        for i in range(0, m, 1):
            x[i] = sum(x[i : (i + self.MA_SIZE)]) / self.MA_SIZE
        n_th = int((sum(x) / len(x)))
        n_th = 30 if (n_th < 30) else n_th
        n_th = 60 if (n_th > 60) else n_th
        ir_valley_locs,n_peaks = self.funs.find_peaks(x, self.BUFFER_SIZE, n_th, 4, 15)
        peak_interval_sum = 0
        if n_peaks >= 2:
            for i in range(1, n_peaks, 1):
                peak_interval_sum += ir_valley_locs[i] - ir_valley_locs[(i - 1)]
            peak_interval_sum = int((peak_interval_sum / (n_peaks - 1)))
            hr = int(((self.SAMPLE_FREQ * 60) / peak_interval_sum))
            hr_valid = True
        else:
            hr = -999
            hr_valid = False
        exact_ir_valley_locs_count = n_peaks
        for i in range(0, exact_ir_valley_locs_count, 1):
            if ir_valley_locs[i] > self.BUFFER_SIZE:
                spo2 = -999
                spo2_valid = False
                return (hr, hr_valid, spo2, spo2_valid)
        i_ratio_count = 0
        ratio = []
        red_dc_max_index = -1
        ir_dc_max_index = -1
        for k in range(0, exact_ir_valley_locs_count - 1, 1):
            red_dc_max = -16777216
            ir_dc_max = -16777216
            if ir_valley_locs[(k + 1)] - ir_valley_locs[k] > 3:
                for i in range(ir_valley_locs[k], ir_valley_locs[(k + 1)], 1):
                    if ir_data[i] > ir_dc_max:
                        ir_dc_max = ir_data[i]
                        ir_dc_max_index = i
                    if red_data[i] > red_dc_max:
                        red_dc_max = red_data[i]
                        red_dc_max_index = i
                    red_ac = int(((red_data[ir_valley_locs[(k + 1)]] - red_data[ir_valley_locs[k]]) * (red_dc_max_index - ir_valley_locs[k])))
                    red_ac = red_data[ir_valley_locs[k]] + int((red_ac / (ir_valley_locs[(k + 1)] - ir_valley_locs[k])))
                    red_ac = red_data[red_dc_max_index] - red_ac
                    ir_ac = int(((ir_data[ir_valley_locs[(k + 1)]] - ir_data[ir_valley_locs[k]]) * (ir_dc_max_index - ir_valley_locs[k])))
                    ir_ac = ir_data[ir_valley_locs[k]] + int((ir_ac / (ir_valley_locs[(k + 1)] - ir_valley_locs[k])))
                    ir_ac = ir_data[ir_dc_max_index] - ir_ac
                    nume = red_ac * ir_dc_max
                    denom = ir_ac * red_dc_max
                    if (denom > 0 and i_ratio_count < 5) and nume != 0:
                        ratio.append(int((((nume * 100)&4294967295) / denom)))
                        i_ratio_count += 1
        ratio = sorted(ratio)
        mid_index = int((i_ratio_count / 2))
        ratio_ave = 0
        if mid_index > 1:
            ratio_ave = int(((ratio[(mid_index - 1)] + ratio[mid_index]) / 2))
        elif len(ratio) != 0:
            ratio_ave = ratio[mid_index]
        if ratio_ave > 2 and ratio_ave < 184:
            spo2 = ((-45.06 * ratio_ave ** 2) / 10000 + (30.054 * ratio_ave) / 100) + 94.845
            spo2_valid = True
        else:
            spo2 = -999
            spo2_valid = False
        return (hr, hr_valid, spo2, spo2_valid )


#三轴传感器
class MSA301():
    def __init__(self):
        self.addr = 98
        # 尝试不同的I2C引脚配置来寻找三轴传感器(地址98)
        self.i2c_configs = [
            (4, 15),   # SDA=4, SCL=15
            (5, 18),   # SDA=5, SCL=18  
            (21, 22),  # SDA=21, SCL=22
            (13, 14)   # SDA=13, SCL=14
        ]
        
        self.i2cxy = None
        
        # 快速找到三轴传感器 - 优先尝试常用配置
        success = False
        common_configs = [
            (21, 22),  # SDA=21, SCL=22 (最常用)
            (4, 15),   # SDA=4, SCL=15
        ]
        
        # 第一轮：尝试最常用的配置
        for sda, scl in common_configs:
            try:
                # 使用较低频率和超时，提高兼容性和速度
                i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=100000, timeout=1000)
                devices = i2c.scan()
                if self.addr in devices:  # 三轴传感器地址
                    self.i2cxy = i2c
                    print(f"[MSA301] 三轴传感器找到 - SDA:{sda}, SCL:{scl}")
                    # 快速初始化传感器
                    self.i2cxy.writeto(self.addr, b'\x0F\x08')
                    self.i2cxy.writeto(self.addr, b'\x11\x00')
                    success = True
                    break
            except:
                # 静默跳过失败的配置
                continue
        
        # 第二轮：如果常用配置失败，尝试其他配置
        if not success:
            fallback_configs = [(5, 18), (13, 14)]
            for sda, scl in fallback_configs:
                try:
                    i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=100000, timeout=1000)
                    devices = i2c.scan()
                    if self.addr in devices:
                        self.i2cxy = i2c
                        print(f"[MSA301] 三轴传感器找到 - SDA:{sda}, SCL:{scl}")
                        self.i2cxy.writeto(self.addr, b'\x0F\x08')
                        self.i2cxy.writeto(self.addr, b'\x11\x00')
                        success = True
                        break
                except:
                    continue
                
        if not success:
            print("[MSA301] 未找到三轴传感器，将使用模拟数据")
            self.i2cxy = None  # 不抛出异常，允许系统继续运行
    def get_y(self):
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

    def get_x(self):
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

#公共使用的方法
class Funs():

    def to_bytearray(s):
        return bytearray([int('0x'+s[i:i+2]) for i in range(0,len(s),2)])


    def find_peaks(self,x, size, min_height, min_dist, max_num):
        i = 0
        n_peaks = 0
        ir_valley_locs = []
        while i < size - 2:
            if x[i] > min_height and x[i] > x[(i - 1)]:
                n_width = 1
                while i + n_width < size - 1 and x[i] == x[(i + n_width)]:
                    n_width += 1
                if x[i] > x[(i + n_width)] and n_peaks < max_num:
                    ir_valley_locs.append(i)
                    n_peaks += 1
                    i += n_width + 1
                else:
                    i += n_width
            else:
                i += 1
        sorted_indices = sorted(ir_valley_locs, key=lambda i: x[i])
        sorted_indices.reverse()
        i = -1
        while i < n_peaks:
            old_n_peaks = n_peaks
            n_peaks = i + 1
            j = i + 1
            while j < old_n_peaks:
                n_dist = (sorted_indices[j] - sorted_indices[i]) if (i != -1) else (sorted_indices[j] + 1)
                if n_dist > min_dist or n_dist < -1 * min_dist:
                    sorted_indices[n_peaks] = sorted_indices[j]
                    n_peaks += 1
                j += 1
            i += 1
        sorted_indices[:n_peaks] = sorted(sorted_indices[:n_peaks])
        n_peaks = min([n_peaks, max_num])
        return (ir_valley_locs, n_peaks)


    def to_bytearray(self,s):
        return bytearray([int('0x'+s[i:i+2]) for i in range(0,len(s),2)])



class Button():
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

        # 使用原生方法检测版本，基于I2C设备扫描
        self.version = self._detect_version()

    def _detect_version(self):
        """检测科创板版本 - 快速版本"""
        # 优先尝试最常用的配置，减少扫描时间
        common_configs = [
            (21, 22),  # SDA=21, SCL=22 (最常用)
            (13, 14),  # SDA=13, SCL=14 (v2.0j)
        ]
        
        # 使用更快的I2C频率和减少超时时间
        for sda, scl in common_configs:
            try:
                # 创建I2C时使用更高频率，减少扫描时间
                i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=100000, timeout=1000)
                devices = i2c.scan()
                
                # 快速检测特定设备来判断版本
                if 80 in devices:
                    if sda == 13:
                        print(f"[BUTTON] 检测到SCB_v2.0j版本 - SDA:{sda}, SCL:{scl}")
                        return "SCB_v2.0j"
                    elif sda == 21:
                        print(f"[BUTTON] 检测到SCB_v2.0x版本 - SDA:{sda}, SCL:{scl}")
                        return "SCB_v2.0x"
            except:
                # 快速跳过失败的配置
                continue
                
        # 如果快速检测失败，使用默认版本避免进一步延迟
        print("[BUTTON] 快速检测失败，使用默认版本SCB_v2.0x")
        return "SCB_v2.0x"

    def value(self,but):
        if self.version == "SCB_v2.0j":
            if but == "上":
                if self.pin12.value() == 1:
                    return 1
                else:
                    return 0
            elif but == "下":
                if self.pin23.value() == 1:
                    return 1
                else:
                    return 0

            elif but == "左":

                if self.adc36.read()==0:
                    return 1
                elif self.adc36.read() > 0:
                    return 0

            elif but == "右":
                if self.pin2.value() == 1:
                    return 1
                else:
                    return 0

            elif but == "确认":
                if self.pin16.value() == 1:
                    return 1
                else:
                    return 0

            elif but == "返回":
                if self.pin19.value() == 1:
                    return 1
                else:
                    return 0


        elif self.version == "SCB_v2.0x":
            if but == "上":
                if self.pin12.value() == 1:
                    return 1
                else:
                    return 0
            elif but == "下":
                if self.pin13.value() == 1:
                    return 1
                else:
                    return 0

            elif but == "左":

                if self.pin14.value()==1:
                    return 1
                else :
                    return 0

            elif but == "右":
                if self.pin18.value() == 1:
                    return 1
                else:
                    return 0

            elif but == "确认":
                if self.pin5.value() == 1:
                    return 1
                else:
                    return 0

            elif but == "返回":
                if self.pin19.value() == 1:
                    return 1
                else:
                    return 0
        return 0




class infrared_get():
    def __init__(self,pinin):
        self.pininf = machine.Pin(pinin, machine.Pin.IN)
        machine.Pin(pinin).irq(handler = self.attachInterrupt_func, trigger = machine.Pin.IRQ_FALLING)
        self.sml = 1
        self.big = 0
        self.infdata = 0


    def get_inf_int(self):
        if  self.infdata == 0:
            return 0
        data = int(self.infdata[16 : 24],2)
        #self.set_inf_zero()
        return data

    def get_inf_bin(self):
        if  self.infdata == 0:
            return 0
        data = self.infdata

        #self.set_inf_zero()
        return data

    def get_inf_hex(self):
        if  self.infdata == 0:
            return 0
        data = hex(int(self.infdata[0 : 24],2))
        #self.set_inf_zero()
        return data

    def set_inf_zero(self):
        self.infdata = 0

    def attachInterrupt_func(self,x):
        info = self.getinfo()
        if info != 0:
            self.infdata = info
            #print(info)


    def getinfo(self):
        j = 0
        k = 0
        err = 0
        Times = 0
        time.sleep_ms(8)
        if self.pininf.value() < self.sml:
            try:
                getdata = 0
                for k in range(0, 8, 1):
                    for j in range(0, 8, 1):
                        err = 45
                        while self.pininf.value() < self.sml and err > 0:
                            time.sleep_us(10)
                            err -= 1
                        err = 450
                        while self.pininf.value() > self.big and err > 0:
                            time.sleep_us(100)
                            Times += 1
                            err -= 1
                            if Times > 16:
                                err = 0
                        getdata = (getdata<<1)
                        if Times >= 8:
                            getdata = getdata + 1
                        Times = 0
                #print((bin(getdata)))
                #print(bin(getdata)[20 : 28])
                return bin(getdata)[4:]

            except:
                return 0
                pass
        return 0



class infrared_set():
    def __init__(self,pinout):

        self.pwmv1 = 500
        self.pwmv0 = 0
        self.pwminf = machine.PWM(machine.Pin(pinout))
        self.pwminf.freq(38000)
        self.pwminf.duty(0)

    def code0(self):
        self.pwminf.duty(self.pwmv1)
        time.sleep_us(520)
        self.pwminf.duty(self.pwmv0)
        time.sleep_us(380)

    def code1(self):
        self.pwminf.duty(self.pwmv1)
        time.sleep_us(520)
        self.pwminf.duty(self.pwmv0)
        time.sleep_us(1500)

    def inf_sendcode(self,f):
        lenf = len(f)
        self.pwminf.duty(self.pwmv1)
        time.sleep_ms(9)
        self.pwminf.duty(self.pwmv0)
        time.sleep_us(4360)
        for i in range(0, lenf, 1):
            self.code1() if(f[i:i+1] == b'1')  else self.code0()


class scbord_car():
    def __init__(self):
        self.carldA = machine.PWM(machine.Pin(12))
        self.carldA.freq(20000)
        self.carlpA = machine.PWM(machine.Pin(21))
        self.carlpA.freq(20000)
        self.carldB = machine.PWM(machine.Pin(19))
        self.carldB.freq(20000)
        self.carlpB = machine.PWM(machine.Pin(18))
        self.carlpB.freq(20000)
        self.carrdA = machine.PWM(machine.Pin(2))
        self.carrdA.freq(20000)
        self.carrpA = machine.PWM(machine.Pin(4))
        self.carrpA.freq(20000)
        self.carrdB = machine.PWM(machine.Pin(16))
        self.carrdB.freq(20000)
        self.carrpB = machine.PWM(machine.Pin(17))
        self.carrpB.freq(20000)

        self.car_driver(0,0,0)
        self.car_driver(1,0,0)
        self.car_driver(2,0,0)
        self.car_driver(3,0,0)



    def car_driver(self,wheel,direction,speed):
        speed = int(speed)
        if wheel == 0:
            self.car_speed(self.carldA,self.carlpA,direction,speed)
        elif wheel == 1:
            self.car_speed(self.carldB,self.carlpB,direction,speed)
        elif wheel == 2:
            self.car_speed(self.carrdA,self.carrpA,direction,speed)
        elif wheel == 3:
            self.car_speed(self.carrdB,self.carrpB,direction,speed)

    def car_speed(self,d,p,direction,speed):
        '''
        if direction == 1:
            d.duty(1023)
            p.duty(1023-speed)
            #p.duty(speed)
        elif direction == 0:
            d.duty(0)
            p.duty(speed)
        '''
        if direction == 1:
            d.duty(1023)
            p.duty(1023-speed)
        elif direction == 0:
            d.duty(1023-speed)
            p.duty(1023)










