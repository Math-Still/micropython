import machine
import SCBoard
import music
import ssd1306
import SCBoard_text
import time
import _thread
import random
import SCBord_port
import neopixel

#科创板演示代码


class SCBord():
    def __init__(self):
        
        self.keyleft = 1
        self.keyright = 1
        self.keyup = 1
        self.keydown = 1
        
        self.SCB = SCBord_port.SCBord_port(0)
        self.version =  self.SCB.get_scb_version()

        self.button = SCBoard.Button()
        machine.Pin(19).irq(handler = self.attachInterrupt_funmenu, trigger = machine.Pin.IRQ_FALLING)
        if self.version == "SCB_v2.0j":
            machine.Pin(16).irq(handler = self.attachInterrupt_funok, trigger = machine.Pin.IRQ_FALLING)
        elif self.version == "SCB_v2.0x":
            machine.Pin(5).irq(handler = self.attachInterrupt_funok, trigger = machine.Pin.IRQ_FALLING)
            self.rgb = neopixel.NeoPixel(machine.Pin(23), 4, timing = True)
            self.rgb[0] = (30, 30, 10)
            self.rgb[1] = (30, 30, 10)
            self.rgb[2] = (30, 30, 10)
            self.rgb[3] = (30, 30, 10)
            self.rgb.write()
            
        
        self.menu = False
        self.ok = False
        self.isstart = False
    
        self.menuindex = 0
        
        i2oled = self.SCB.get_sen_i2c(60)
        self.oled = ssd1306.SSD1306_I2C(128,64,i2oled)
        
        self.tx = SCBoard_text.Font()
        self.t1 = self.tx.get_24_text("t1")
        self.t2 = self.tx.get_24_text("t2")
        self.t3 = self.tx.get_24_text("t3")
        self.t4 = self.tx.get_24_text("t4")
        self.t5 = self.tx.get_24_text("t5")
        self.t6 = self.tx.get_24_text("t6")
        self.t7 = self.tx.get_24_text("t7")
        self.t8 = self.tx.get_24_text("t8")

        self.fangge32 = self.tx.getzksp("fangge32")
        self.fangge16 = self.tx.getzksp("fangge16")
        self.qiuti16 = self.tx.getzksp("qiuti16")
        self.qiuti16xiaolian = self.tx.getzksp("qiuti16xiaolian")
        self.qiuti16kulian = self.tx.getzksp("qiuti16kulian")
        self.lingdian16 = self.tx.getzksp("lingdian16")
        
        self.geshu = 32
        self.ypy0 = 0
        self.ypy1 = 32
        self.xpy = 0
        self.ypy = 16
        self.tppy = 4
        
        self.pwm27 = machine.PWM(machine.Pin(27))
        self.adc39 = machine.ADC(machine.Pin(39))
        self.adc39.atten(machine.ADC.ATTN_11DB)
        self.adc36 = machine.ADC(machine.Pin(36))
        self.adc36.atten(machine.ADC.ATTN_11DB)
        
        
        self.qiuti16s = Qiuti16()
        self.sanzhou = SCBoard.MSA301()
        
        self.blood = SCBoard.blood()
        #self.xueyang = SCBoard.Xueyang()
        
        self.line_d = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
        self.line_a = SCBoard.smartpoint(1,128,1,64,0.3)
        self.line_b = SCBoard.smartpoint(1,128,1,64,0.2)
        self.line_c = SCBoard.smartpoint(1,128,1,64,0.15)
        self.line_s = SCBoard.smartpoint(-20,128,-20,64,0.1)
        
        self.spx = 0
        self.spy = 0
        
        
        self.lr = 20
        self.lg = 20
        self.lb = 20
        self.ll = 20
        self.lc = 5
        
        self.zaoyindata = []
        
        self.menutoled()
        
        


    def start(self):
        pwmmenu = 0
        pwmmboo = False
        while True:
        
            if self.menu and self.menuindex == 0:
                break

            if self.button.value("上") and self.keydown:
                self.keydown = 0
                print("上")
                if self.menuindex > 4 :self.menuindex -= 4
                self.menutoled()
            elif self.button.value("上")==0 and self.keydown==0:
                self.keydown = 1
                
            if self.button.value("下") and self.keyup:
                self.keyup = 0
                print("下")
                if self.menuindex <= 4 :self.menuindex += 4
                self.menutoled()
            elif self.button.value("下")==0 and self.keyup==0:
                self.keyup = 1
                
            if self.button.value("左") and self.keyleft:
                self.keyleft = 0
                print("左")
                if self.menuindex > 1 :self.menuindex -= 1
                self.menutoled()
            elif self.button.value("左")==0 and self.keyleft==0:
                self.keyleft = 1
                
            if self.button.value("右") and self.keyright:
                self.keyright = 0
                print("右")
                if self.menuindex < 8 :self.menuindex += 1
                self.menutoled()
            elif self.button.value("右")==0 and self.keyright==0:
                self.keyright = 1
                
            
            if self.ok and self.menuindex > 0:
                self.menutoled()
                
            if self.menu:
                self.menu = False
                self.menutoled()
            
            
            
            if self.version == "SCB_v2.0j":
                if pwmmboo:
                    pwmmenu += 1
                else:
                    pwmmenu -= 1
                if pwmmenu >1024:
                    pwmmboo = False
                elif pwmmenu <1:
                    pwmmboo = True
                self.pwm27.duty(int(pwmmenu))
            elif self.version == "SCB_v2.0x":
                if pwmmboo:
                    pwmmenu += 1
                else:
                    pwmmenu -= 1
                    
                if pwmmenu >254:
                    pwmmboo = False
                elif pwmmenu <1:
                    pwmmboo = True
                self.rgb[0] = (pwmmenu, 50, 50)
                self.rgb[1] = (50, pwmmenu, 50)
                self.rgb[2] = (50, 100, pwmmenu)
                self.rgb[3] = (50, pwmmenu, 0)
                self.rgb.write()
                
               
        self.oled.fill(0)
        print("debug>>")
        self.oled.text("debug>>",0,0)
        self.oled.show()

    def menutoled(self):
        print(self.menuindex)
        x = self.menuindex - 1
        if -1 == x:
            try:
                
                self.oled.framebuf.blit(self.tx.getzksp("zhong"),15, 20)
                self.oled.framebuf.blit(self.tx.getzksp("ke"),40,20)
                self.oled.framebuf.blit(self.tx.getzksp("si"),65, 20)
                self.oled.framebuf.blit(self.tx.getzksp("ping"),90, 20)
                #self.oled.text("www.3000lab.com",0,50)
                self.oled.show()
                music.play(music.RINGTONE, 25)
                pass
            except:
                print("屏幕测试失败")
            
        try:
            music.pitch_time(25, 100 + (x*50), 100)
        except:
            music.pitch(25, 100 + (x*50), 100)

        if(x>=0):

            self.oled.fill(0)
            
            if x<4:
                self.oled.framebuf.blit(self.fangge32,x * self.geshu, self.ypy0)
            elif x>=4:
                self.oled.framebuf.blit(self.fangge32,(x-4) * self.geshu, self.ypy1)
                
            self.oled.framebuf.blit(self.t1,self.geshu*0 + self.tppy,self.ypy0+self.tppy)
            self.oled.framebuf.blit(self.t2,self.geshu*1 + self.tppy,self.ypy0+self.tppy)
            self.oled.framebuf.blit(self.t3,self.geshu*2 + self.tppy,self.ypy0+self.tppy)
            self.oled.framebuf.blit(self.t4,self.geshu*3 + self.tppy,self.ypy0+self.tppy)
            self.oled.framebuf.blit(self.t5,self.geshu*0 + self.tppy,self.ypy1+self.tppy)
            self.oled.framebuf.blit(self.t6,self.geshu*1 + self.tppy,self.ypy1+self.tppy)
            self.oled.framebuf.blit(self.t7,self.geshu*2 + self.tppy,self.ypy1+self.tppy)
            self.oled.framebuf.blit(self.t8,self.geshu*3 + self.tppy,self.ypy1+self.tppy)
            
            self.oled.show()
            pass
        try:
            if self.menuindex == 1:
                self.moveball()
            if self.menuindex == 2:
                self.music()
            if self.menuindex == 3:
                self.triaxial()
            if self.menuindex == 4:
                self.hertinfo()
            if self.menuindex == 5:
                self.noise()
            if self.menuindex == 6:
                self.light()
            if self.menuindex == 7:
                self.temps()
            if self.menuindex == 8:
                self.line()
        except:
            print("error")

            
            
    
    def line(self):
        if self.ok:
            
            pass
            
        while self.ok:
            self.oled.fill(0)
        
            self.line_s.carry()
            self.oled.framebuf.blit(self.qiuti16xiaolian,self.line_s.get_x(), self.line_s.get_y(),)
            
            
            
            
            if self.line_d[0] < 22:
                for i in range(0, int(self.line_d[0]/3), 1):
                    self.oled.circle(self.line_d[1], self.line_d[2], i * (self.line_d[0]&3) + 1, 1)
                    
            else:
                self.line_d[0] = 0
                self.line_d[1] = random.randint(8, 112)
                self.line_d[2] = random.randint(8, 56)
            self.line_d[0] += 1 
            
            
            
            if self.line_d[3] < 8:
                self.oled.circle(self.line_d[4], self.line_d[5], self.line_d[3] , 1)
            else:
                self.line_d[3] = 0
                self.line_d[4] = random.randint(8, 112)
                self.line_d[5] = random.randint(8, 56)
            self.line_d[3] += 1 
            
            
            
            if self.line_d[6] < 20:
                self.oled.rect(int(self.line_d[7]-self.line_d[6]/2), int(self.line_d[8] -self.line_d[6]/2), self.line_d[6],self.line_d[6], 1)
            else:
                self.line_d[6] = 0
                self.line_d[7] = random.randint(20, 108)
                self.line_d[8] = random.randint(20, 44)
            self.line_d[6] += 1 
            
            
            self.line_a.carry()
            self.line_b.carry()
            self.line_c.carry()
            self.oled.triangle(self.line_a.get_x(), self.line_a.get_y(),self.line_b.get_x(), self.line_b.get_y(),self.line_c.get_x(), self.line_c.get_y(), 1)
            
            self.oled.show()
            time.sleep_ms(10)
            
            
            if self.version == "SCB_v2.0x":
                self.rgb[0] = (random.randint(0,255), 0, 50)
                self.rgb[1] = (0, random.randint(0,255), 50)
                self.rgb[2] = (50, 50, random.randint(0,255))
                self.rgb[3] = (0, random.randint(0,255), 100)
                self.rgb.write()
            
    
    
    def temps(self):
        if self.ok:
            self.oled.fill(0)
            self.oled.framebuf.blit(self.t7,6,32)
            self.oled.show()
            maxtemp = 0
        while self.ok:
            
            self.oled.fill(0)
            
            self.oled.rect(14, 5, 100, 5,1)
            self.oled.rect(14, 15, 100, 5,1)
            self.oled.rect(14, 25, 100, 5,1)
            self.oled.text("R",0,5)
            self.oled.text("G",0,15)
            self.oled.text("B",0,25)
            self.oled.fill_circle(self.ll + 13, self.lc + 2, 3, 1)
            self.oled.framebuf.blit(self.t7,54,35)
            
            self.oled.show()
            if self.button.value("上") and self.keydown:
                self.keydown = 0
                self.lc -=10
                if self.lc < 1:
                    self.lc = 5
                if self.lc == 5:
                    self.ll = int(self.lr /2)
                if self.lc == 15:
                    self.ll = int(self.lg /2)
                if self.lc == 25:
                    self.ll = int(self.lb /2)
            elif self.button.value("上")==0 and self.keydown==0:
                self.keydown = 1
                
            if self.button.value("下") and self.keyup:
                self.keyup = 0
                self.lc +=10
                if self.lc > 26:
                    self.lc = 25
                if self.lc == 5:
                    self.ll = int(self.lr /2)
                if self.lc == 15:
                    self.ll = int(self.lg /2)
                if self.lc == 25:
                    self.ll = int(self.lb /2)
            elif self.button.value("下")==0 and self.keyup==0:
                self.keyup = 1

            if self.button.value("左"):
                self.ll -=1
                if self.ll < 0:
                    self.ll = 0

            if self.button.value("右"):
                self.ll +=1
                if self.ll > 101:
                    self.ll = 101
                
            if self.lc == 5:
                self.lr = self.ll * 2
            if self.lc == 15:
                self.lg = self.ll * 2
            if self.lc == 25:
                self.lb = self.ll * 2
            
            
            self.rgb[0] = (self.lr, self.lg, self.lb)
            self.rgb[1] = (self.lr, self.lg, self.lb)
            self.rgb[2] = (self.lr, self.lg, self.lb)
            self.rgb[3] = (self.lr, self.lg, self.lb)
            self.rgb.write()
            
    
    def light(self):
    
        if self.ok:
            self.oled.fill(0)
            self.oled.text("light value",20,0)
            self.oled.framebuf.blit(self.t6,50,13)
            self.oled.show()
        
        while self.ok:
            guanmin = self.adc36.read()
            self.oled.fill(0)
            
            self.oled.framebuf.blit(self.t6,50,13)
            guanm = 4095-guanmin
            for i in range(0, len(str(guanm)), 1):
                self.oled.framebuf.blit(self.tx.get_24_text(int(str(guanm)[i])),32 + 18 * i,40)
            
            self.oled.text("light value",20,0)
            self.oled.show()
            time.sleep_ms(10)
        
    
    
    
    def noise(self):
        
        
        if self.ok:
            self.zaoyindata = []
            self.oled.fill(0)
            self.oled.text("level of noise",10,0)
            self.oled.show()
            
            
        while self.ok:
            for i in range(0, 98, 1):
                zaoyin = self.adc39.read()
                if zaoyin > 10:
                    self.zaoyindata.append(zaoyin)
            if(len(self.zaoyindata)>0):
                
                zaoyins = sum(self.zaoyindata)/len(self.zaoyindata)
                
                self.oled.fill(0)
                ls = int((zaoyins/450)*64)
                self.oled.fill_rect(0, 64-ls, 20,ls,1)
                
                aaa = int(ls*2.3)
                #print(zaoyins)
                for i in range(0, len(str(aaa)), 1):
                    self.oled.framebuf.blit(self.tx.get_24_text(int(str(aaa)[i])),35 + 18 * i,32)
                
                self.oled.framebuf.blit(self.tx.get_24_text("d"),90,32)
                self.oled.framebuf.blit(self.tx.get_24_text("B"),110,32)
                self.oled.text("level of noise",10,0)
                self.oled.show()
                
                if self.version == "SCB_v2.0j":
                    self.pwm27.duty(int(zaoyins*2 + 20))
                elif self.version == "SCB_v2.0x":
                    self.rgb[0] = ( 0, 0,aaa)
                    self.rgb[1] = ( 0, 0,aaa)
                    self.rgb[2] = ( 0, 0,aaa)
                    self.rgb[3] = ( 0, 0,aaa)
                    self.rgb.write()
                
            self.zaoyindata = []
    
    
    
    def hertinfo(self):
        #print("心率测试")
        
        if self.ok:
        
            hei_num = 0
            hei_num_eat = False
            low_num = 0
            hrd_list = []
            hert_t = 3
            time_tihs = 0
            time_list = []
            
            red = []
            ir = []
             
            my_hert = 0
            my_blood = 0
            pwmblood = 0
            pwmbloodx = 0
            isshowoled = 0
            ishert = 0
            
            oled_poxel = []
            for i in range(0, 111, 1):
                oled_poxel.append(0)
                
            
            for i in range(0, 10, 1):
                time_list.append(800)
            for i in range(0, 31, 1):
                hrd_list.append(12345)
                
            self.oled.fill(0)
            self.oled.text("hert and blood",10,0)
            self.oled.text("Put a finger>>-",10,52)
            self.oled.framebuf.blit(self.t4,50,15)
            self.oled.show()
        while self.ok:
            hrd,ird = self.blood.get_hrir()

            red.append(hrd)
            ir.append(ird)
            
            hrd_list[30] = hrd 
            for i in range(0, 30, 1):
                hrd_list[i] = hrd_list[i+1]
            mean_hr = sum(hrd_list)/31
            chaval = hrd - mean_hr
            #print(chaval)
            if chaval<50 and chaval >-50:
                ishert +=1
            else:
                ishert =0
                
            if chaval > 0:
                hei_num += 1
                if hei_num > hert_t:
                    hei_num_eat = True
                    hei_num = 0
            
            if hei_num_eat:
                if chaval < 0:
                    low_num += 1
                    if low_num > hert_t:
                        hei_num_eat = False
                        systime = time.ticks_ms()
                        hetime = systime - time_tihs
                        time_tihs = systime
                        low_num = 0
                        
                        if ishert < 18:
                            pwmblood = 1024
                            pwmbloodx = 255
                            if hetime <1600 and hetime>400:
                                time_list[9] = hetime
                                for i in range(0, 9, 1):
                                    time_list[i] = time_list[i+1]
                            
                            
                            #print(time_list)
                            hert = 600000 / (sum(time_list))
                            #print("心率： "+ str(hert))
                            my_hert = hert
            
            if self.version == "SCB_v2.0j":
                self.pwm27.duty(pwmblood)
                if pwmblood > 80:
                    pwmblood -= 80
                else:
                    pwmblood = 0
            elif self.version == "SCB_v2.0x":
                if pwmbloodx > 20:
                    pwmbloodx -= 20
                else:
                    pwmbloodx = 0
                self.rgb[0] = ( 0,pwmbloodx, 0)
                self.rgb[1] = ( 0,pwmbloodx, 0)
                self.rgb[2] = ( 0,pwmbloodx, 0)
                self.rgb[3] = ( 0,pwmbloodx, 0)
                self.rgb.write()
            
            oled_poxel[110] = (chaval + 300)/20
            self.oled.fill(0)
            self.oled.text("hert and blood",10,0)
            self.oled.text("HR:  " + str(int(my_hert)) + "bpm",0,10)
            self.oled.text("SaO2:" + str(int(my_blood)) + "%",0,20)
            
            for i in range(0, 110, 1):
                oled_poxel[i] = oled_poxel[i+1]
                self.oled.pixel(i,int(oled_poxel[i] + 36),1)
            for i in range(110, 128, 1):
                self.oled.pixel(i,int(oled_poxel[110] + 36),1)
            
            self.oled.show()
            
            
            isshowoled += 1
            if isshowoled > 128 and ishert < 18:
                isshowoled = 0
                
            if len(red)>100:
                hr, hr_valid, spo2, spo2_valid = self.blood.calc_hr_and_spo2(ir, red)
                #print("心率:" + str(hr) + "次/分钟")
                #print("血氧: " + str(spo2) + "  %")
                my_blood = spo2
                red = []
                ir = []
            
            
            
    
    def triaxial(self):
        #三轴
        self.ok = False
        xrest = 0
        yrest = 0
        while self.isstart:
            
            if self.ok:
                self.ok = False
                xrest = self.sanzhou.get_x()
                yrest = self.sanzhou.get_y()
            
            sxp = []
            syp = []
            for i in range(0, 10, 1):
                sx = self.sanzhou.get_x()
                sy = self.sanzhou.get_y()

                sxp.append(sx - xrest)
                syp.append(sy - yrest)

            sxpx = sum(sxp) / len(sxp)
            sypy = sum(syp) / len(syp)

            lingmidu = 66
            if sxpx >= 28/lingmidu:
                sxpx = 28/lingmidu
            if sxpx <= -28/lingmidu:
                sxpx = -28/lingmidu
            if sypy >= 56/lingmidu:
                sypy = 56/lingmidu
            if sypy <= -49/lingmidu:
                sypy = -49/lingmidu

            statex = -int(sypy * lingmidu) + 64 - 8

            statey = -int((sxpx * lingmidu)) + 32 - 4

            self.oled.fill(0)
            self.oled.text("^_^", statex,statey)
            self.oled.show()

    
    def music(self):
        #放歌
        if self.isstart:
            musics = Music()
            self.ok = False
            list_str = ["ENTERTAINER","DADADADUM","PRELUDE","ODE","NYAN","RINGTONE","FUNK","BLUES","BIRTHDAY","WEDDING","FUNERAL","PYTHON","BADDY","CHASE","BA_DING","WAWAWAWAA","JUMP_UP","JUMP_DOWN","POWER_UP","POWER_DOWN"    ]
            list_music = [music.ENTERTAINER,music.DADADADUM,music.PRELUDE,music.ODE,music.NYAN,music.RINGTONE,music.FUNK,music.BLUES,music.BIRTHDAY,music.WEDDING,music.FUNERAL,music.PYTHON,music.BADDY,music.CHASE,music.BA_DING,music.WAWAWAWAA,music.JUMP_UP,music.JUMP_DOWN,music.POWER_UP,music.POWER_DOWN]

            while self.isstart:
                
                if self.button.value("上") and self.keydown:
                    self.keydown = 0
                    print("上")
                    if musics.get_music() > 0 : musics.set_music(musics.get_music()-1)
                elif self.button.value("上")==0 and self.keydown==0:
                    self.keydown = 1
                    
                if self.button.value("下") and self.keyup:
                    self.keyup = 0
                    print("下")
                    if musics.get_music() < 19 :musics.set_music(musics.get_music()+1)
                elif self.button.value("下")==0 and self.keyup==0:
                    self.keyup = 1
                    
                if self.button.value("左") and self.keyleft:
                    self.keyleft = 0
                    print("左")
                    if musics.get_music() > 0 :musics.set_music(musics.get_music()-1)
                elif self.button.value("左")==0 and self.keyleft==0:
                    self.keyleft = 1
                    
                if self.button.value("右") and self.keyright:
                    self.keyright = 0
                    print("右")
                    if musics.get_music() < 19 :musics.set_music(musics.get_music()+1)
                elif self.button.value("右")==0 and self.keyright==0:
                    self.keyright = 1
                    
                self.oled.fill(0)
                self.oled.text("    music",0,0)
                self.oled.text("num: " + str(musics.get_music()),0,16)
                self.oled.text("name: " + list_str[musics.get_music()],0,32)
                self.oled.show()
                
                if self.ok:
                    music.play(list_music[musics.get_music()], 25)
                    self.ok = False
            
    
    def moveball(self):
    
        #小球移动
        okstart = True
        self.ok = False
        ballr = 4
        isbig = False
        
        if self.ok:
            self.spx = random.randint(0, 7)
            self.spy = random.randint(0, 3)
        
        while self.isstart:
            for i in range(0, 128, 16):
                for j in range(0, 64, 16):
                    self.oled.framebuf.blit(self.fangge16,i,j)
            
            if self.button.value("上") and self.keydown:
                self.keydown = 0
                print("上")
                okstart = True
                if( self.qiuti16s.get_qiuti16y()>0):
                    self.qiuti16s.set_qiuti16y(self.qiuti16s.get_qiuti16y()-1)
            elif self.button.value("上")==0 and self.keydown==0:
                self.keydown = 1
                
            if self.button.value("下") and self.keyup:
                self.keyup = 0
                print("下")
                okstart = True
                if(self.qiuti16s.get_qiuti16y()<3 ):
                    self.qiuti16s.set_qiuti16y(self.qiuti16s.get_qiuti16y()+1)
            elif self.button.value("下")==0 and self.keyup==0:
                self.keyup = 1
                
            if self.button.value("左") and self.keyleft:
                self.keyleft = 0
                print("左")
                okstart = True
                if(self.qiuti16s.get_qiuti16x()>0):
                    self.qiuti16s.set_qiuti16x(self.qiuti16s.get_qiuti16x()-1)
                
            elif self.button.value("左")==0 and self.keyleft==0:
                self.keyleft = 1
                
            if self.button.value("右") and self.keyright:
                self.keyright = 0
                print("右")
                okstart = True
                if(self.qiuti16s.get_qiuti16x()<7):
                    self.qiuti16s.set_qiuti16x(self.qiuti16s.get_qiuti16x()+1)
                
            elif self.button.value("右")==0 and self.keyright==0:
                self.keyright = 1
                
            x = self.qiuti16s.get_qiuti16x()
            y = self.qiuti16s.get_qiuti16y()
            self.oled.framebuf.blit(self.qiuti16xiaolian,x*16,y*16)
   
            if x == self.spx and y == self.spy:
                isbig = True
                
            if isbig:
                ballr+=1
            if ballr > 65:
                isbig = False
                self.spx = random.randint(0, 7)
                self.spy = random.randint(0, 3)
                ballr = 4
            
            #print(str(self.spx) + str(self.spy))
            r = int(ballr/16)
            if ballr < 16:
                self.oled.circle(self.spx * 16 + 7, self.spy * 16 + 7, ballr, 1)  
            else:
                for i in range(0, 2 , 1):
                    
                    self.oled.circle(self.spx * 16 + 7, self.spy * 16 + 7, i * 8 + ballr, 1)  
                    
            self.oled.show()
                
            if okstart:
                okstart = False
                if self.version == "SCB_v2.0j":
                    self.pwm27.duty( x*150 + y*88 + 100)
                elif self.version == "SCB_v2.0x":
                    self.rgb[0] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                    self.rgb[1] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                    self.rgb[2] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                    self.rgb[3] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                    self.rgb.write()
                    
                try:
                    music.pitch_time(25, x*150 + y*88 + 100, 100)
                except:
                    music.pitch(25, x*150 + y*88 + 100, 100)
            if self.ok:
                try:
                    music.pitch_time(25, x*150 + y*88 + 100, 500)
                except:
                    music.pitch(25, x*150 + y*88 + 100, 500)
                self.ok = False
            
        

    def attachInterrupt_funmenu(self,x):
        print('menu')
        self.menu = True
        self.ok = False
        self.isstart = False
    def attachInterrupt_funok(self,x):
        print('ok')
        self.ok = True
        self.isstart = True
    
        



class Qiuti16(object):
    qiuti16x = 4
    qiuti16y = 2
    def get_qiuti16x(self):
        return Qiuti16.qiuti16x
    def set_qiuti16x(self, qiuti16x):
        Qiuti16.qiuti16x = qiuti16x
    def get_qiuti16y(self):
        return Qiuti16.qiuti16y
    def set_qiuti16y(self, qiuti16y):
        Qiuti16.qiuti16y = qiuti16y

class Music(object):
    music = 0
    def get_music(self):
        return Music.music
    def set_music(self, music):
        Music.music = music






