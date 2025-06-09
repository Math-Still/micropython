import time
import machine
import tm1650
import sonar
import pca9685

class mars_rover_trail():

    def __init__(self, sda, scl ,sp = 46):

        self.lAIN1 = 4 
        self.lAIN2 = 3 
        self.lPWMA = 2 
        self.lBIN1 = 5 
        self.lBIN2 = 6 
        self.lPWMB = 7 
        self.rAIN1 = 10
        self.rAIN2 = 9
        self.rPWMA = 8
        self.rBIN1 = 11
        self.rBIN2 = 12
        self.rPWMB = 13
        self.H = 4095
        self.L = 0
        self.sp = sp  # 调整速度

        # 初始化电机驱动板
        self.i2c_pca9685 = machine.I2C(scl = machine.Pin(scl), sda = machine.Pin(sda), freq = 400000)
        print(self.i2c_pca9685.scan())
        self.motor = pca9685.PCA9685(self.i2c_pca9685,address=72)
        self.motor.freq(2000)
        # 初始化舵机驱动板
        self.carservo = pca9685.PCA9685(self.i2c_pca9685,address=73)
        self.carservo.freq(50)

        self.carservo.servo(0,95)
        self.carservo.servo(1,80)
        self.carservo.servo(2,0)
        # 初始化小车灯驱动板
        #self.carlight = pca9685.PCA9685(self.i2c_pca9685,address=74)
        #self.carlight.freq(2000)
        self.adc34 = machine.ADC(machine.Pin(34))
        self.adc35 = machine.ADC(machine.Pin(35))
        self.adc32 = machine.ADC(machine.Pin(32))
        self.adc33 = machine.ADC(machine.Pin(33))
        self.A = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.rw = "xunji"
        # 任务命令 说明：
        # 0   无任务，默认为寻迹模式
        # 1   前进任务
        # 2   后转任务
        # 3   左转任务
        # 4   右转任务
        # 5   右转 修桥任务
        # 6   加速模式        #使用加速模式快速走一秒左右
        # 7   清理障碍物   这个不可以用
        # 8   取货
        # 9   放下货物
        # 10  向前走
        # 11  向后走
        #  第0个数组[任务位置，任务状态]，  其他数组为任务的[任务计数，任务命令]  如果任务命令大于10则执行任务data
        self.task = [[1,0],   [0,4],[0,1],[0,1],[0,1],[0,8],[0,2],[0,3],[0,9],[0,2],[0,3],[0,1],[0,1],[0,3],[0,2],["end","end"]]   # 取货任务模型

        #self.task = [[1,0],   [0,4],[0,4],[0,1],[0,3],[0,3],[0,5],[0,4],[0,4],[0,4],[0,6],[0,2],[0,6],[0,4],[0,3],[0,3],[0,2],["end","end"]]   # 测土壤湿度任务模型

        self.task == None
        self.xunjistate = 0
        self.tdata = []
        self.isstop_00 = 0
        self.xunjispeed = 1

        self.qianpao_num = 0
        
        
        self.sp_l = 30
        self.sp_r = 30
        self.sustete = 0
        

    def carA(self, dirs,speed):
        if dirs==0:
            self.motor.pwm(self.lAIN1,0,self.H)
            self.motor.pwm(self.lAIN2,0,self.L)
            self.motor.pwm(self.lPWMA,0,int(speed))
            
        elif dirs==1:
            self.motor.pwm(self.lAIN1,0,self.L)
            self.motor.pwm(self.lAIN2,0,self.H)
            self.motor.pwm(self.lPWMA,0,int(speed))
            
    def carB(self, dirs,speed):
        if dirs==0:
            self.motor.pwm(self.lBIN1,0,self.H)
            self.motor.pwm(self.lBIN2,0,self.L)
            self.motor.pwm(self.lPWMB,0,int(speed))
            
        elif dirs==1:
            self.motor.pwm(self.lBIN1,0,self.L)
            self.motor.pwm(self.lBIN2,0,self.H)
            self.motor.pwm(self.lPWMB,0,int(speed))

    def carC(self, dirs,speed):
        if dirs==0:
            self.motor.pwm(self.rAIN1,0,self.H)
            self.motor.pwm(self.rAIN2,0,self.L)
            self.motor.pwm(self.rPWMA,0,int(speed))
            
        elif dirs==1:
            self.motor.pwm(self.rAIN1,0,self.L)
            self.motor.pwm(self.rAIN2,0,self.H)
            self.motor.pwm(self.rPWMA,0,int(speed))
            
    def carD(self, dirs,speed):
        if dirs==0:
            self.motor.pwm(self.rBIN1,0,self.H)
            self.motor.pwm(self.rBIN2,0,self.L)
            self.motor.pwm(self.rPWMB,0,int(speed))
            
        elif dirs==1:
            self.motor.pwm(self.rBIN1,0,self.L)
            self.motor.pwm(self.rBIN2,0,self.H)
            self.motor.pwm(self.rPWMB,0,int(speed))

    # 后转任务模型
    def houzhuan(self):
        self.carA(1,30 * self.sp)
        self.carB(1,30 * self.sp)
        self.carC(1,30 * self.sp)
        self.carD(1,30 * self.sp)
        time.sleep_ms(400)
        for i in range(0,500,1):
            time.sleep_ms(30)
            
            if self.adc35.read() > 500:
                self.B = 1
            else:
                self.B = 0
            if self.B == 1:
                i == 500
                print("houzhuan ok")
                
                self.xunjistate = 1
                self.task[0][1] = 0
                return
            else:
                self.carA(0,35 * self.sp)
                self.carB(0,35 * self.sp)
                self.carC(1,35 * self.sp)
                self.carD(1,35 * self.sp)

            print(i)
        self.rw = "xunji"


    # 后转任务 + 修桥
    def houzhuan_bridge(self):
        self.carservo.servo(1,80)
        self.carservo.servo(2,50)
        self.carA(1,30 * self.sp)
        self.carB(1,30 * self.sp)
        self.carC(1,30 * self.sp)
        self.carD(1,30 * self.sp)
        time.sleep_ms(1000)
        self.carA(0,30 * self.sp)
        self.carB(0,30 * self.sp)
        self.carC(0,30 * self.sp)
        self.carD(0,30 * self.sp)
        time.sleep_ms(500)
        self.carA(1,0)
        self.carB(1,0)
        self.carC(1,0)
        self.carD(1,0)
        time.sleep_ms(1000)
        
        for i in range(0,500,1):
            time.sleep_ms(30)
            if self.adc35.read() > 500:
                self.B = 1
            else:
                self.B = 0
            if self.B == 1:
                i == 500
                print("houzhuan_bridge ok")
                
                self.xunjistate = 1
                self.task[0][1] = 0
                
                
                return
            else:
                self.carA(0,35 * self.sp)
                self.carB(0,35 * self.sp)
                self.carC(1,35 * self.sp)
                self.carD(1,35 * self.sp)
            print(i)
        self.rw = "xunji"
        self.carservo.servo(1,100)
        self.carservo.servo(2,50)

    # 加速模式
    def qianpao(self):
        if self.qianpao_num < 500:
            self.xunjispeed = 1234
            self.rw = "xunji"
        else:
            self.xunjispeed = 1
        for i in range(1,100,1):
            self.init_data()

            if self.B == 1 and self.C == 1:
                self.carA(1,30 * self.sp  + self.xunjispeed)
                self.carB(1,30 * self.sp  + self.xunjispeed)
                self.carC(1,30 * self.sp  + self.xunjispeed)
                self.carD(1,30 * self.sp  + self.xunjispeed)
            if self.B == 0 and self.C == 0:
                self.carA(1,30 * self.sp  + self.xunjispeed)
                self.carB(1,30 * self.sp  + self.xunjispeed)
                self.carC(1,30 * self.sp  + self.xunjispeed)
                self.carD(1,30 * self.sp  + self.xunjispeed)
            if self.B == 1 and self.C == 0:
                self.carA(1,16 * self.sp  + self.xunjispeed)
                self.carB(1,16 * self.sp  + self.xunjispeed)
                self.carC(1,30 * self.sp  + self.xunjispeed)
                self.carD(1,30 * self.sp  + self.xunjispeed)
            if self.B == 0 and self.C == 1:
                self.carA(1,30 * self.sp  + self.xunjispeed)
                self.carB(1,30 * self.sp  + self.xunjispeed)
                self.carC(1,16 * self.sp  + self.xunjispeed)
                self.carD(1,16 * self.sp  + self.xunjispeed)
            time.sleep_ms(10)
        print("任务完成" + str(self.task[0][0]))
        
        self.task[0][0] += 1
        self.xunjistate = 0
        self.task[0][1] = 0 
        self.xunjispeed = 1
                
                
                
    def init_data(self):
        if self.adc34.read() > 500:
            self.A = 1
        else:
            self.A = 0
        if self.adc35.read() > 500:
            self.B = 1
        else:
            self.B = 0
        if self.adc32.read() > 500:
            self.C = 1
        else:
            self.C = 0
        if self.adc33.read() > 500:
            self.D = 1
        else:
            self.D = 0
            
    

    # # 清理障碍物步骤
    # def qingli():
    #     for i in range(1,100,1):
    #         chaosheng = sonar.Sonar(25, 26).checkdist()
    #         if chaosheng > 7:
    #             carA(1,30 * sp)
    #             carB(1,30 * sp)
    #             carC(1,30 * sp)
    #             carD(1,30 * sp)
    #         else:
    #             carA(1,1)
    #             carB(1,1)
    #             carC(1,1)
    #             carD(1,1)
    #             time.sleep_ms(666)
    #             carservo.servo(1,40)
    #             carA(0,35 * sp)
    #             carB(0,35 * sp)
    #             carC(0,35 * sp)
    #             carD(0,35 * sp)
    #             time.sleep_ms(800)
    #             carservo.servo(1,80)
    #             
    #             return
    #     
    #     task[0][0] += 1
        
    #取货任务
    def quhuo(self):
        self.carA(1,0)
        self.carB(1,0)
        self.carC(1,0)
        self.carD(1,0)

        time.sleep_ms(1000)
        self.carA(1,30 * self.sp)
        self.carB(1,30 * self.sp)
        self.carC(1,30 * self.sp)
        self.carD(1,30 * self.sp)
        time.sleep_ms(600)
        self.carA(1,0)
        self.carB(1,0)
        self.carC(1,0)
        self.carD(1,0)
        self.carservo.servo(2,0)
        time.sleep_ms(500)
        self.carservo.servo(1,45)
        time.sleep_ms(1000)
        self.carservo.servo(2,50)
        time.sleep_ms(1000)
        self.carservo.servo(1,80)
        self.carA(0,30 * self.sp)
        self.carB(0,30 * self.sp)
        self.carC(0,30 * self.sp)
        self.carD(0,30 * self.sp)

        self.task[0][0] += 1
        time.sleep_ms(1200)

    #卸货任务
    def xiehuo(self):
        self.carA(1,0)
        self.carB(1,0)
        self.carC(1,0)
        self.carD(1,0)
        time.sleep_ms(500)
        self.carA(1,35 * self.sp)
        self.carB(1,35 * self.sp)
        self.carC(1,35 * self.sp)
        self.carD(1,35 * self.sp)
        time.sleep_ms(300)
        self.carA(1,0)
        self.carB(1,0)
        self.carC(1,0)
        self.carD(1,0)
        time.sleep_ms(1000)
        self.carservo.servo(1,70)
        time.sleep_ms(1000)
        self.carservo.servo(2,0)
        time.sleep_ms(1000)
        self.task[0][0] += 1
        self.carA(0,35 * self.sp)
        self.carB(0,35 * self.sp)
        self.carC(0,35 * self.sp)
        self.carD(0,35 * self.sp)
        time.sleep_ms(700)
        self.carservo.servo(1,110)
        
    #前进
    def qianjin(self):
        self.carA(1,35 * self.sp)
        self.carB(1,35 * self.sp)
        self.carC(1,35 * self.sp)
        self.carD(1,35 * self.sp)
        time.sleep_ms(1000)
        self.carA(1,0)
        self.carB(1,0)
        self.carC(1,0)
        self.carD(1,0)
        time.sleep_ms(500)
        self.task[0][0] += 1
        self.sustete = 0
        
    #后退
    def houtui(self):
        self.carA(0,35 * self.sp)
        self.carB(0,35 * self.sp)
        self.carC(0,35 * self.sp)
        self.carD(0,35 * self.sp)
        time.sleep_ms(1300)
        self.carA(1,0)
        self.carB(1,0)
        self.carC(1,0)
        self.carD(1,0)
        time.sleep_ms(500)
        self.task[0][0] += 1
        self.sustete = 0
        
    
    def execute(self,tasks):
    
        if self.task != tasks:
            self.task = tasks
            print("执行任务：")
            print(self.task)
        self.init_data()
        # print(A,end ="")
        # print(B,end ="")
        # print(C,end ="")
        # print(D)
        if self.task[self.task[0][0]][1] == "end":
            print("end")
            print("三秒后重新执行任务")
            self.carA(1,0)
            self.carB(1,0)
            self.carC(1,0)
            self.carD(1,0)
            time.sleep_ms(3000)
            print("重新执行任务：")
            print(self.task)
            self.task[0][0] = 1
        else:

            time.sleep_ms(8)
            if self.A == 0 and self.B == 0  and self.C == 0 and self.D == 0: # 如果为全亮，停止运行
                
                print("stop" + str(self.isstop_00))
                if self.isstop_00 > 88:
                    self.isstop_00 = 0
                    self.carA(1,1)
                    self.carB(1,1)
                    self.carC(1,1)
                    self.carD(1,1)
                else :
                    self.isstop_00 += 1
                    
            #elif A == 1 and B == 1  and C == 1 and D == 1: # 如果为全亮，停止运行
                #print("11")
                #my_scb_car.car_driver(0,1,1)
                #my_scb_car.car_driver(1,1,1)
                #my_scb_car.car_driver(2,1,1)
                #my_scb_car.car_driver(3,1,1)
                
            else:
            
                self.isstop_00 =0
                if self.rw == "xunji":
                    #if self.B == 1 and self.C == 1:
                    #    if self.sp_l < 35:
                    #        self.sp_l += 0.6
                    #    if self.sp_r < 35:
                    #        self.sp_r += 0.6
                    #if self.B == 0 and self.C == 0:
                    #    if self.sp_l < 35:
                    #        self.sp_l += 0.6
                    #    if self.sp_r < 35:
                    #        self.sp_r += 0.6
                    #if self.B == 1 and self.C == 0:
                    #    if self.sp_r < 35:
                    #        self.sp_r += 0.3
                    #    if self.sp_l > 16 :
                    #        self.sp_l -= 0.8
                    #if self.B == 0 and self.C == 1:
                    #    if self.sp_l < 35:
                    #        self.sp_l += 0.3
                    #    if self.sp_r > 16:
                    #        self.sp_r -= 0.8
                    #
                    #self.carA(1,self.sp_l * self.sp  + self.xunjispeed)
                    #self.carB(1,self.sp_l * self.sp  + self.xunjispeed)
                    #self.carC(1,self.sp_r * self.sp  + self.xunjispeed)
                    #self.carD(1,self.sp_r * self.sp  + self.xunjispeed)
                    
                    if self.B == 1 and self.C == 1:
                        self.carA(1,30 * self.sp  + self.xunjispeed)
                        self.carB(1,30 * self.sp  + self.xunjispeed)
                        self.carC(1,30 * self.sp  + self.xunjispeed)
                        self.carD(1,30 * self.sp  + self.xunjispeed)
                    if self.B == 0 and self.C == 0:
                        self.carA(1,30 * self.sp  + self.xunjispeed)
                        self.carB(1,30 * self.sp  + self.xunjispeed)
                        self.carC(1,30 * self.sp  + self.xunjispeed)
                        self.carD(1,30 * self.sp  + self.xunjispeed)
                    if self.B == 1 and self.C == 0:
                        self.carA(1,18 * self.sp  + self.xunjispeed)
                        self.carB(1,18 * self.sp  + self.xunjispeed)
                        self.carC(1,30 * self.sp  + self.xunjispeed)
                        self.carD(1,30 * self.sp  + self.xunjispeed)
                    if self.B == 0 and self.C == 1:
                        self.carA(1,30 * self.sp  + self.xunjispeed)
                        self.carB(1,30 * self.sp  + self.xunjispeed)
                        self.carC(1,18 * self.sp  + self.xunjispeed)
                        self.carD(1,18 * self.sp  + self.xunjispeed)

                if self.xunjistate:
                # 如果寻迹次数很多了，说明上个任务完成
                    self.task[0][1] += 1
                    if self.task[0][1] > 66:
                        print("任务完成" + str(self.task[0][0]))
                        self.task[0][0] += 1
                        self.xunjistate = 0
                        self.task[0][1] = 0 
                        #xunjispeed = 1 # 默认速度为1            
                    
                
                #print("xuji" + str(self.xunjistate))
                
                if self.xunjistate == 0:
                    if self.D == 1 and self.task[self.task[0][0]][1] == 4:
                        #完成右转后就进行寻迹
                        print("D")
                        self.rw = "youzhuan"
                        if self.task[self.task[0][0]][1] == 4: # 如果是右转任务，就执行
                            print("r")
                            self.carA(1,30 * self.sp  + self.xunjispeed)
                            self.carB(1,30 * self.sp  + self.xunjispeed)
                            self.carC(1,30 * self.sp  + self.xunjispeed)
                            self.carD(1,30 * self.sp  + self.xunjispeed)
                            time.sleep_ms(500)
                            for i in range(1,200,1):
                                if self.adc32.read() > 500:
                                    self.C = 1
                                else:
                                    self.C = 0
                                self.carA(1,35 * self.sp)
                                self.carB(1,35 * self.sp)
                                self.carC(0,35 * self.sp)
                                self.carD(0,35 * self.sp)
                                if i > 30:
                                    if self.C == 1:
                                        #self.task[0][0] += 1
                                        self.rw = "xunji"
                                        print("跳出r")
                                        self.xunjistate = 1
                                        break;
                                time.sleep_ms(10)
                                print("r-" + str(i))
                            
                            
                            #self.task[self.task[0][0]][0] += 1
                            #if self.task[self.task[0][0]][0] > 10:
                            #    self.rw = "xunji"
                            #
                            
                            #time.sleep_ms(80)
                        elif self.task[self.task[0][0]][1] == 1:
                            self.task[self.task[0][0]][0] += 1
                            if self.task[self.task[0][0]][0] > 10:
                                self.rw = "xunji"
                                
                                
                        #self.xunjistate = 1
                        #self.task[0][1] = 0

                            
                    else:
                        self.task[self.task[0][0]][0] = 0
                        self.rw = "xunji"
                            
                    if self.A == 1 and self.task[self.task[0][0]][1] == 3:
                        # 完成左转后就进行寻迹
                        print("A")
                        self.rw = "zuozhuan"
                        if self.task[self.task[0][0]][1] == 3: # 如果是左转任务，就执行
                            print("l")
                            self.carA(1,30 * self.sp  + self.xunjispeed)
                            self.carB(1,30 * self.sp  + self.xunjispeed)
                            self.carC(1,30 * self.sp  + self.xunjispeed)
                            self.carD(1,30 * self.sp  + self.xunjispeed)
                            time.sleep_ms(500)
                            for i in range(1,200,1):
                                if self.adc35.read() > 500:
                                    self.B = 1
                                else:
                                    self.B = 0
                                self.carA(0,35 * self.sp)
                                self.carB(0,35 * self.sp)
                                self.carC(1,35 * self.sp)
                                self.carD(1,35 * self.sp)
                                if i > 30:
                                    if self.B == 1:
                                        #self.task[0][0] += 1
                                        self.rw = "xunji"
                                        print("跳出l")
                                        self.xunjistate = 1
                                        break;
                                time.sleep_ms(10)
                                print("l-" + str(i))
                        
                            #self.task[self.task[0][0]][0] += 1
                            #if self.task[self.task[0][0]][0] > 10:
                            #    self.rw = "xunji"
                                
                            #time.sleep_ms(80)
                        elif self.task[self.task[0][0]][1] == 1:
                            self.task[self.task[0][0]][0] += 1
                            if self.task[self.task[0][0]][0] > 10:
                                self.rw = "xunji"
                                
                            #self.xunjistate = 1
                            #self.task[0][1] = 0
                            
                    else:
                        self.task[self.task[0][0]][0] = 0
                        self.rw = "xunji"
                    
                    if self.D == 1 or self.A == 1:
                        if self.task[self.task[0][0]][1] == 0:  # 无任务
                            print("无任务")
                            self.task[0][1] = -10
                            self.xunjistate = 1
                        if self.task[self.task[0][0]][1] == 1:  # 前进
                            print("前进")
                            self.task[0][1] = -10
                            self.xunjistate = 1
                        if self.task[self.task[0][0]][1] == 2:  # 后转
                            print("后转")
                            self.houzhuan()
                            self.task[0][1] = -10
                            self.xunjistate = 1
                        elif self.task[self.task[0][0]][1] == 5:  # 后转修桥任务
                            print("后转修桥")
                            self.houzhuan_bridge()
                            self.task[0][1] = -10
                            self.xunjistate = 1
                        #elif self.task[self.task[0][0]][1] == 6:# 加速模式
                        #    print("加速模式")
                        #    self.qianpao()
                        #    self.task[0][1] = 0
                        #    self.xunjistate = 1
                        elif self.task[self.task[0][0]][1] == 8:# 取货
                            print("取货")
                            self.quhuo()
                            self.task[0][1] = 0
                            self.xunjistate = 0
                        elif self.task[self.task[0][0]][1] == 9:# 卸货
                            print("卸货")
                            self.xiehuo()
                            self.task[0][1] = 0
                            self.xunjistate = 0
                        elif self.task[self.task[0][0]][1] == 10:# 前进
                            print("前进")
                            self.qianjin()
                            self.task[0][1] = 0
                            self.xunjistate = 0
                            
                            
                            

                            
                            
                    if self.task[self.task[0][0]][1] == 6:# 加速模式
                            print("加速模式")
                            self.qianpao()
                    #print(self.xunjispeed)
                    
            if self.task[self.task[0][0]][1] == 11:# 后退
                print("准备后退")
                if self.sustete == 1:
                    print("后退")
                    self.houtui()
                    self.task[0][1] = 0
                    self.xunjistate = 0
                else:
                    self.sustete = 1
                    
                    
            #print(task)
        

                    
                    
                    
                    
                    
