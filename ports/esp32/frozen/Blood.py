import time
import machine
# 移除SCBord_port依赖，使用原生I2C

#血氧初始化
class Xueyang():
    def __init__(self):
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

#科创板血氧
class blood():
    def __init__(self):
        self.i2cxueyang = None
        self._device_found = False  # 添加设备检测标志
        
        try:
            self.xueyang = Xueyang()
            # 快速找到血氧传感器 - 优先尝试常用配置
            common_configs = [
                (21, 22),  # SDA=21, SCL=22 (最常用)
            ]
            
            success = False
            
            # 尝试连接血氧传感器
            for scl, sda in common_configs:
                try:
                    print(f"[BLOOD] 尝试连接血氧传感器 - SDA:{sda}, SCL:{scl}")
                    i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=100000)
                    
                    # 扫描I2C设备
                    devices = i2c.scan()
                    print(f"[BLOOD] 发现的I2C设备: {devices}")
                    
                    if 87 in devices:  # 血氧传感器地址
                        self.i2cxueyang = i2c
                        self._device_found = True
                        success = True
                        print(f"[BLOOD] 血氧传感器找到 - SDA:{sda}, SCL:{scl}")
                        break
                    else:
                        print(f"[BLOOD] 在地址87未找到血氧传感器")
                        # 释放I2C资源
                        del i2c
                        
                except Exception as e:
                    print(f"[BLOOD] 连接血氧传感器失败 - SDA:{sda}, SCL:{scl}: {e}")
                    continue
            
            if not success:
                print("[BLOOD] 未找到血氧传感器，将跳过血氧功能")
                self.i2cxueyang = None
                self._device_found = False
                
        except Exception as e:
            print(f"[BLOOD] 初始化失败: {e}")
            self.i2cxueyang = None
            self._device_found = False
            
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

    def _check_device(self):
        """检查设备是否可用"""
        if not self._device_found or not self.i2cxueyang:
            return False
        try:
            # 尝试读取设备ID来验证设备是否响应
            device_id = self.i2cxueyang.readfrom_mem(87, 255, 1, addrsize=8)  # PART_ID register
            return True
        except Exception as e:
            print(f"[BLOOD] 设备检查失败: {e}")
            self._device_found = False
            return False

    def get_hrir(self):
        if not self._check_device():
            print("[BLOOD] 血氧传感器不可用")
            return (0, 0)
            
        try:
            if self.isstate != 1:
                self.isstate = 1
                self.xueyang.setup(self.i2cxueyang)
            reg_INTR1 = self.i2cxueyang.readfrom_mem(87, self.REG_INTR_STATUS_1,1,addrsize=8)
            reg_INTR2 = self.i2cxueyang.readfrom_mem(87, self.REG_INTR_STATUS_2,1,addrsize=8)
            d = self.i2cxueyang.readfrom_mem(87, self.REG_FIFO_DATA,6,addrsize=8)
            hr = ((((d[0]<<16)|(d[1]<<8))|d[2])&262143)
            ir = ((((d[3]<<16)|(d[4]<<8))|d[5])&262143)
            return (hr,ir)
        except Exception as e:
            print(f"[BLOOD] 读取心率数据失败: {e}")
            return (0, 0)

    def start(self):
        if not self._check_device():
            print("[BLOOD] 血氧传感器不可用，无法启动监测")
            return ""
            
        try:
            if self.isstate != 2:
                self.isstate = 2
                self.xueyang.setup(self.i2cxueyang)
            
            while self.bloodbool:
                try:
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
                    
                    if ddd>1.6:
                        if self.frequency >=0:
                            self.frequency += 1
                            if self.frequency >3:
                                timedd = time.ticks_ms()
                                self.frequency_time[7] = timedd
                                self.frequency = -1
                                for j in range(0, 7, 1):
                                    self.frequency_time[j] = self.frequency_time[j + 1]
                                
                                hrtime = []
                                for k in range(0, 6, 1):
                                    ahr = int(self.frequency_time[k+1]-self.frequency_time[k])
                                    if 200 < ahr < 2000:
                                        hrtime.append(ahr)
                                
                                try:
                                    self.htnum = 60/(sum(hrtime)/6000)
                                    print(str(round(self.htnum,2)))
                                    return hrtime
                                except:
                                    pass
                    else:
                        self.frequency = 0
                    self.oldhr = newhr

                    if len(self.red)>100:
                        hr, hr_valid, spo2, spo2_valid = self.xueyang.calc_hr_and_spo2(self.ir, self.red)
                        if spo2 >10:
                            self.spo2x = spo2
                        self.red = []
                        self.ir = []
                        
                except Exception as e:
                    print(f"[BLOOD] 监测过程中出错: {e}")
                    time.sleep_ms(100)  # 出错时等待一段时间再重试
                    
        except Exception as e:
            print(f"[BLOOD] 启动监测失败: {e}")
            
        return ""
    def get_heart(self):
        #print("hert:   " + str(self.htnum))
        return self.htnum
    def get_blood(self):
        #print("spo2:   " + str(self.spo2x))
        return self.spo2x

    def get_temp(self):
        if not self._check_device():
            print("[BLOOD] 血氧传感器不可用，无法读取温度")
            return 0.0
            
        try:
            self.isstate = 3
            self.i2cxueyang.writeto_mem(87, 12, b'\x00', addrsize=8)
            self.i2cxueyang.writeto_mem(87, 13, b'\x00', addrsize=8)
            self.i2cxueyang.writeto_mem(87, 33, b'\x01', addrsize=8)
            tempInt = self.i2cxueyang.readfrom_mem(87, 31,1,addrsize=8);
            tempFrac = self.i2cxueyang.readfrom_mem(87, 32,1,addrsize=8);
            tempi = ord(tempInt) + ord(tempFrac) * 0.0625
            return tempi
        except Exception as e:
            print(f"[BLOOD] 读取温度失败: {e}")
            return 0.0
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

    def deinit(self):
        """释放血氧模块的所有资源"""
        try:
            # 停止心率监测
            self.heart_rate_stop()
            
            # 重置传感器配置到初始状态
            if self.i2cxueyang and self._device_found:
                try:
                    # 关闭LED电源
                    self.i2cxueyang.writeto_mem(87, 12, b'\x00', addrsize=8)  # LED1_PA
                    self.i2cxueyang.writeto_mem(87, 13, b'\x00', addrsize=8)  # LED2_PA
                    self.i2cxueyang.writeto_mem(87, 16, b'\x00', addrsize=8)  # PILOT_PA
                    
                    # 禁用中断
                    self.i2cxueyang.writeto_mem(87, 2, b'\x00', addrsize=8)   # INTR_ENABLE_1
                    self.i2cxueyang.writeto_mem(87, 3, b'\x00', addrsize=8)   # INTR_ENABLE_2
                    
                    # 重置FIFO
                    self.i2cxueyang.writeto_mem(87, 4, b'\x00', addrsize=8)   # FIFO_WR_PTR
                    self.i2cxueyang.writeto_mem(87, 5, b'\x00', addrsize=8)   # OVF_COUNTER
                    self.i2cxueyang.writeto_mem(87, 6, b'\x00', addrsize=8)   # FIFO_RD_PTR
                    
                    # 关闭传感器
                    self.i2cxueyang.writeto_mem(87, 9, b'\x80', addrsize=8)   # MODE_CONFIG (shutdown mode)
                    
                    print("[BLOOD] 血氧传感器已重置")
                except Exception as e:
                    print(f"[BLOOD] 重置传感器时出错: {e}")
            
            # 释放Xueyang对象
            if hasattr(self, 'xueyang') and self.xueyang:
                try:
                    del self.xueyang
                except Exception as e:
                    print(f"[BLOOD] 释放Xueyang对象时出错: {e}")
            
            # 清理数据缓冲区
            self.red.clear()
            self.ir.clear()
            self.frequency_time.clear()
            
            # 重置状态变量
            self.bloodbool = False
            self.isstate = 0
            self.htnum = 0
            self.spo2x = 0
            self.frequency = 0
            self.hehthr = 0
            self.lowehr = 0
            self.oldhr = 0
            
            # 标记为未初始化
            self._device_found = False
            
            print("[BLOOD] 血氧模块资源已释放")
            
        except Exception as e:
            print(f"[BLOOD] 释放资源时出错: {e}")

    def __del__(self):
        """析构函数，确保资源被释放"""
        self.deinit()

    def calc_hr_and_spo2(self,ir,red):
        return self.xueyang.calc_hr_and_spo2(ir,red)


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
