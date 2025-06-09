import time
import ssd1306
import music
import machine
from framebuf import FrameBuffer as FB
import ustruct
import random


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

class Voice24():
	def __init__(self):
		self.f = Funs()
		
		fontsize24 = 24
		testd = "000000000000000000E000E000E000E000E00EE03FE07FE071E0F1E0F0E0F0E0F0E0F1E07BE03FE01FE0000000000000"
		self.testd = FB(self.f.to_bytearray(testd), 16, fontsize24, 3)
		testB = "0000000000000000FF00FFC0FFE0F1E0F0E0F0E0F1E0FFC0FFC0F3E0F0F0F0F0F0F0F0F0FFE0FFC0FF00000000000000"
		self.testB = FB(self.f.to_bytearray(testB), 16, fontsize24, 3)
		test1 = "000000000000000007000F001F003F007F007F000F000F000F000F000F000F000F000F000F000F000700000000000000"
		self.test1 = FB(self.f.to_bytearray(test1), 16, fontsize24, 3)
		test2 = "00000000000000001F803FC07BE0F1E0E0E000E001E001C003C007800F000E001E003C007FE0FFE07FE0000000000000"
		self.test2 = FB(self.f.to_bytearray(test2), 16, fontsize24, 3)
		test3 = "00000000000000001F803FC079E070E070E000E001C00FC00FC003E000E000E0F0E0F1E07FE03FC01F00000000000000"
		self.test3 = FB(self.f.to_bytearray(test3), 16, fontsize24, 3)
		test4 = "000000000000000001C003C003C007C00FC00FC01DC03DC079C071C0F1C0FFF0FFF001C001C001C001C0000000000000"
		self.test4 = FB(self.f.to_bytearray(test4), 16, fontsize24, 3)
		test5 = "00000000000000003FE03FE07FC0780070007E007F80FFC0F1E000E000E000E0E0E0E1E0FBC07FC03F00000000000000"
		self.test5 = FB(self.f.to_bytearray(test5), 16, fontsize24, 3)
		test6 = "0000000000000000038007800F000E001E003C003FC07FE079F0F0F0F070F070F0F070F079E03FC01F80000000000000"
		self.test6 = FB(self.f.to_bytearray(test6), 16, fontsize24, 3)
		test7 = "0000000000000000FFF0FFF07FF000E001C001C003800380070007000F000E000E001E001C001C001C00000000000000"
		self.test7 = FB(self.f.to_bytearray(test7), 16, fontsize24, 3)
		test8 = "00000000000000001F803FC079E0F0E0F0E071E07BC03FC07FC07BE0F0E0E0F0E0F0F0E0FBE07FC03F80000000000000"
		self.test8 = FB(self.f.to_bytearray(test8), 16, fontsize24, 3)
		test9 = "00000000000000001F807FC07BE0F1E0E0E0E0E0E0E0F1E0FBC07FC01F80078007000F000E001E003C00000000000000"
		self.test9 = FB(self.f.to_bytearray(test9), 16, fontsize24, 3)
		test0 = "00000000000000001F803FC07FC071E0F0E0F0E0F0E0F0F0E0F0E0E0F0E0F0E070E079E07FC03FC01F00000000000000"
		self.test0 = FB(self.f.to_bytearray(test0), 16, fontsize24, 3)


	def getvoicetext(self,x):

		if(x==1):
			return self.test1
		elif(x==2):
			return self.test2
		elif(x==3):
			return self.test3
		elif(x==4):
			return self.test4
		elif(x==5):
			return self.test5
		elif(x==6):
			return self.test6
		elif(x==7):
			return self.test7
		elif(x==8):
			return self.test8
		elif(x==9):
			return self.test9
		elif(x==0):
			return self.test0
		elif(x=="d"):
			return self.testd
		elif(x=="B"):
			return self.testB
			
			
		return self.test0
	
	
	

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	


