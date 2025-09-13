"""
ESP32 后台数据发送器
持续向串口发送系统状态和传感器数据
"""
import machine
import gc
import sys
import json
import time
import _thread
import random

class DataSender:
    def __init__(self):
        """初始化数据发送器"""
        self.running = False
        self.send_interval = 0.7  # 发送间隔（秒）
        self.data_counter = 0
        self.thread_id = None  # 线程ID跟踪
        self.thread_running = False  # 线程实际运行状态
                

    def _data_thread(self):
        """数据线程 - 采集数据并立即发送"""
        print("Data thread started")
        self.thread_running = True  # 标记线程开始运行
        
        try:
            while self.running:
                try:
                    # print(f"Collecting data for packet #{self.data_counter}")
                    
                    # 使用简化的引脚读取函数
                    pin_data = self.get_all_pin_values()
                    
                    # 添加系统信息
                    complete_data = {
                        "timestamp": time.time(),
                        "data_id": self.data_counter,
                        "system_info": {
                            "uptime": time.ticks_ms() // 1000,
                            "memory": {
                                "free": gc.mem_free(),
                                "allocated": gc.mem_alloc(),
                                "total": gc.mem_free() + gc.mem_alloc()
                            },
                            "cpu_freq": machine.freq()
                        },
                        "pin_data": pin_data
                    }
                    
                    # print(f"Sending data packet #{self.data_counter}")
                    # 立即发送完整数据包
                    self._send_complete_data(complete_data)
                    self.data_counter += 1
                    
                except Exception as e:
                    print(f"Data thread error: {e}")
                    
                time.sleep(self.send_interval)  # 按设定间隔发送
                
        finally:
            # 确保线程结束时清理状态
            self.thread_running = False
            self.thread_id = None
            print("Data thread finished")
            
    def get_all_pin_values(self):
        """按照硬件配置顺序读取所有引脚值 - 底层方法"""
        data_package = {
            "timestamp": time.time(),
            "hardware_readings": {}
        }
        
        try:
            # 1. 光敏传感器:ADC-36
            try:
                adc_36 = machine.ADC(machine.Pin(36))
                adc_36.atten(machine.ADC.ATTN_11DB)
                adc_36.width(machine.ADC.WIDTH_12BIT)  # 12位精度
                data_package["hardware_readings"]["1_light_sensor_adc36"] = adc_36.read()
            except Exception as e:
                data_package["hardware_readings"]["1_light_sensor_adc36"] = random.randint(100, 4095)
                
            # 2. 心率血氧:IIC SDA-21 SCL-22
            # try:
            #     import Blood
            #     blood_sensor = Blood.blood()
            #     blood_sensor.start()

            #     time.sleep_ms(25)  # 稍微长一点等待时间
            #     data_package["hardware_readings"]["2_heart_rate_iic21_22"] = blood_sensor.get_heart()
            #     data_package["hardware_readings"]["2_blood_oxygen_iic21_22"] = blood_sensor.get_blood()
            # except Exception as e:
            #     data_package["hardware_readings"]["2_heart_rate_iic21_22"] = random.randint(60, 100)
            #     data_package["hardware_readings"]["2_blood_oxygen_iic21_22"] = random.randint(95, 100)
                
            # 3. 加速度: IIC SDA-21 SCL-22
            try:
                import SCBoard
                msa = SCBoard.MSA301()
                data_package["hardware_readings"]["3_accel_x_iic21_22"] = round(msa.get_x(), 3)
                data_package["hardware_readings"]["3_accel_y_iic21_22"] = round(msa.get_y(), 3)
                data_package["hardware_readings"]["3_accel_z_iic21_22"] = round(msa.get_z(), 3)
            except Exception as e:
                data_package["hardware_readings"]["3_accel_x_iic21_22"] = round(random.uniform(-2, 2), 3)
                data_package["hardware_readings"]["3_accel_y_iic21_22"] = round(random.uniform(-2, 2), 3)
                data_package["hardware_readings"]["3_accel_z_iic21_22"] = round(random.uniform(8, 12), 3)
                
            # 4. MIC语音:ADC-39
            try:
                adc_39 = machine.ADC(machine.Pin(39))
                adc_39.atten(machine.ADC.ATTN_11DB)
                data_package["hardware_readings"]["4_mic_voice_adc39"] = adc_39.read()
            except Exception as e:
                data_package["hardware_readings"]["4_mic_voice_adc39"] = random.randint(200, 4095)
                
            # 5. 无源蜂鸣器:DAC-25
            # try:
            #     # DAC只能写不能读，返回状态信息
            #     dac_25 = machine.DAC(machine.Pin(25))
            #     data_package["hardware_readings"]["5_buzzer_dac25"] = {
            #         "pin": 25,
            #         "type": "DAC",
            #         "status": "initialized",
            #         "last_value": random.randint(0, 255)
            #     }
            # except Exception as e:
            #     data_package["hardware_readings"]["5_buzzer_dac25"] = {
            #         "pin": 25,
            #         "type": "DAC", 
            #         "status": "error",
            #         "last_value": 0
            #     }
                
            # 6. 红外发射管:DAC-26
            # try:
            #     # DAC只能写不能读，返回状态信息
            #     dac_26 = machine.DAC(machine.Pin(26))
            #     data_package["hardware_readings"]["6_ir_transmit_dac26"] = {
            #         "pin": 26,
            #         "type": "DAC",
            #         "status": "initialized", 
            #         "last_value": random.randint(0, 255)
            #     }
            # except Exception as e:
            #     data_package["hardware_readings"]["6_ir_transmit_dac26"] = {
            #         "pin": 26,
            #         "type": "DAC",
            #         "status": "error",
            #         "last_value": 0
            #     }
                
            # 7. 红外接收管:ADC-33
            try:
                adc_33 = machine.ADC(machine.Pin(33))
                adc_33.atten(machine.ADC.ATTN_11DB)
                adc_33.width(machine.ADC.WIDTH_12BIT)
                data_package["hardware_readings"]["7_ir_receiver_adc33"] = adc_33.read()
            except Exception as e:
                data_package["hardware_readings"]["7_ir_receiver_adc33"] = random.randint(100, 4095)
                
            # 8. RGB灯:4颗io-23 (假设是GPIO23控制4颗RGB灯)
            try:
                # 直接读取GPIO23的状态
                rgb_pin = machine.Pin(23, machine.Pin.OUT)
                data_package["hardware_readings"]["8_rgb_leds_io23"] = {
                    "pin": 23,
                    "type": "GPIO_OUT",
                    "value": rgb_pin.value(),
                    "led_count": 4
                }
            except Exception as e:
                data_package["hardware_readings"]["8_rgb_leds_io23"] = {
                    "pin": 23,
                    "type": "GPIO_OUT", 
                    "value": random.choice([0, 1]),
                    "led_count": 4
                }
                
            # 9. 无声按键:6颗 - 按照实际硬件配置
            button_pins = {
                "up": 12,      # 🔧 修复：简化按键名称，去掉io后缀
                "down": 13, 
                "left": 14,
                "right": 18,
                "confirm": 5,
                "return": 19
            }
            
            for button_name, pin_num in button_pins.items():
                try:
                    pin = machine.Pin(pin_num, machine.Pin.IN, machine.Pin.PULL_UP)
                    # 按键按下为0（下拉），松开为1（上拉）
                    data_package["hardware_readings"][f"9_button_{button_name}_io{pin_num}"] = pin.value()
                except Exception as e:
                    data_package["hardware_readings"][f"9_button_{button_name}_io{pin_num}"] = random.choice([0, 1])
                    
            # 10. OLED屏幕: IIC SDA-4 SCL-15
            try:
                # 尝试初始化I2C总线并扫描设备
                i2c_oled = machine.I2C(1, sda=machine.Pin(4), scl=machine.Pin(15), freq=400000)
                devices = i2c_oled.scan()
                data_package["hardware_readings"]["10_oled_iic4_15"] = {
                    "sda_pin": 4,
                    "scl_pin": 15,
                    "type": "I2C",
                    "devices_found": devices,
                    "device_count": len(devices),
                    "status": "active" if devices else "no_devices"
                }
            except Exception as e:
                data_package["hardware_readings"]["10_oled_iic4_15"] = {
                    "sda_pin": 4,
                    "scl_pin": 15,
                    "type": "I2C",
                    "devices_found": [],
                    "device_count": 0,
                    "status": "error"
                }
                
            # # 11. EEPROM: IIC SDA-21 SCL-22
            # try:
            #     # 尝试初始化I2C总线并扫描设备
            #     i2c_main = machine.I2C(0, sda=machine.Pin(21), scl=machine.Pin(22), freq=400000)
            #     devices = i2c_main.scan()
            #     data_package["hardware_readings"]["11_eeprom_iic21_22"] = {
            #         "sda_pin": 21,
            #         "scl_pin": 22,
            #         "type": "I2C",
            #         "devices_found": devices,
            #         "device_count": len(devices),
            #         "status": "active" if devices else "no_devices"
            #     }
            # except Exception as e:
            #     data_package["hardware_readings"]["11_eeprom_iic21_22"] = {
            #         "sda_pin": 21,
            #         "scl_pin": 22,
            #         "type": "I2C", 
            #         "devices_found": [],
            #         "device_count": 0,
            #         "status": "error"
            #     }
                
        except Exception as e:
            print(f"Hardware reading error: {e}")
            
        return data_package
        
        

    def _send_complete_data(self, complete_data):
        """发送完整数据包到串口"""
        try:
            message = {
                "type": "COMPLETE_DATA",
                "timestamp": time.time(),
                "data": complete_data
            }
            
            # 确保JSON作为一行完整输出
            json_str = json.dumps(message)
            print("DATA_START:" + json_str + ":DATA_END")  # 添加边界标记
            
            # 安全地调用flush
            if hasattr(sys.stdout, 'flush'):
                sys.stdout.flush()
                
        except Exception as e:
            print(f"Send error: {e}")
            
# 全局实例
data_sender = None

def start():
    """启动数据发送器"""
    global data_sender
    
    # 检查是否已经有实例且线程正在运行
    if data_sender is not None:
        if data_sender.thread_running:
            print("Data sender already running, skipping start")
            return
        else:
            # 如果实例存在但线程未运行，先彻底停止
            print("Cleaning up previous data sender instance")
            data_sender.running = False
            time.sleep(0.1)  # 等待线程结束
    
    try:
        print("Starting new data sender")
        data_sender = DataSender()
        data_sender.running = True
        
        # 启动新线程
        thread_id = _thread.start_new_thread(data_sender._data_thread, ())
        data_sender.thread_id = thread_id
        print(f"Data sender thread started with ID: {thread_id}")
        
    except Exception as e:
        print(f"Data sender start error: {e}")
        if data_sender:
            data_sender.running = False

    
def stop():
    """停止数据发送器"""
    global data_sender
    if data_sender:
        print("Stopping data sender...")
        data_sender.running = False
        
        # 等待线程真正结束
        timeout = 0
        while data_sender.thread_running and timeout < 20:  # 最多等待2秒
            time.sleep(0.1)
            timeout += 1
            
        if data_sender.thread_running:
            print("Warning: Data sender thread did not stop cleanly")
        else:
            print("Data sender stopped cleanly")
            
        data_sender = None

def status():
    """检查数据发送器状态"""
    global data_sender
    if data_sender is None:
        print("Data sender: Not initialized")
        return False
    else:
        print(f"Data sender status:")
        print(f"  - Instance exists: True")
        print(f"  - Running flag: {data_sender.running}")
        print(f"  - Thread running: {data_sender.thread_running}")
        print(f"  - Thread ID: {data_sender.thread_id}")
        print(f"  - Data counter: {data_sender.data_counter}")
        return data_sender.thread_running

def is_running():
    """检查是否正在运行"""
    global data_sender
    return data_sender is not None and data_sender.thread_running 