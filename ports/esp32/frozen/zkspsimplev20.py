import machine
import time
import ssd1306

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
            
            # 初始化LED (使用PWM控制)
            try:
                self.led_pin = machine.Pin(23, machine.Pin.OUT)
                self.led_pin.value(0)
            except:
                self.led_pin = None
                
            # 初始化蜂鸣器
            self.buzzer = machine.Pin(25, machine.Pin.OUT)
            
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
                "2. Sound Demo", 
                "3. LED Demo",
                "4. Game Demo",
                "5. Exit"
            ]
            
            for i, item in enumerate(menu_items):
                if i == self.menuindex:
                    self.oled.text(">" + item, 5, i * 12)
                else:
                    self.oled.text(" " + item, 5, i * 12)
            
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
    
    def sound_demo(self):
        """声音演示"""
        try:
            self.oled.fill(0)
            self.oled.text("Sound Demo", 20, 10)
            self.oled.text("Playing...", 20, 30)
            self.oled.text("Press BACK to exit", 5, 50)
            self.oled.show()
            
            # 播放音阶
            frequencies = [200, 300, 400, 500, 600, 700, 800]
            for freq in frequencies:
                # 检查退出按键
                up, down, left, right, ok, back = self.read_buttons()
                if back:  # 返回键退出
                    break
                    
                self.beep(freq, 200)
                time.sleep_ms(100)
                
        except Exception as e:
            print(f"声音演示失败: {e}")
    
    def led_demo(self):
        """LED演示"""
        try:
            self.oled.fill(0)
            self.oled.text("LED Demo", 20, 10)
            self.oled.text("Blinking...", 15, 30)
            self.oled.text("Press BACK to exit", 5, 50)
            self.oled.show()
            
            if self.led_pin:
                # LED闪烁
                for _ in range(20):  # 增加闪烁次数
                    # 检查退出按键
                    up, down, left, right, ok, back = self.read_buttons()
                    if back:  # 返回键退出
                        break
                        
                    self.led_pin.value(1)  # 点亮LED
                    time.sleep_ms(200)
                    self.led_pin.value(0)  # 熄灭LED
                    time.sleep_ms(200)
                    
        except Exception as e:
            print(f"LED演示失败: {e}")
    
    def game_demo(self):
        """游戏演示"""
        try:
            self.oled.fill(0)
            self.oled.text("Game Demo", 20, 10)
            self.oled.text("Moving dot", 15, 30)
            self.oled.text("Press BACK to exit", 5, 50)
            self.oled.show()
            
            time.sleep_ms(1000)
            
            # 简单的移动点游戏
            x, y = 64, 32
            for _ in range(100):  # 增加游戏时长
                # 检查退出按键
                up, down, left, right, ok, back = self.read_buttons()
                if back:  # 返回键退出
                    break
                    
                self.oled.fill(0)
                self.oled.text("Game Demo", 20, 10)
                
                # 绘制一个简单的点
                self.oled.pixel(x, y, 1)
                # 绘制一个小方块代替点，更容易看到
                self.oled.fill_rect(x-1, y-1, 3, 3, 1)
                
                self.oled.show()
                
                # 移动点
                x = (x + 2) % 128
                y = (y + 1) % 64
                time.sleep_ms(100)
                
        except Exception as e:
            print(f"游戏演示失败: {e}")
    
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
                    self.menuindex = (self.menuindex - 1) % 5
                    self.show_menu()
                    self.beep(300, 50)
                elif not up:
                    self.keyup = 1
                    
                if down and self.keydown:
                    self.keydown = 0
                    self.menuindex = (self.menuindex + 1) % 5
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
                        self.sound_demo()
                    elif self.menuindex == 2:
                        self.led_demo()
                    elif self.menuindex == 3:
                        self.game_demo()
                    elif self.menuindex == 4:
                        print("退出程序")
                        break
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