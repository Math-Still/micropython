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

# 初始化OLED显示屏
oled = None
try:
    import ssd1306
    
    # 尝试不同的I2C配置来找OLED (地址60)
    i2c_configs = [
        (4, 15, 100000),   # SDA=4, SCL=15, 100kHz
        (21, 22, 100000),  # SDA=21, SCL=22, 100kHz
        (5, 18, 100000),   # SDA=5, SCL=18, 100kHz
        (13, 14, 100000),  # SDA=13, SCL=14, 100kHz
        (4, 15, 400000),   # 尝试更高频率
    ]
    
    for sda, scl, freq in i2c_configs:
        try:
            i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=freq)
            devices = i2c.scan()
            
            # 检查是否有OLED设备 (通常地址是60或0x3C)
            if 60 in devices or 0x3C in devices:
                oled = ssd1306.SSD1306_I2C(128, 64, i2c)
                
                # 测试OLED是否能正常工作
                oled.fill(0)
                oled.text("SDNUAlion", 30, 25)
                oled.text("ESP32 Starting", 10, 45)
                oled.show()
                
                print(f"[BOOT] OLED显示屏初始化成功 - SDA:{sda}, SCL:{scl}, {freq}Hz")
                
                # 将OLED实例保存到全局命名空间，供其他模块共享使用
                import builtins
                builtins.boot_oled = oled
                
                # 创建共享的OLED线程锁
                try:
                    import _thread
                    builtins.boot_oled_lock = _thread.allocate_lock()
                    print("[BOOT] OLED实例和线程锁已共享到全局命名空间")
                except:
                    builtins.boot_oled_lock = None
                    print("[BOOT] OLED实例已共享，但无法创建线程锁")
                break
        except Exception as e:
                            # 只在详细调试时打印配置失败信息
                continue
    
    if not oled:
        print("[BOOT] 未找到OLED设备，将以无显示模式运行")
        
except Exception as e:
    print(f"[BOOT] OLED模块加载失败: {e}")
    oled = None

def reinit_oled_if_needed(force_reinit=False):
    """重新初始化OLED（如果需要）"""
    global oled
    
    # 如果强制重新初始化，直接清除现有OLED
    if force_reinit:
        print("[BOOT] 强制重新初始化OLED...")
        oled = None
    
    # 如果已经有OLED，先测试是否还能正常工作
    if oled and not force_reinit:
        try:
            # 简单测试OLED是否响应
            oled.fill(0)
            oled.show()
            return True  # OLED工作正常
        except:
            print("[BOOT] OLED连接已失效，尝试重新初始化...")
            oled = None
    
    # 如果没有OLED或OLED失效，尝试重新初始化
    if not oled:
        try:
            import ssd1306
            # 尝试不同的I2C配置来重新找OLED
            i2c_configs = [
                (4, 15, 100000),   # SDA=4, SCL=15, 100kHz
                (21, 22, 100000),  # SDA=21, SCL=22, 100kHz
                (5, 18, 100000),   # SDA=5, SCL=18, 100kHz
                (13, 14, 100000),  # SDA=13, SCL=14, 100kHz
            ]
            
            for sda, scl, freq in i2c_configs:
                try:
                    # 重新创建I2C对象
                    i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=freq)
                    devices = i2c.scan()
                    
                    # 检查是否有OLED设备
                    if 60 in devices or 0x3C in devices:
                        oled = ssd1306.SSD1306_I2C(128, 64, i2c)
                        
                        # 测试OLED是否能正常工作
                        oled.fill(0)
                        oled.show()
                        
                        print(f"[BOOT] OLED重新初始化成功 - SDA:{sda}, SCL:{scl}")
                        
                        # 更新全局共享实例
                        import builtins
                        builtins.boot_oled = oled
                        return True
                        
                except Exception as e:
                    continue
            
            print("[BOOT] OLED重新初始化失败，将跳过显示")
            return False
            
        except Exception as e:
            print(f"[BOOT] OLED重新初始化错误: {e}")
            return False
    
    return True

def safe_oled_operation(operation_func):
    """安全的OLED操作包装器，提供线程锁保护和自动重连"""
    global oled
    
    # 获取共享的线程锁
    oled_lock = None
    try:
        import builtins
        if hasattr(builtins, 'boot_oled_lock'):
            oled_lock = builtins.boot_oled_lock
    except:
        pass
    
    # 使用线程锁保护OLED访问
    if oled_lock:
        oled_lock.acquire()
    
    try:
        # 在使用OLED前重新验证和初始化
        if not reinit_oled_if_needed():
            return  # OLED不可用，直接返回
        
        # 执行OLED操作
        operation_func()
        
    except Exception as e:
        print(f"[BOOT] OLED操作错误: {e}")
        # 尝试重新初始化OLED
        oled = None
        reinit_oled_if_needed()
    finally:
        # 释放线程锁
        if oled_lock:
            oled_lock.release()

def safe_oled_show(lines_dict, clear=True):
    """安全显示多行文本的快捷函数
    lines_dict: {y_position: text} 或 {y_position: (x_position, text)}
    """
    def show_operation():
        if clear:
            oled.fill(0)
        for y_pos, content in lines_dict.items():
            if isinstance(content, tuple):
                x_pos, text = content
                oled.text(text[:16], x_pos, y_pos)
            else:
                # 默认x=0，但某些文本居中显示
                text = content
                if len(text) <= 10:  # 短文本居中
                    x_pos = max(0, (128 - len(text) * 8) // 2)
                else:
                    x_pos = 0
                oled.text(text[:16], x_pos, y_pos)
        oled.show()
    
    safe_oled_operation(show_operation)

def display_on_oled(lines, clear=True):
    """在OLED上显示文本 - 线程安全版本"""
    def oled_operation():
        if clear:
            oled.fill(0)
        
        y_pos = 0
        for line in lines:
            if y_pos < 64:  # 确保不超出屏幕范围
                oled.text(line[:16], 0, y_pos)  # 每行最多16字符
                y_pos += 10
        oled.show()
    
    safe_oled_operation(oled_operation)

def show_progress_bar(progress, title="Loading", subtitle="", max_width=120):
    """显示进度条 - 线程安全版本"""
    def oled_operation():
        oled.fill(0)
        
        # 显示标题
        oled.text("sdnuAlion team", 30, 12)
        
        # 显示进度标题
        oled.text(title[:16], 0, 25)
        if subtitle:
            oled.text(subtitle[:16], 0, 35)
        
        # 绘制进度条框架
        bar_x = 10
        bar_y = 50
        bar_width = 108
        bar_height = 8
        
        # 进度条边框
        oled.rect(bar_x, bar_y, bar_width, bar_height, 1)
        
        # 进度条填充
        fill_width = int((progress / 100.0) * (bar_width - 2))
        if fill_width > 0:
            oled.fill_rect(bar_x + 1, bar_y + 1, fill_width, bar_height - 2, 1)
        
        # 显示百分比
        progress_text = f"{progress}%"
        oled.text(progress_text, 55, 42)
        
        oled.show()
    
    safe_oled_operation(oled_operation)

def update_boot_progress(step, total_steps, title, subtitle=""):
    """更新启动进度"""
    progress = int((step / total_steps) * 100)
    show_progress_bar(progress, title, subtitle)
    print(f"[BOOT] {title} - {progress}% ({step}/{total_steps})")
    time.sleep_ms(200)  # 让用户能看到进度变化

# ESP32 启动横幅
print("=" * 50)
print("    ESP32 Scratch双通道系统启动中...")
print("    ESP32 Scratch Dual-Channel System Starting")
print("=" * 50)

# 等待I2C总线稳定
print("[BOOT] 等待I2C总线稳定...")
time.sleep_ms(300)

# 启动进度追踪
total_boot_steps = 8
current_step = 0

# 步骤1: 系统初始化
current_step += 1
update_boot_progress(current_step, total_boot_steps, "System Init", "Starting...")

# 添加启动延迟，让串口稳定
time.sleep_ms(300)

# 步骤2: 内存检查
current_step += 1
update_boot_progress(current_step, total_boot_steps, "Memory Check", f"{gc.mem_free()//1024}KB")

# 显示系统信息
print(f"[BOOT] ESP32系统启动完成")
print(f"[BOOT] 固件版本: MicroPython + Scratch双通道扩展")
print(f"[BOOT] 可用内存: {gc.mem_free()} bytes")
print(f"[BOOT] 时间戳: {time.ticks_ms()}ms")

# 步骤3: 系统就绪
current_step += 1
update_boot_progress(current_step, total_boot_steps, "System Ready", f"Time:{time.ticks_ms()}")

# 步骤4: 启动双通道服务
current_step += 1
update_boot_progress(current_step, total_boot_steps, "Start Dual", "Loading...")

# 简化的双通道启动流程
dual_service_running = False
try:
    # 显示详细的加载过程
    def show_loading():
        oled.fill(0)
        oled.text("腾信教育", 30, 12)
        oled.text("Loading Dual", 20, 25)
        oled.text("Channel Service", 10, 35)
        oled.text("Please Wait...", 20, 50)
        oled.show()
    
    safe_oled_operation(show_loading)
    
    print("[BOOT] 🔄 正在加载双通道服务模块...")
    import dual_channel_service
    print("[BOOT] ✅ dual_channel_service模块加载成功")
    
    # 步骤5: 初始化服务
    current_step += 1
    update_boot_progress(current_step, total_boot_steps, "Init Service", "UART2...")
    
    # 显示UART2初始化过程
    safe_oled_show({
        12: "sdnuAlion team",
        25: "Init UART2",
        35: "GPIO 16,17", 
        50: "115200 baud"
    })
    
    print("[BOOT] 🔧 正在初始化UART2通道 (GPIO16=RX, GPIO17=TX)...")
    
    # 启动双通道服务
    result = dual_channel_service.start_dual_channel()
    
    if result:
        dual_service_running = True
        print("[BOOT] 🎉 双通道服务启动成功!")
        print("[BOOT] 📡 数据通道: UART2 (TX=17, RX=16)")
        print("[BOOT] ⚡ 数据间隔: 200ms")
        print("[BOOT] 🔄 后台数据流已启动")
        
        # 步骤6: 服务运行确认
        current_step += 1
        update_boot_progress(current_step, total_boot_steps, "Service ON", "Background")
        
        # 显示成功状态
        safe_oled_show({
            12: "sdnuAlion team",
            25: "Dual Channel", 
            35: "ACTIVE",
            50: "Background Run"
        })
        
        # 简化传感器检测 - 不阻塞启动
        print("[BOOT] 🔍 后台检测传感器...")
        
        # 步骤7: 后台运行
        current_step += 1
        update_boot_progress(current_step, total_boot_steps, "Running", "Background")
        
        # 步骤8: 完成
        current_step += 1
        update_boot_progress(current_step, total_boot_steps, "Complete", "Ready")
        
    else:
        print("[BOOT] ⚠️ 双通道服务启动失败")
        print("[BOOT] 🔧 可能原因: UART2端口被占用或硬件问题")
        print("[BOOT] 💡 系统将以单通道模式运行")
        
        # 显示失败状态
        safe_oled_show({
            12: "sdnuAlion team",
            25: "Service FAILED",
            35: "Single Mode", 
            50: "Check UART2"
        })
        
        # 快速完成剩余步骤
        current_step = total_boot_steps
        update_boot_progress(current_step, total_boot_steps, "Single Mode", "OK")
        
except ImportError as e:
    print(f"[BOOT] ❌ 模块导入失败: {e}")
    print("[BOOT] 🔧 可能原因: dual_channel_service.py不在frozen目录")
    
    # 显示导入错误
    safe_oled_show({
        12: "sdnuAlion team",
        25: "Import ERROR",
        35: "Module Missing",
        50: "Check Firmware"
    })
    
    current_step = total_boot_steps
    update_boot_progress(current_step, total_boot_steps, "Import Err", "Missing")
    
except Exception as e:
    print(f"[BOOT] ❌ 启动错误: {e}")
    print(f"[BOOT] 🔧 错误详情: {str(e)}")
    
    # 显示一般错误
    safe_oled_show({
        12: "sdnuAlion team",
        25: "Start ERROR",
        35: str(e)[:16],
        50: "Basic Mode"
    })
    
    current_step = total_boot_steps
    update_boot_progress(current_step, total_boot_steps, "Error", str(e)[:8])



# 显示最终状态
time.sleep_ms(300)

# 显示最终启动状态（在传感器初始化后重新尝试OLED）
def show_final_status():
    oled.fill(0)
    oled.text("SDNUAlion", 30, 12)
    
    if dual_service_running:
        # 双通道成功 - 显示运行状态
        oled.text("Dual Channel", 15, 25)
        oled.text("RUNNING", 35, 35)
        
        # 绘制运行指示器
        oled.rect(20, 45, 88, 6, 1)
        oled.fill_rect(21, 46, 86, 4, 1)
        oled.text("Connect Now!", 20, 55)
    else:
        # 单通道模式 - 显示基础状态
        oled.text("Single Mode", 20, 25)
        oled.text("Ready", 45, 35)
        
        # 绘制基础指示器
        oled.rect(20, 45, 88, 6, 1)
        oled.fill_rect(21, 46, 43, 4, 1)  # 只填充一半
        oled.text("Connect Now!", 20, 55)
    
    oled.show()

# 在传感器初始化完成后，尝试重新恢复OLED显示
print("[BOOT] 传感器初始化完成，检查OLED状态...")
time.sleep_ms(200)  # 给I2C总线一些恢复时间

# 强制重新检测OLED
reinit_oled_if_needed(force_reinit=True)  # 强制重新初始化OLED

safe_oled_operation(show_final_status)

# 简化的状态指示 - 只闪烁一次
time.sleep_ms(500)

def show_blink_effect():
    oled.invert(1)
    oled.show()
    time.sleep_ms(200)
    oled.invert(0)
    oled.show()

safe_oled_operation(show_blink_effect)
