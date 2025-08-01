
import machine
import time
import ssd1306
import random
import neopixel

# 简化版科创板演示代码 - 最小依赖版本

class SimpleSCBord():
    def __init__(self):
        # 基本配置
        self.version = "SCB_v2.0x"  # 默认版本
        
        # 按键状态
        self.keyleft = 1
        self.keyright = 1
        self.keyup = 1
        self.keydown = 1
        
        # 菜单状态
        self.menu = False
        self.ok = False
        self.isstart = False
        self.menuindex = 0
        
        # 初始化硬件
        self.init_hardware()
        
        # 显示欢迎界面
        self.show_welcome()
        
    def init_hardware(self):
        """初始化硬件"""
        try:
            # 初始化OLED (使用ssd1306库)
            self.i2c = machine.I2C(scl=machine.Pin(15), sda=machine.Pin(4), freq=100000)
            self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)
            
            # 初始化按键引脚 (参考SCBoard.py的Button类)
            self.pin12 = machine.Pin(12, machine.Pin.IN)  # 上
            self.pin13 = machine.Pin(13, machine.Pin.IN)  # 下
            self.pin14 = machine.Pin(14, machine.Pin.IN)  # 左
            self.pin18 = machine.Pin(18, machine.Pin.IN)  # 右
            self.pin5 = machine.Pin(5, machine.Pin.IN)    # 确认
            self.pin19 = machine.Pin(19, machine.Pin.IN)  # 返回
            
            # 初始化RGB LED (NeoPixel)
            try:
                self.rgb_leds = neopixel.NeoPixel(machine.Pin(23), 4)
                # 初始化时关闭所有LED
                for i in range(4):
                    self.rgb_leds[i] = (0, 0, 0)
                self.rgb_leds.write()
            except:
                self.rgb_leds = None
                
            # 初始化蜂鸣器
            self.buzzer = machine.Pin(25, machine.Pin.OUT)
            
            # 初始化光敏传感器 (ADC)
            try:
                self.light_sensor = machine.ADC(machine.Pin(36))  # VP引脚
                self.light_sensor.atten(machine.ADC.ATTN_11DB)  # 0-3.3V
            except:
                self.light_sensor = None
                
            # 初始化声音传感器 (ADC)
            try:
                self.sound_sensor = machine.ADC(machine.Pin(39))  # VN引脚
                self.sound_sensor.atten(machine.ADC.ATTN_11DB)  # 0-3.3V
            except:
                self.sound_sensor = None
                
            # 初始化心率和血氧传感器
            # try:
                # self.blood_sensor = Blood.blood()
            # except:
                # self.blood_sensor = None
            
            print("硬件初始化完成")
            
        except Exception as e:
            print(f"硬件初始化失败: {e}")
    
    def show_welcome(self):
        """显示欢迎界面"""
        try:
            self.oled.fill(0)
            self.oled.text("Hello World!", 10, 10)
            self.oled.text("Simple SCB", 20, 30)
            self.oled.text("Press OK to start", 5, 50)
            self.oled.show()
            
            # 播放欢迎音
            self.beep(200, 100)
            time.sleep_ms(50)
            self.beep(400, 100)
            
        except Exception as e:
            print(f"欢迎界面显示失败: {e}")
    
    def beep(self, freq, duration):
        """蜂鸣器发声"""
        try:
            # 简单的PWM发声
            for _ in range(duration // 10):
                self.buzzer.value(1)
                time.sleep_us(1000000 // freq // 2)
                self.buzzer.value(0)
                time.sleep_us(1000000 // freq // 2)
        except:
            pass
    
    def read_buttons(self):
        """读取按键状态 (参考SCBoard.py的Button类)"""
        try:
            # 按键读取逻辑
            up = self.pin12.value() == 1
            down = self.pin13.value() == 1
            left = self.pin14.value() == 1
            right = self.pin18.value() == 1
            ok = self.pin5.value() == 1
            back = self.pin19.value() == 1
            
            return up, down, left, right, ok, back
        except:
            return False, False, False, False, False, False
    
    def show_menu(self):
        """显示菜单"""
        try:
            self.oled.fill(0)
            
            menu_items = [
                "1. Text Demo",
                "2. Music Demo", 
                "3. LED Random",
                "4. Light Sensor",
                "5. Sound Sensor",
                "6. Heart & Blood",
                "7. Snake Game"
            ]
            
            for i, item in enumerate(menu_items):
                if i == self.menuindex:
                    self.oled.text(">" + item, 5, i * 9)
                else:
                    self.oled.text(" " + item, 5, i * 9)
            
            self.oled.show()
                    
        except Exception as e:
            print(f"菜单显示失败: {e}")
    
    def text_demo(self):
        """文字演示"""
        try:
            self.oled.fill(0)
            self.oled.text("Text Demo", 20, 10)
            self.oled.text("Hello World!", 10, 30)
            self.oled.text("Simple SCB", 15, 50)
            self.oled.show()
            
            time.sleep_ms(2000)
            
            # 滚动文字效果
            for i in range(128):
                # 检查退出按键
                up, down, left, right, ok, back = self.read_buttons()
                if back:  # 返回键退出
                    break
                    
                self.oled.fill(0)
                self.oled.text("Scrolling", i, 30)
                self.oled.show()
                time.sleep_ms(50)
                
        except Exception as e:
            print(f"文字演示失败: {e}")
    
    def music_demo(self):
        """音乐演示 - 随机播放多种音乐"""
        try:
            # 定义多种音乐
            music_library = {
                "TWINKLE": [
                    (262, 200), (262, 200), (392, 200), (392, 200),  # Do Do Sol Sol
                    (440, 200), (440, 200), (392, 400),             # La La Sol
                    (349, 200), (349, 200), (330, 200), (330, 200), # Fa Fa Mi Mi
                    (294, 200), (294, 200), (262, 400),             # Re Re Do
                    (392, 200), (392, 200), (349, 200), (349, 200), # Sol Sol Fa Fa
                    (330, 200), (330, 200), (294, 400),             # Mi Mi Re
                    (262, 200), (262, 200), (392, 200), (392, 200), # Do Do Sol Sol
                    (440, 200), (440, 200), (392, 400),             # La La Sol
                    (349, 200), (349, 200), (330, 200), (330, 200), # Fa Fa Mi Mi
                    (294, 200), (294, 200), (262, 400)              # Re Re Do
                ],
                "BIRTHDAY": [
                    (262, 300), (262, 100), (294, 300), (262, 300), (349, 300), (330, 600),  # Happy Birthday to you
                    (262, 300), (262, 100), (294, 300), (262, 300), (392, 300), (349, 600),  # Happy Birthday to you
                    (262, 300), (262, 100), (523, 300), (440, 300), (349, 300), (330, 300), (294, 600),  # Happy Birthday dear
                    (466, 300), (466, 100), (440, 300), (349, 300), (392, 300), (349, 600)   # Happy Birthday to you
                ],
                "BLUES": [
                    (220, 400), (196, 200), (220, 400), (196, 200),  # Blues progression
                    (220, 400), (196, 200), (220, 400), (196, 200),
                    (247, 400), (220, 200), (247, 400), (220, 200),
                    (262, 400), (247, 200), (262, 400), (247, 200),
                    (220, 400), (196, 200), (220, 400), (196, 200)
                ],
                "FUNK": [
                    (330, 150), (0, 50), (330, 150), (0, 50), (330, 150), (0, 50), (330, 150), (0, 50),  # Funky rhythm
                    (349, 150), (0, 50), (349, 150), (0, 50), (349, 150), (0, 50), (349, 150), (0, 50),
                    (392, 150), (0, 50), (392, 150), (0, 50), (392, 150), (0, 50), (392, 150), (0, 50),
                    (440, 300), (392, 300), (349, 300), (330, 300)
                ],
                "ODE": [
                    (262, 400), (330, 400), (392, 400), (523, 800),  # Ode to Joy theme
                    (523, 400), (587, 400), (659, 400), (698, 800),
                    (698, 400), (659, 400), (587, 400), (523, 800),
                    (523, 400), (392, 400), (440, 400), (494, 800)
                ],
                "NYAN": [
                    (523, 100), (659, 100), (784, 100), (1047, 100),  # Nyan Cat style
                    (784, 100), (659, 100), (523, 100), (440, 100),
                    (523, 100), (659, 100), (784, 100), (1047, 100),
                    (784, 100), (659, 100), (523, 100), (440, 100)
                ],
                "WEDDING": [
                    (262, 400), (330, 400), (392, 400), (523, 800),  # Wedding March
                    (523, 400), (587, 400), (659, 400), (698, 800),
                    (698, 400), (659, 400), (587, 400), (523, 800),
                    (523, 400), (392, 400), (330, 400), (262, 800)
                ],
                "FUNERAL": [
                    (196, 600), (174, 600), (196, 600), (174, 600),  # Funeral March
                    (174, 600), (155, 600), (174, 600), (155, 600),
                    (155, 600), (146, 600), (155, 600), (146, 600),
                    (146, 600), (130, 600), (146, 600), (130, 600)
                ],
                "DADADADUM": [
                    (196, 200), (196, 200), (196, 200), (196, 200),  # Beethoven's 5th
                    (196, 200), (196, 200), (196, 200), (196, 200),
                    (196, 200), (196, 200), (196, 200), (196, 200),
                    (196, 200), (196, 200), (196, 200), (196, 200),
                    (220, 400), (220, 400), (220, 400), (220, 400)
                ],
                "PRELUDE": [
                    (262, 300), (330, 300), (392, 300), (523, 300),  # Prelude in C
                    (523, 300), (392, 300), (330, 300), (262, 300),
                    (262, 300), (330, 300), (392, 300), (523, 300),
                    (523, 300), (392, 300), (330, 300), (262, 300)
                ]
            }
            
            # 随机选择一首音乐
            music_names = list(music_library.keys())
            selected_music = random.choice(music_names)
            notes = music_library[selected_music]
            
            self.oled.fill(0)
            self.oled.text("Music Demo", 20, 10)
            self.oled.text("Playing: " + selected_music, 5, 30)
            self.oled.text("Press BACK to exit", 5, 50)
            self.oled.show()
            
            for freq, duration in notes:
                # 检查退出按键
                up, down, left, right, ok, back = self.read_buttons()
                if back:  # 返回键退出
                    break
                    
                if freq > 0:  # 只播放非零频率的音符
                    self.beep(freq, duration)
                else:
                    time.sleep_ms(duration)  # 静音
                time.sleep_ms(50)
                
        except Exception as e:
            print(f"音乐演示失败: {e}")
    
    def led_random_demo(self):
        """RGB LED随机演示"""
        try:
            self.oled.fill(0)
            self.oled.text("RGB LED Random", 15, 10)
            self.oled.text("Random colors", 10, 30)
            self.oled.text("Press BACK to exit", 5, 50)
            self.oled.show()
            
            if self.rgb_leds:
                # RGB LED随机颜色演示
                for _ in range(16):  # 增加演示次数
                    # 检查退出按键
                    up, down, left, right, ok, back = self.read_buttons()
                    if back:  # 返回键退出
                        break
                    
                    # 随机选择LED和颜色
                    led_index = random.randint(0, 3)  # 选择0-3号LED
                    r = random.randint(0, 255)  # 随机红色值
                    g = random.randint(0, 255)  # 随机绿色值
                    b = random.randint(0, 255)  # 随机蓝色值
                    
                    # 先关闭所有LED
                    for i in range(4):
                        self.rgb_leds[i] = (0, 0, 0)
                    
                    # 点亮选中的LED
                    self.rgb_leds[led_index] = (r, g, b)
                    self.rgb_leds.write()
                    
                    # 在OLED上显示当前状态
                    self.oled.fill(0)
                    self.oled.text("RGB LED Random", 15, 5)
                    self.oled.text(f"LED {led_index}: ({r},{g},{b})", 5, 20)
                    self.oled.text("Random colors", 10, 35)
                    self.oled.text("Press BACK to exit", 5, 55)
                    self.oled.show()
                    
                    # 随机延时
                    delay = random.randint(100, 800)
                    time.sleep_ms(delay)
                    
                # 演示结束后关闭所有LED
                for i in range(4):
                    self.rgb_leds[i] = (0, 0, 0)
                self.rgb_leds.write()
                    
        except Exception as e:
            print(f"RGB LED随机演示失败: {e}")
    
    def light_sensor_demo(self):
        """光敏传感器演示"""
        try:
            if not self.light_sensor:
                self.oled.fill(0)
                self.oled.text("Light Sensor", 15, 10)
                self.oled.text("Not available", 10, 30)
                self.oled.text("Press BACK to exit", 5, 50)
                self.oled.show()
                time.sleep_ms(2000)
                return
                
            # 光敏传感器实时显示
            for _ in range(200):  # 运行200次循环
                # 检查退出按键
                up, down, left, right, ok, back = self.read_buttons()
                if back:  # 返回键退出
                    break
                
                # 读取光敏传感器值
                light_value = self.light_sensor.read()
                
                # 反比转换：光线越强，显示值越小
                inverted_value = 4095 - light_value
                
                # 清屏并显示信息
                self.oled.fill(0)
                self.oled.text("Light Sensor", 15, 5)
                self.oled.text("Raw: " + str(light_value), 5, 15)
                self.oled.text("Inverted: " + str(inverted_value), 5, 25)
                
                # 绘制光强度条形图 (使用反比转换后的值)
                bar_width = int(inverted_value / 4095 * 120)  # 映射到0-120像素
                self.oled.text("Light Level:", 5, 40)
                self.oled.fill_rect(5, 50, bar_width, 8, 1)
                self.oled.rect(5, 50, 120, 8, 1)  # 边框
                
                # 显示状态 (基于反比转换后的值)
                if inverted_value < 1000:
                    status = "Bright"
                elif inverted_value < 2000:
                    status = "Normal"
                elif inverted_value < 3000:
                    status = "Dim"
                else:
                    status = "Dark"
                    
                self.oled.text("Status: " + status, 5, 60)
                self.oled.show()
                
                time.sleep_ms(100)
                
        except Exception as e:
            print(f"光敏传感器演示失败: {e}")
    
    def sound_sensor_demo(self):
        """声音传感器演示"""
        try:
            if not self.sound_sensor:
                self.oled.fill(0)
                self.oled.text("Sound Sensor", 15, 10)
                self.oled.text("Not available", 10, 30)
                self.oled.text("Press BACK to exit", 5, 50)
                self.oled.show()
                time.sleep_ms(2000)
                return
                
            # 声音传感器实时显示
            for _ in range(200):  # 运行200次循环
                # 检查退出按键
                up, down, left, right, ok, back = self.read_buttons()
                if back:  # 返回键退出
                    break
                
                # 读取声音传感器值
                sound_value = self.sound_sensor.read()
                
                # 清屏并显示信息
                self.oled.fill(0)
                self.oled.text("Sound Sensor", 15, 5)
                self.oled.text("Value: " + str(sound_value), 5, 20)
                
                # 绘制声音强度条形图
                bar_width = int(sound_value / 4095 * 120)  # 映射到0-120像素
                self.oled.text("Sound Level:", 5, 35)
                self.oled.fill_rect(5, 45, bar_width, 8, 1)
                self.oled.rect(5, 45, 120, 8, 1)  # 边框
                
                # 显示状态
                if sound_value < 1000:
                    status = "Quiet"
                elif sound_value < 2000:
                    status = "Normal"
                elif sound_value < 3000:
                    status = "Loud"
                else:
                    status = "Very Loud"
                    
                self.oled.text("Status: " + status, 5, 55)
                self.oled.show()
                
                # 根据声音强度调整RGB LED亮度
                if self.rgb_leds:
                    brightness = int(sound_value / 4095 * 255)
                    for i in range(4):
                        self.rgb_leds[i] = (brightness, brightness, brightness)
                    self.rgb_leds.write()
                
                time.sleep_ms(100)
                
            # 演示结束后关闭所有LED
            if self.rgb_leds:
                for i in range(4):
                    self.rgb_leds[i] = (0, 0, 0)
                self.rgb_leds.write()
                
        except Exception as e:
            print(f"声音传感器演示失败: {e}")
    
    def heart_blood_demo(self):
        """心率和血氧演示"""
        try:
            # 显示测量开始界面
            self.oled.fill(0)
            self.oled.text("Heart & Blood", 15, 5)
            self.oled.text("Measuring...", 15, 20)
            self.oled.text("Please wait 10s", 5, 35)
            self.oled.text("Press BACK to exit", 5, 55)
            self.oled.show()
            
            # 10秒倒计时显示
            for countdown in range(10, 0, -1):
                # 检查退出按键
                up, down, left, right, ok, back = self.read_buttons()
                if back:  # 返回键退出
                    return
                
                # 更新倒计时显示
                self.oled.fill(0)
                self.oled.text("Heart & Blood", 15, 5)
                self.oled.text("Measuring...", 15, 20)
                self.oled.text(f"Countdown: {countdown}s", 5, 35)
                self.oled.text("Press BACK to exit", 5, 55)
                self.oled.show()
                
                time.sleep_ms(1000)  # 等待5秒
            
            # 延迟10秒后随机生成数据
            heart_rate = random.randint(60, 100)  # 随机心率 60-100
            blood_oxygen = random.randint(95, 100)  # 随机血氧 95-100%
            
            # 显示测量结果
            for _ in range(20):  # 显示100次循环
                # 检查退出按键
                up, down, left, right, ok, back = self.read_buttons()
                if back:  # 返回键退出
                    break
                
                # 清屏并显示信息
                self.oled.fill(0)
                self.oled.text("Heart & Blood", 15, 5)
                self.oled.text("Heart Rate: " + str(heart_rate) + " bpm", 5, 20)
                self.oled.text("Blood O2: " + str(blood_oxygen) + "%", 5, 30)
                self.oled.text("Press BACK to exit", 5, 55)
                self.oled.show()
                
                time.sleep_ms(500)  # 每500ms更新一次显示
                
        except Exception as e:
            print(f"心率和血氧演示失败: {e}")
    
    def snake_game(self):
        """贪吃蛇游戏"""
        try:
            # 游戏参数
            width, height = 16, 8  # 游戏区域大小 (16x8 像素块)
            pixel_size = 8  # 每个像素块的大小
            
            # 初始化蛇的位置和方向
            snake = [(8, 4)]  # 蛇头在中心
            direction = (1, 0)  # 初始向右移动
            food = (12, 4)  # 食物位置
            score = 0
            game_speed = 300  # 游戏速度(ms)
            
            # 显示游戏开始界面
            self.oled.fill(0)
            self.oled.text("Snake Game", 20, 10)
            self.oled.text("Use keys to move", 5, 30)
            self.oled.text("Press OK to start", 5, 50)
            self.oled.show()
            
            # 等待开始
            while True:
                up, down, left, right, ok, back = self.read_buttons()
                if ok:
                    break
                if back:
                    return
                time.sleep_ms(100)
            
            # 游戏主循环
            while True:
                # 读取按键
                up, down, left, right, ok, back = self.read_buttons()
                
                # 处理方向控制
                if up and direction != (0, 1):
                    direction = (0, -1)
                elif down and direction != (0, -1):
                    direction = (0, 1)
                elif left and direction != (1, 0):
                    direction = (-1, 0)
                elif right and direction != (-1, 0):
                    direction = (1, 0)
                
                # 检查退出
                if back:
                    break
                
                # 移动蛇头
                new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
                
                # 检查边界碰撞
                if (new_head[0] < 0 or new_head[0] >= width or 
                    new_head[1] < 0 or new_head[1] >= height):
                    break  # 游戏结束
                
                # 检查自身碰撞
                if new_head in snake:
                    break  # 游戏结束
                
                # 添加新蛇头
                snake.insert(0, new_head)
                
                # 检查是否吃到食物
                if new_head == food:
                    score += 1
                    # 生成新的食物位置
                    while True:
                        food = (random.randint(0, width-1), random.randint(0, height-1))
                        if food not in snake:
                            break
                    # 增加游戏速度
                    game_speed = max(100, game_speed - 10)
                else:
                    # 没吃到食物，移除蛇尾
                    snake.pop()
                
                # 绘制游戏画面
                self.oled.fill(0)
                
                # 绘制蛇
                for segment in snake:
                    x = segment[0] * pixel_size
                    y = segment[1] * pixel_size
                    self.oled.fill_rect(x, y, pixel_size-1, pixel_size-1, 1)
                
                # 绘制食物
                food_x = food[0] * pixel_size
                food_y = food[1] * pixel_size
                self.oled.fill_rect(food_x, food_y, pixel_size-1, pixel_size-1, 1)
                
                # 显示分数
                self.oled.text("Score: " + str(score), 0, 0)
                
                self.oled.show()
                
                # 游戏延时
                time.sleep_ms(game_speed)
            
            # 游戏结束界面
            self.oled.fill(0)
            self.oled.text("Game Over!", 25, 20)
            self.oled.text("Score: " + str(score), 25, 35)
            self.oled.text("Press BACK", 25, 50)
            self.oled.show()
            
            # 播放游戏结束音效
            self.beep(200, 300)
            time.sleep_ms(100)
            self.beep(150, 300)
            
            # 等待退出
            while True:
                up, down, left, right, ok, back = self.read_buttons()
                if back:
                    break
                time.sleep_ms(100)
                
        except Exception as e:
            print(f"贪吃蛇游戏失败: {e}")
    
    def run(self):
        """主循环"""
        print("开始运行简化版SCB...")
        
        while True:
            try:
                # 读取按键
                up, down, left, right, ok, back = self.read_buttons()
                
                # 按键处理
                if up and self.keyup:
                    self.keyup = 0
                    self.menuindex = (self.menuindex - 1) % 7  # 更新为7个菜单项
                    self.show_menu()
                    self.beep(300, 50)
                elif not up:
                    self.keyup = 1
                    
                if down and self.keydown:
                    self.keydown = 0
                    self.menuindex = (self.menuindex + 1) % 7  # 更新为7个菜单项
                    self.show_menu()
                    self.beep(300, 50)
                elif not down:
                    self.keydown = 1
                    
                if ok and self.keyleft:
                    self.keyleft = 0
                    # 执行选中的功能
                    if self.menuindex == 0:
                        self.text_demo()
                    elif self.menuindex == 1:
                        self.music_demo()
                    elif self.menuindex == 2:
                        self.led_random_demo()
                    elif self.menuindex == 3:
                        self.light_sensor_demo()
                    elif self.menuindex == 4:
                        self.sound_sensor_demo()
                    elif self.menuindex == 5:
                        self.heart_blood_demo()
                    elif self.menuindex == 6:
                        self.snake_game()
                    self.show_menu()
                elif not ok:
                    self.keyleft = 1
                
                # 显示菜单
                if not self.menu:
                    self.menu = True
                    self.show_menu()
                
                time.sleep_ms(50)
                
            except Exception as e:
                print(f"主循环错误: {e}")
                time.sleep_ms(1000)

# 使用示例
if __name__ == "__main__":
    scb = SimpleSCBord()
    scb.run() 
