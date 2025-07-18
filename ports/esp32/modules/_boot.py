import gc
import vfs
from flashbdev import bdev

try:
    if bdev:
        vfs.mount(bdev, "/")
except OSError:
    import inisetup
    inisetup.setup()

gc.collect()

import time
import machine
import send_fucking_data

# ==========================================
# OLED显示屏初始化
# ==========================================

oled = None

def init_oled():
    """初始化OLED显示屏"""
    global oled
    
    try:
        import ssd1306
        
        # ESP32常用的I2C配置
        i2c_configs = [
            (4, 15, 100000),   # SDA=4, SCL=15, 100kHz
            (21, 22, 100000),  # SDA=21, SCL=22, 100kHz  
            (5, 18, 100000),   # SDA=5, SCL=18, 100kHz
        ]
        
        for sda, scl, freq in i2c_configs:
            try:
                i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=freq)
                devices = i2c.scan()
                
                # 检查OLED设备 (地址60或0x3C)
                if 60 in devices or 0x3C in devices:
                    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
                    print(f"[BOOT] OLED初始化成功 - SDA:{sda}, SCL:{scl}")
                    return True
                    
            except Exception:
                continue
        
        print("[BOOT] 未找到OLED设备")
        return False
        
    except Exception as e:
        print(f"[BOOT] OLED初始化失败: {e}")
        return False

def safe_oled_display(display_func):
    """安全的OLED显示操作"""
    if oled:
        try:
            display_func()
        except Exception as e:
            print(f"[BOOT] OLED显示错误: {e}")

# ==========================================
# 启动动画函数
# ==========================================

def show_splash_screen():
    """显示启动画面"""
    def display():
        oled.fill(0)
        # 标题
        oled.text("ESP32", 45, 10)
        oled.text("Scratch", 35, 25)
        oled.text("System", 40, 40)
        # 版本信息
        oled.text("v1.0", 50, 55)
        oled.show()
    
    safe_oled_display(display)

def show_loading_animation():
    """显示加载动画"""
    loading_chars = ["|", "/", "-", "\\"]
    
    for i in range(10):  # 动画循环3秒
        def display():
            oled.fill(0)
            oled.text("ESP32 Scratch", 15, 15)
            oled.text("Loading", 40, 30)
            
            # 旋转loading图标
            char = loading_chars[i % 4]
            oled.text(char, 60, 45)
            
            # 进度点
            dots = "." * (i % 4)
            oled.text(dots, 70, 45)
            
            oled.show()
        
        safe_oled_display(display)
        time.sleep_ms(180)

def show_progress_bar(progress, title="Loading"):
    """显示进度条"""
    def display():
        oled.fill(0)
        
        # 标题
        oled.text("ESP32 Scratch", 15, 5)
        oled.text(title, 0, 20)
        
        # 进度条框架
        bar_x, bar_y = 10, 35
        bar_width, bar_height = 108, 8
        
        # 进度条边框
        oled.rect(bar_x, bar_y, bar_width, bar_height, 1)
        
        # 进度条填充
        fill_width = int((progress / 100.0) * (bar_width - 2))
        if fill_width > 0:
            oled.fill_rect(bar_x + 1, bar_y + 1, fill_width, bar_height - 2, 1)
        
        # 百分比显示
        oled.text(f"{progress}%", 55, 50)
        
        oled.show()
    
    safe_oled_display(display)

def show_ready_screen():
    """显示就绪画面"""
    def display():
        oled.fill(0)
        
        # 主标题
        oled.text("ESP32", 45, 8)
        oled.text("Ready!", 40, 25)
        
        # 状态指示
        oled.text("Waiting for", 20, 40)
        oled.text("Connection...", 15, 52)
        
        # 装饰边框
        oled.rect(5, 3, 118, 58, 1)
        
        oled.show()
    
    safe_oled_display(display)

def show_system_info():
    """显示系统信息"""
    def display():
        oled.fill(0)
        
        oled.text("System Info", 25, 5)
        oled.text(f"Memory: {gc.mem_free()//1024}KB", 5, 20)
        oled.text(f"Freq: {machine.freq()//1000000}MHz", 5, 32)
        oled.text(f"Time: {time.ticks_ms()}ms", 5, 44)
        oled.text("Press any key", 20, 56)
        
        oled.show()
    
    safe_oled_display(display)

def breathing_effect():
    """呼吸灯效果"""
    for brightness in range(5):
        def display():
            oled.fill(0)
            
            # 中心圆点
            center_x, center_y = 64, 32
            radius = brightness * 8 + 10
            
            # 简单的同心圆效果
            for r in range(0, radius, 8):
                if r < 128 and r < 64:
                    oled.rect(center_x - r//2, center_y - r//2, r, r, 1)
            
            oled.text("ESP32", 45, center_y - 5)
            oled.show()
        
        safe_oled_display(display)
        time.sleep_ms(200)

# ==========================================
# 主启动流程
# ==========================================

def boot_sequence():
    """完整的启动序列"""
    print("=" * 50)
    print("    ESP32 Scratch系统启动中...")
    print("    ESP32 Scratch System Starting")
    print("=" * 50)
    
    # 初始化OLED
    oled_available = init_oled()
    
    if oled_available:
        # 启动画面
        show_splash_screen()
        time.sleep_ms(1500)
        
        # 加载动画
        show_loading_animation()
        
        # 模拟启动进度
        # startup_steps = [
        #     (20, "Init System"),
        #     (40, "Load Modules"), 
        #     (60, "Check Memory"),
        #     (80, "Setup GPIO"),
        #     (100, "Complete")
        # ]
        
        # for progress, title in startup_steps:
        #     show_progress_bar(progress, title)
        #     print(f"[BOOT] {title} - {progress}%")
        #     time.sleep_ms(300)
        
        # 系统信息显示
        show_system_info()
        time.sleep_ms(1000)

        # 呼吸效果
        breathing_effect()
        
        # 最终就绪画面
        show_ready_screen()
        
        # 闪烁提示
        time.sleep_ms(300)
        if oled:
            oled.invert(1)
            oled.show()
            time.sleep_ms(200)
            oled.invert(0) 
            oled.show()
    
    # 控制台输出启动完成信息
    print(f"[BOOT] ✅ ESP32 Scratch系统启动完成")
    print(f"[BOOT] 💾 可用内存: {gc.mem_free()} bytes ({gc.mem_free()//1024}KB)")
    print(f"[BOOT] ⚡ CPU频率: {machine.freq()//1000000}MHz")
    print(f"[BOOT] ⏰ 启动时间: {time.ticks_ms()}ms")
    print(f"[BOOT] 📟 OLED状态: {'✅ 可用' if oled_available else '❌ 不可用'}")
    print("=" * 50)
    print("    系统就绪，等待连接...")
    print("    System Ready, Waiting for Connection...")
    print("=" * 50)

# 执行启动序列
try:
    import zkspsimplev20
    import SCBoard 
    import music
    import Blood 
    import sonar
    import ds18x20x
    import lm35
    import dhtx
    import framebuf
    import ssd1306 
    import neopixel
    import machine 
    import math
    import random
    import time
    boot_sequence()
except Exception as e:
    print(f"[BOOT] ❌ 启动过程出错: {e}")
    # 即使出错也显示基本信息
    if oled:
        def error_display():
            oled.fill(0)
            oled.text("Boot Error", 30, 20)
            oled.text("Check Console", 15, 35)
            oled.show()
        safe_oled_display(error_display)

# 清理内存
gc.collect()

# 导出OLED实例供其他模块使用
if oled:
    import builtins
    builtins.boot_oled = oled
    print("[BOOT] 📤 OLED实例已导出到全局命名空间")
