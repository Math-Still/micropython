
import machine
import time
import json
import _thread
from machine import UART, Pin

# 不再在dual_channel_service中初始化OLED，避免I2C冲突
# 尝试从_boot.py获取共享的OLED实例
oled = None
oled_lock = None

try:
    # 尝试从全局命名空间获取_boot.py中初始化的OLED
    import builtins
    if hasattr(builtins, 'boot_oled'):
        oled = builtins.boot_oled
        print("[DUAL] 使用共享OLED实例")
        
        # 获取共享的线程锁
        if hasattr(builtins, 'boot_oled_lock'):
            oled_lock = builtins.boot_oled_lock
            print("[DUAL] 使用共享OLED线程锁")
        else:
            print("[DUAL] 未找到共享线程锁，OLED访问可能不安全")
    else:
        print("[DUAL] 未找到共享OLED实例，将跳过显示")
        
except Exception as e:
    print(f"[DUAL] OLED访问失败: {e}")
    oled = None

def reinit_dual_oled_if_needed():
    """重新初始化OLED（dual_channel_service专用）- 优先使用共享实例"""
    global oled
    
    # 优先尝试从_boot.py获取最新的共享OLED实例
    try:
        import builtins
        if hasattr(builtins, 'boot_oled') and builtins.boot_oled:
            # 测试共享OLED是否还能工作
            test_oled = builtins.boot_oled
            try:
                test_oled.fill(0)
                test_oled.show()
                oled = test_oled
                return True  # 成功使用共享OLED
            except:
                # 共享OLED也失效了，等待_boot.py重新初始化
                pass
    except:
        pass
    
    # 如果共享OLED不可用，简单检测是否有OLED硬件
    try:
        from machine import I2C
        from ssd1306 import SSD1306_I2C
        
        # 只尝试最可能的I2C配置
        i2c_configs = [
            (4, 15, 100000),   # SDA=4, SCL=15, 100kHz (最常用)
            (21, 22, 100000),  # SDA=21, SCL=22, 100kHz
        ]
        
        for sda, scl, freq in i2c_configs:
            try:
                i2c = I2C(scl=Pin(scl), sda=Pin(sda), freq=freq)
                devices = i2c.scan()
                
                if 60 in devices or 0x3C in devices:
                    test_oled = SSD1306_I2C(128, 64, i2c)
                    test_oled.fill(0)
                    test_oled.show()
                    
                    oled = test_oled
                    return True
                    
            except:
                continue
        
        # 没有找到OLED硬件，静默跳过
        oled = None
        return False
        
    except:
        oled = None
        return False

def safe_dual_oled_operation(operation_func):
    """安全的OLED操作包装器，专用于dual_channel_service，支持自动重连"""
    global oled, oled_lock
    
    # 使用线程锁保护OLED访问
    if oled_lock:
        oled_lock.acquire()
    
    try:
        # 在使用OLED前重新验证和初始化
        if not reinit_dual_oled_if_needed():
            return  # OLED不可用，直接返回
        
        # 执行OLED操作
        operation_func()
        
    except Exception as e:
        print(f"[DUAL] OLED显示错误: {e}")
        # 尝试重新初始化OLED
        oled = None
        reinit_dual_oled_if_needed()
    finally:
        # 释放线程锁
        if oled_lock:
            oled_lock.release()

def show_dual_progress(step, info=""):
    """显示双通道服务加载进度 - 线程安全版本"""
    def progress_operation():
        oled.fill(0)
        oled.text("SDNUAlion", 30, 0)
        oled.text("Dual Service", 15, 12)
        oled.text(f"Step: {step}", 10, 25)
        oled.text(info[:16], 0, 38)
        oled.text("Loading...", 25, 52)
        oled.show()
    
    safe_dual_oled_operation(progress_operation)

# 不再依赖外部传感器模块，直接内置传感器功能
HAS_SENSORS = True  # 总是可用

# 显示初始化开始
show_dual_progress("Init", "Starting...")

class DualChannelService:
    """双通道通信服务"""
    
    def __init__(self):
        show_dual_progress("Class", "Init Variables")
        print("[DUAL] 开始初始化DualChannelService类...")
        
        # 数据通道配置 (UART2)
        self.data_uart = None
        self.data_running = False
        self.data_thread = None
        
        show_dual_progress("Cache", "Init Cache")
        print("[DUAL] 初始化缓存结构...")
        
        # 内置传感器管理
        self.adc_cache = {}  # ADC对象缓存
        self.pin_cache = {}  # PIN对象缓存
        
        # 传感器重连统计
        self.blood_reconnect_count = 0
        self.msa301_reconnect_count = 0
        self.last_reconnect_log_time = 0
        self.reconnect_log_interval = 30000  # 30秒间隔打印重连统计
        
        show_dual_progress("Sensors", "Loading Modules")
        print("[DUAL] 开始初始化传感器...")
        
        # 初始化常用传感器对象
        self._init_sensors()
        
        show_dual_progress("Config", "Set Interval")
        print("[DUAL] 设置数据间隔...")
            
        # 数据发送间隔
        self.data_interval = 200  # 200ms
        
        show_dual_progress("UART2", "Init Channel")
        print("[DUAL] 初始化数据通道...")
        
        # 初始化数据通道
        self._init_data_channel()
        
        show_dual_progress("Ready", "Init Complete")
        print("[DUAL] DualChannelService类初始化完成")
    
    def _log_reconnect_status(self, sensor_name, sda, scl):
        """记录传感器重连状态（限制日志频率）"""
        current_time = time.ticks_ms()
        
        # 只在间隔时间后打印重连信息
        if time.ticks_diff(current_time, self.last_reconnect_log_time) > self.reconnect_log_interval:
            total_reconnects = self.blood_reconnect_count + self.msa301_reconnect_count
            if total_reconnects > 0:
                print(f"[DUAL] 传感器重连统计: 血氧{self.blood_reconnect_count}次, 三轴{self.msa301_reconnect_count}次")
            self.last_reconnect_log_time = current_time
        
        # 对于第一次重连，立即打印信息
        if (sensor_name == "血氧传感器" and self.blood_reconnect_count == 1) or \
           (sensor_name == "三轴传感器" and self.msa301_reconnect_count == 1):
            print(f"[DUAL] {sensor_name}重连成功 - SDA:{sda}, SCL:{scl}")
    
    def _init_sensors(self):
        """初始化传感器对象"""
        try:
            show_dual_progress("SCBoard", "Importing...")
            print("[DUAL] 尝试导入SCBoard模块...")
            
            # 快速初始化主控板对象
            try:
                import SCBoard
                
                # 快速创建Button对象（通常很快）
                show_dual_progress("SCBoard", "Creating Button")
                print("[DUAL] 创建Button对象...")
                try:
                    self.button = SCBoard.Button()
                    print("[DUAL] ✅ Button对象创建成功")
                except Exception as e:
                    self.button = None
                    print(f"[DUAL] ⚠️ Button对象创建失败: {e}")
                
                # 创建MSA301对象（可能较慢）
                show_dual_progress("SCBoard", "Creating MSA301")
                print("[DUAL] 创建MSA301对象...")
                start_time = time.ticks_ms()
                try:
                    self.msa301 = SCBoard.MSA301()
                    elapsed = time.ticks_diff(time.ticks_ms(), start_time)
                    print(f"[DUAL] ✅ MSA301对象创建成功 (耗时{elapsed}ms)")
                except Exception as e:
                    elapsed = time.ticks_diff(time.ticks_ms(), start_time)
                    self.msa301 = None
                    print(f"[DUAL] ⚠️ MSA301对象创建失败 (耗时{elapsed}ms): {e}")
                
                print("[DUAL] ✅ SCBoard模块已加载")
                show_dual_progress("SCBoard", "OK")
                time.sleep_ms(50)  # 减少延迟
            except ImportError as e:
                self.button = None
                self.msa301 = None
                print(f"[DUAL] ❌ SCBoard模块导入失败: {e}")
                show_dual_progress("SCBoard", "Import Failed")
                time.sleep_ms(100)
            except Exception as e:
                self.button = None
                self.msa301 = None
                print(f"[DUAL] ❌ SCBoard模块不可用: {e}")
                show_dual_progress("SCBoard", "Failed")
                time.sleep_ms(100)
                
            show_dual_progress("Blood", "Importing...")
            print("[DUAL] 尝试导入Blood模块...")
            
            # 尝试初始化血氧传感器
            try:
                import Blood
                show_dual_progress("Blood", "Creating Sensor")
                print("[DUAL] 创建Blood对象...")
                try:
                    self.blood_sensor = Blood.blood()
                    # 验证血氧传感器是否有I2C连接
                    if self.blood_sensor.i2cxueyang:
                        print("[DUAL] ✅ Blood对象创建成功，I2C连接正常")
                    else:
                        print("[DUAL] ⚠️ Blood对象创建成功，但未找到血氧传感器硬件")
                except Exception as e:
                    self.blood_sensor = None
                    print(f"[DUAL] ⚠️ Blood对象创建失败: {e}")
                
                print("[DUAL] ✅ Blood模块已加载")
                show_dual_progress("Blood", "OK")
                time.sleep_ms(50)  # 减少延迟
            except ImportError as e:
                self.blood_sensor = None
                print(f"[DUAL] ❌ Blood模块导入失败: {e}")
                show_dual_progress("Blood", "Import Failed")
                time.sleep_ms(100)
            except Exception as e:
                self.blood_sensor = None
                print(f"[DUAL] ❌ Blood模块不可用: {e}")
                show_dual_progress("Blood", "Failed")
                time.sleep_ms(100)
                
            show_dual_progress("Sensors", "Complete")
            print("[DUAL] ✅ 传感器初始化完成")
            time.sleep_ms(100)
            
        except Exception as e:
            show_dual_progress("Sensors", "Error")
            print(f"[DUAL] ❌ 传感器初始化失败: {e}")
            time.sleep_ms(300)
    
    def _get_adc(self, pin):
        """获取ADC对象，支持缓存"""
        if pin not in self.adc_cache:
            try:
                adc = machine.ADC(machine.Pin(pin))
                adc.atten(machine.ADC.ATTN_11DB)
                self.adc_cache[pin] = adc
            except Exception as e:
                print(f"[DUAL] ADC初始化失败 Pin{pin}: {e}")
                return None
        return self.adc_cache[pin]
    
    def _get_pin(self, pin, mode=machine.Pin.IN):
        """获取PIN对象，支持缓存"""
        cache_key = f"{pin}_{mode}"
        if cache_key not in self.pin_cache:
            try:
                self.pin_cache[cache_key] = machine.Pin(pin, mode)
            except Exception as e:
                print(f"[DUAL] PIN初始化失败 Pin{pin}: {e}")
                return None
        return self.pin_cache[cache_key]
    
    def _read_analog_pin(self, pin):
        """读取模拟引脚值"""
        try:
            adc = self._get_adc(pin)
            if adc:
                return adc.read()
            return 0
        except Exception as e:
            return 0
    
    def _read_digital_pin(self, pin):
        """读取数字引脚值"""
        try:
            pin_obj = self._get_pin(pin, machine.Pin.IN)
            if pin_obj:
                return pin_obj.value()
            return 0
        except Exception as e:
            return 0
    
    def _read_button(self, button_name):
        """读取按钮状态 - 增强错误处理"""
        try:
            if self.button:
                return self.button.value(button_name)
            return 0
        except Exception as e:
            # 按钮读取失败，可能是GPIO或版本检测问题，静默返回0
            return 0
    
    def _read_dht_sensor(self, pin=17):
        """读取DHT温湿度传感器"""
        try:
            import dhtx
            temp = dhtx.get_dht_temperature('dht11', pin)
            hum = dhtx.get_dht_relative_humidity('dht11', pin)
            return temp, hum
        except:
            return 0, 0
    
    def _read_ultrasonic(self, trig_pin=17, echo_pin=16):
        """读取超声波距离传感器"""
        try:
            import sonar
            sensor = sonar.Sonar(trig_pin, echo_pin)
            return sensor.checkdist()
        except:
            return 0
    
    def _reinit_msa301_if_needed(self):
        """重新初始化三轴传感器（如果需要）"""
        if not self.msa301:
            return False
            
        # 测试当前I2C连接是否还能工作
        try:
            if self.msa301.i2cxy:
                # 尝试简单的I2C通信测试
                self.msa301.i2cxy.scan()
                return True  # 连接正常
        except:
            # I2C连接失效，尝试重新初始化
            pass
        
        # 重新初始化三轴传感器的I2C连接
        try:
            # 尝试不同的I2C配置来重新找三轴传感器
            i2c_configs = [
                (4, 15),   # SDA=4, SCL=15
                (21, 22),  # SDA=21, SCL=22
                (5, 18),   # SDA=5, SCL=18  
                (13, 14)   # SDA=13, SCL=14
            ]
            
            for sda, scl in i2c_configs:
                try:
                    i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=400000)
                    devices = i2c.scan()
                    if 98 in devices:  # 三轴传感器地址
                         self.msa301.i2cxy = i2c
                         # 重新初始化传感器
                         self.msa301.i2cxy.writeto(98, b'\x0F\x08')
                         self.msa301.i2cxy.writeto(98, b'\x11\x00')
                         # 增加重连计数
                         self.msa301_reconnect_count += 1
                         self._log_reconnect_status("三轴传感器", sda, scl)
                         return True
                except:
                    continue
            
            # 无法重新连接，禁用三轴传感器
            self.msa301 = None
            return False
            
        except Exception as e:
            self.msa301 = None
            return False
    
    def _read_accelerometer(self):
        """读取三轴加速度 - 支持自动重连"""
        try:
            if not self.msa301:
                return 0, 0, 0
            
            # 在读取前验证并重新初始化I2C连接
            if not self._reinit_msa301_if_needed():
                return 0, 0, 0  # 三轴传感器不可用
            
            # 读取三轴数据
            x = self.msa301.get_x()
            y = self.msa301.get_y()
            z = self.msa301.get_z()
            return x, y, z
            
        except:
            # 读取失败时不打印错误，下次轮询时会自动重试重连
            return 0, 0, 0
    
    def _reinit_blood_sensor_if_needed(self):
        """重新初始化血氧传感器（如果需要）"""
        if not self.blood_sensor:
            return False
            
        # 测试当前I2C连接是否还能工作
        try:
            if self.blood_sensor.i2cxueyang:
                # 尝试简单的I2C通信测试
                self.blood_sensor.i2cxueyang.scan()
                return True  # 连接正常
        except:
            # I2C连接失效，尝试重新初始化
            pass
        
        # 重新初始化血氧传感器的I2C连接
        try:
            # 尝试不同的I2C配置来重新找血氧传感器
            i2c_configs = [
                (4, 15),   # SDA=4, SCL=15
                (21, 22),  # SDA=21, SCL=22
                (5, 18),   # SDA=5, SCL=18  
                (13, 14)   # SDA=13, SCL=14
            ]
            
            for sda, scl in i2c_configs:
                try:
                    i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=400000)
                    devices = i2c.scan()
                    if 87 in devices:  # 血氧传感器地址
                         self.blood_sensor.i2cxueyang = i2c
                         # 重新设置传感器状态
                         self.blood_sensor.isstate = 0
                         # 增加重连计数
                         self.blood_reconnect_count += 1
                         self._log_reconnect_status("血氧传感器", sda, scl)
                         return True
                except:
                    continue
            
            # 无法重新连接，禁用血氧传感器
            self.blood_sensor.i2cxueyang = None
            return False
            
        except Exception as e:
            self.blood_sensor.i2cxueyang = None
            return False
    
    def _read_blood_oxygen(self):
        """读取血氧数据 - 支持自动重连"""
        try:
            if not self.blood_sensor:
                return 0, 0, 0
            
            # 在读取前验证并重新初始化I2C连接
            if not self._reinit_blood_sensor_if_needed():
                return 0, 0, 0  # 血氧传感器不可用
            
            # 读取血氧数据
            heart_rate = self.blood_sensor.get_heart()
            blood_oxygen = self.blood_sensor.get_blood()
            temperature = self.blood_sensor.get_temp()
            return heart_rate, blood_oxygen, temperature
            
        except Exception as e:
            # 读取失败时不打印错误（避免日志刷屏），直接返回0值
            # 下次轮询时会自动重试重连
            return 0, 0, 0
    
    def _quick_sensor_scan(self):
        """快速传感器扫描"""
        data = {}
        
        # 快速读取关键传感器
        try:
            # 光线传感器 (GPIO36)
            data['AR36'] = self._read_analog_pin(36)
            
            # 声音传感器 (GPIO39)  
            data['AR39'] = self._read_analog_pin(39)
            
            # 一个数字引脚
            data['DR2'] = self._read_digital_pin(2)
            
            # 主要按钮
            data['BTN_上'] = self._read_button('上')
            data['BTN_确认'] = self._read_button('确认')
            
            # 血氧数据（如果可用）- 使用重连机制
            if self.blood_sensor:
                try:
                    heart_rate, blood_oxygen, blood_temp = self._read_blood_oxygen()
                    if heart_rate > 0:
                        data['HEART_RATE'] = heart_rate
                    if blood_oxygen > 0:
                        data['BLOOD_OXYGEN'] = blood_oxygen
                    if blood_temp > 0:
                        data['BLOOD_TEMP'] = blood_temp
                except:
                    # 静默处理血氧读取错误
                    pass
            
            # 三轴加速度数据（如果可用）- 使用重连机制  
            if self.msa301:
                try:
                    x, y, z = self._read_accelerometer()
                    if x != 0 or y != 0 or z != 0:  # 只在有有效数据时添加
                        data['ACCEL_X'] = x
                        data['ACCEL_Y'] = y
                        data['ACCEL_Z'] = z
                except:
                    # 静默处理三轴读取错误
                    pass
            
        except Exception as e:
            print(f"[DUAL] 快速扫描失败: {e}")
            
        return data
    
    def _get_sensor_value(self, sensor_type, pin=None):
        """根据传感器类型获取数值"""
        try:
            if sensor_type == 'analog' and pin:
                return self._read_analog_pin(int(pin))
            elif sensor_type == 'digital' and pin:
                return self._read_digital_pin(int(pin))
            elif sensor_type == 'button' and pin:
                return self._read_button(pin)
            elif sensor_type == 'temperature':
                temp, _ = self._read_dht_sensor()
                return temp
            elif sensor_type == 'humidity':
                _, hum = self._read_dht_sensor()
                return hum
            elif sensor_type == 'distance':
                return self._read_ultrasonic()
            elif sensor_type == 'accelerometer':
                return self._read_accelerometer()
            elif sensor_type == 'heart_rate':
                heart_rate, _, _ = self._read_blood_oxygen()
                return heart_rate
            elif sensor_type == 'blood_oxygen':
                _, blood_oxygen, _ = self._read_blood_oxygen()
                return blood_oxygen
            elif sensor_type == 'blood_temperature':
                _, _, temperature = self._read_blood_oxygen()
                return temperature
            else:
                return 0
        except:
            return 0
        
    def _init_data_channel(self):
        """初始化数据通道"""
        try:
            show_dual_progress("UART2", "Creating...")
            print("[DUAL] 创建UART2对象...")
            
            # 使用UART2 (GPIO16=RX, GPIO17=TX)
            self.data_uart = UART(2, baudrate=115200, tx=17, rx=16)
            
            show_dual_progress("UART2", "Testing...")
            print("[DUAL] 测试UART2通道...")
            time.sleep_ms(100)
            
            show_dual_progress("UART2", "Ready")
            print(f"[DUAL] ✅ 数据通道已初始化: UART2 (TX=17, RX=16)")
            time.sleep_ms(100)
            return True
        except Exception as e:
            show_dual_progress("UART2", "Failed")
            print(f"[DUAL] ❌ 数据通道初始化失败: {e}")
            time.sleep_ms(300)
            return False
    
    def start_data_service(self):
        """启动数据服务"""
        show_dual_progress("Service", "Checking...")
        
        if not self.data_uart:
            show_dual_progress("Service", "No UART2")
            print("[DUAL] ❌ 数据通道未初始化")
            time.sleep_ms(300)
            return False
            
        if self.data_running:
            show_dual_progress("Service", "Already Run")
            print("[DUAL] ⚠️ 数据服务已在运行")
            time.sleep_ms(300)
            return True
            
        try:
            show_dual_progress("Service", "Starting...")
            self.data_running = True
            
            show_dual_progress("Thread", "Sender...")
            print("[DUAL] 启动数据发送线程...")
            # 启动数据发送线程
            _thread.start_new_thread(self._data_sender_thread, ())
            time.sleep_ms(100)
            
            show_dual_progress("Thread", "Receiver...")
            print("[DUAL] 启动命令接收线程...")
            # 启动命令接收线程  
            _thread.start_new_thread(self._data_receiver_thread, ())
            time.sleep_ms(100)
            
            show_dual_progress("Service", "Running")
            print("[DUAL] ✅ 数据服务已启动")
            time.sleep_ms(200)
            return True
        except Exception as e:
            show_dual_progress("Service", "Failed")
            print(f"[DUAL] ❌ 启动数据服务失败: {e}")
            self.data_running = False
            time.sleep_ms(500)
            return False
    
    def stop_data_service(self):
        """停止数据服务"""
        self.data_running = False
        print("[DUAL] 数据服务已停止")
    
    def _data_sender_thread(self):
        """数据发送线程"""
        print("[DUAL] 数据发送线程已启动")
        
        while self.data_running:
            try:
                # 使用内置传感器读取
                data = self._quick_sensor_scan()
                if data:
                    # 构建数据包
                    packet = {
                        'type': 'sensor_data',
                        'timestamp': time.ticks_ms(),
                        'data': data
                    }
                    
                    # 发送JSON数据包
                    json_str = json.dumps(packet) + '\n'
                    self.data_uart.write(json_str.encode())
                        
                # 等待间隔
                time.sleep_ms(self.data_interval)
                
            except Exception as e:
                print(f"[DUAL] 数据发送错误: {e}")
                time.sleep_ms(1000)  # 错误后等待更长时间
    
    def _data_receiver_thread(self):
        """数据接收线程 - 处理来自Scratch的命令"""
        print("[DUAL] 数据接收线程已启动")
        
        buffer = ""
        
        while self.data_running:
            try:
                if self.data_uart.any():
                    # 读取数据
                    data = self.data_uart.read().decode('utf-8', 'ignore')
                    buffer += data
                    
                    # 处理完整的行
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line:
                            self._handle_data_command(line)
                
                time.sleep_ms(10)  # 短暂休息
                
            except Exception as e:
                print(f"[DUAL] 数据接收错误: {e}")
                time.sleep_ms(100)
    
    def _handle_data_command(self, command):
        """处理数据通道命令"""
        try:
            cmd = json.loads(command)
            cmd_type = cmd.get('type', '')
            
            if cmd_type == 'get_sensor':
                # 获取指定传感器数据
                sensor_type = cmd.get('sensor_type', '')
                pin = cmd.get('pin', None)
                
                # 使用内置传感器读取方法
                value = self._get_sensor_value(sensor_type, pin)
                response = {
                    'type': 'sensor_response',
                    'sensor_type': sensor_type,
                    'pin': pin,
                    'value': value,
                    'timestamp': time.ticks_ms()
                }
                self.data_uart.write((json.dumps(response) + '\n').encode())
                    
            elif cmd_type == 'set_interval':
                # 设置数据发送间隔
                interval = cmd.get('interval', 200)
                self.data_interval = max(50, min(2000, interval))  # 限制范围50-2000ms
                print(f"[DUAL] 数据间隔已设置为: {self.data_interval}ms")
                
            elif cmd_type == 'ping':
                # 心跳检测
                response = {
                    'type': 'pong',
                    'timestamp': time.ticks_ms()
                }
                self.data_uart.write((json.dumps(response) + '\n').encode())
                
        except Exception as e:
            print(f"[DUAL] 处理命令失败: {command}, 错误: {e}")
    
    def send_debug_info(self):
        """发送调试信息到数据通道"""
        if not self.data_uart or not self.data_running:
            return
            
        try:
            debug_info = {
                'type': 'debug_info',
                'memory_free': machine.mem_free() if hasattr(machine, 'mem_free') else 0,
                'sensors_available': True,  # 总是可用
                'data_interval': self.data_interval,
                'timestamp': time.ticks_ms()
            }
            
            self.data_uart.write((json.dumps(debug_info) + '\n').encode())
        except Exception as e:
            print(f"[DUAL] 发送调试信息失败: {e}")

# 创建全局服务实例
show_dual_progress("Global", "Creating Instance")
print("[DUAL] 创建全局服务实例...")

try:
    dual_service = DualChannelService()
    show_dual_progress("Global", "Instance OK")
    print("[DUAL] ✅ 全局服务实例创建成功")
    time.sleep_ms(200)
except Exception as e:
    show_dual_progress("Global", "Instance Failed")
    print(f"[DUAL] ❌ 全局服务实例创建失败: {e}")
    dual_service = None
    time.sleep_ms(500)

# 自动启动服务
def start_dual_channel():
    """启动双通道服务"""
    show_dual_progress("Start", "Checking Service")
    if dual_service is None:
        show_dual_progress("Start", "No Service")
        print("[DUAL] ❌ 服务实例不存在")
        time.sleep_ms(300)
        return False
    
    show_dual_progress("Start", "Starting...")
    result = dual_service.start_data_service()
    
    if result:
        show_dual_progress("Start", "Success")
        print("[DUAL] 🎉 双通道服务启动成功")
    else:
        show_dual_progress("Start", "Failed")
        print("[DUAL] ❌ 双通道服务启动失败")
    
    time.sleep_ms(200)
    return result

def stop_dual_channel():
    """停止双通道服务"""
    dual_service.stop_data_service()

def get_data_uart():
    """获取数据串口对象"""
    return dual_service.data_uart

def set_data_interval(interval):
    """设置数据发送间隔"""
    dual_service.data_interval = max(50, min(2000, interval))

# 便捷函数
def dual_status():
    """获取双通道状态"""
    sensor_status = {
        'button_available': dual_service.button is not None,
        'msa301_available': dual_service.msa301 is not None,
        'blood_available': dual_service.blood_sensor is not None and dual_service.blood_sensor.i2cxueyang is not None,
        'blood_reconnects': dual_service.blood_reconnect_count,
        'msa301_reconnects': dual_service.msa301_reconnect_count
    }
    
    status = {
        'data_running': dual_service.data_running,
        'data_uart_available': dual_service.data_uart is not None,
        'sensors_available': True,  # 内置传感器总是可用
        'data_interval': dual_service.data_interval,
        'sensor_status': sensor_status
    }
    print(f"[DUAL] 双通道状态: 运行={status['data_running']}, 数据间隔={status['data_interval']}ms")
    print(f"[DUAL] 传感器状态: 按钮={sensor_status['button_available']}, 三轴={sensor_status['msa301_available']}, 血氧={sensor_status['blood_available']}")
    print(f"[DUAL] 重连统计: 血氧{sensor_status['blood_reconnects']}次, 三轴{sensor_status['msa301_reconnects']}次")
    return status

def dual_test():
    """测试双通道功能"""
    print("[DUAL] 开始测试...")
    
    # 发送测试数据
    if dual_service.data_uart:
        test_data = {
            'type': 'test',
            'message': 'Hello from ESP32 data channel!',
            'timestamp': time.ticks_ms()
        }
        dual_service.data_uart.write((json.dumps(test_data) + '\n').encode())
        print("[DUAL] 测试数据已发送")
    else:
        print("[DUAL] 数据通道不可用")

# 添加便捷的传感器测试函数
def quick_sensor_test():
    """快速传感器测试"""
    print("[DUAL] 开始传感器测试...")
    data = dual_service._quick_sensor_scan()
    for key, value in data.items():
        print(f"[DUAL] {key}: {value}")
    return data

def test_analog_pin(pin):
    """测试模拟引脚"""
    value = dual_service._read_analog_pin(pin)
    print(f"[DUAL] 模拟引脚{pin}: {value}")
    return value

def test_digital_pin(pin):
    """测试数字引脚"""
    value = dual_service._read_digital_pin(pin)
    print(f"[DUAL] 数字引脚{pin}: {value}")
    return value

def test_button(button):
    """测试按钮"""
    value = dual_service._read_button(button)
    print(f"[DUAL] 按钮{button}: {value}")
    return value

# 启动信息
show_dual_progress("Module", "Loading Complete")
print("[DUAL] ✅ 双通道服务模块已加载 (内置传感器)")
print("[DUAL] 📋 使用 start_dual_channel() 启动服务")
print("[DUAL] 📊 使用 dual_status() 查看状态")
print("[DUAL] 🧪 使用 dual_test() 测试功能")
print("[DUAL] 🔍 使用 quick_sensor_test() 测试传感器")

# 最终完成显示 - 线程安全版本
def show_module_loaded():
    oled.fill(0)
    oled.text("SDNUAlion", 30, 0)
    oled.text("Module Loaded", 15, 15)
    oled.text("Ready to Start", 10, 30)
    oled.text("Dual Channel", 15, 45)
    oled.text("Service", 40, 55)
    oled.show()
    time.sleep_ms(500)

safe_dual_oled_operation(show_module_loaded)

print("[DUAL] 🎉 模块加载完成，准备启动双通道服务！") 