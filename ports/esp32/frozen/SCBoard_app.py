from simple import MQTTClient 
import network
import time 
import json
import _thread
import urequests
import socket
import machine

lock = _thread.allocate_lock()

class SCBoard_app():
    def __init__(self,ssid,passward,address=None):
        self.SSID = ssid.encode("utf-8")       #修改为你的WiFi名称
        self.PASSWORD = passward.encode("utf-8")  #修改为你WiFi密码
        self.SCBordaddress = address.encode("utf-8") #连接的设备地址
        
        self.client = None
        self.wlan = None
        self.wifiState = False
        self.TOPIC_PUB = None
        self.TOPIC = {}
        self.call_data = {}
        self.state = 0
        
        self.name = ""
        self.valse = ""
        self.topic_index = 0
        _thread.start_new_thread(self.testThread, ())

    def app_senddata(self,name,valse):
        if self.state == 1:
            try:
                MQTT_MSG=json.dumps({"type": "sensor_01","name":name,"value": str(valse)});
                MQTT_MSG = MQTT_MSG.encode("utf-8")
                #print(self.TOPIC_PUB)
                #print(MQTT_MSG)
                return self.client.publish_str(self.TOPIC_PUB,MQTT_MSG)
                #time.sleep_ms(1000)
            
                pass
            except OSError as e:
                print("app send data fail---")
                self.reconnect()



    def app_senddata_sendmsg(self,name):
        if self.state == 1:
            try:
                
                return self.client.publish_str(self.TOPIC_PUB,name.encode("utf-8"))
                #time.sleep_ms(1000)
            
                pass
            except OSError as e:
                print("app send sendmsg fail---")
                self.reconnect()

    def testThread(self):
    
        self.connect_mqtt()
            
    #连接WiFi
    def connectWifi(self,ssid,passwd):
        if self.wlan is None:
            self.wlan = network.WLAN(network.STA_IF) 
        self.wlan.active(True)   #激活网络
        self.wlan.disconnect()   #断开WiFi连接
        self.wlan.connect(ssid, passwd)   #连接WiFi
        #for i in range(20):
        i = 0;
        while True:
            if i > 600:
                machine.reset()
            i +=1
            print('{} times try to connect wifi'.format(i))
            
            if self.wlan.isconnected():
                break
            time.sleep_ms(1000)
            
        if not self.wlan.isconnected():
            self.wlan.active(False) #关掉连接
            print("wifi connect error")
            return False
        else:
            print("network config=",self.wlan.ifconfig())
            
        return True

    def reconnect(self):
        print('enter reconnect--')
        i = 0
        while True:
            result = False
            try:
                
                if self.wlan.isconnected() == False:
                    self.connectWifi(self.SSID,self.PASSWORD)
                lock.acquire()
                if self.wlan.isconnected():
                    print('wlan is connected---')
                    
                    self.client.connect()
                    print('reconnect subscribe')
                    self.client.subscribe(self.TOPIC["SCBort"])
                    for i in range(0,len(self.TOPIC )- 1,1):
                        self.client.subscribe(self.TOPIC[i])
                    
                    result= True
                else:
                    result= False
                lock.release()
                return result
            except OSError as e:
                i +=1
                time.sleep(2)
                machine.reset()
            

    #接收到消息后的回调函数
    def sub_cb(self,topic, msg):
        #global state
        #print(topic, msg)
        if self.TOPIC["SCBort"] == b''+ topic:
            self.call_data["SCBort"](msg.decode("utf-8"))
        else:
            self.call_data[topic](topic.decode("utf-8"),msg.decode("utf-8"))
            
        
    def call_app_data(self,f):
        
        self.call_data["SCBort"] = f
            
    def connect_mqtt(self):

        Server = "www.3000iot.com" #mqtt broker ip
        Port   = 1883              #mqtt 连接端口号
        CLIENT_ID="SCBoard20"      #mqtt client ID
        username="NBguest"         #mqtt 用户名
        passwd="NBguest12"         #mqtt 密码
        self.state = 0
        self.wlan = None  #wlan
        self.client = None
        self.TOPIC["SCBort"] = b"SCBort/"+self.SCBordaddress+"/response"             #订阅主题 
        self.TOPIC_PUB = b"SCBort/"+self.SCBordaddress+"/report"           #发送主题
        #要上报的数据点
        #message = {'datastreams':[{'id':'temperature','datapoints':[{'value':27}]}]}
        #message = {"data":"test"}

         
            #连接wifi信息
        if self.wlan is None:
            self.wifiState = self.connectWifi(self.SSID,self.PASSWORD)
            if not self.wifiState:
                print('Failed to connect wifi, please check your wifi connection!')
                return
        elif not self.wlan.isconnected():
            self.wifiState = self.connectWifi(self.SSID,self.PASSWORD)
            if not self.wifiState:
                print('Failed to connect wifi, please check your wifi connection!')
                return
        
            #初始化mqtt客户端
        if self.client is None:
            self.client = MQTTClient(CLIENT_ID + str(self.SCBordaddress) + str(self.wlan.ifconfig()[0]), Server, Port, username, passwd,keepalive=10)

            #初始化mqtt 回调函数
        self.client.set_callback(self.sub_cb)
            #建立mqtt 连接
        if self.wlan.isconnected():
            self.client.connect()
            #订阅mqtt主题
        print(self.TOPIC)
        self.client.subscribe(self.TOPIC["SCBort"])
        for i in range(0,len(self.TOPIC )- 1,1):
            self.client.subscribe(self.TOPIC[i])
        print('mqtt subscriber')
        # self.client.publish(message,'$dp')    #发布
        print('publish end')
        self.state = 1
        
        #try:    
        while True:
            #等待消息到达
            #print("等待消息到达")
            #self.client.wait_msg()
            self.waitmsg()
            #print('wait msg')

                
        #xcept:
        #   #异常处理
        #   print("exception----")
        #   self.client.disconnect()
        #   self.wlan.disconnect()
        #   self.wlan.active(False)
        #   esp_restart()
    def mqtt_subscribe(self,topic,fun):
        self.TOPIC[self.topic_index] = b''+topic.encode("utf-8")+''
        self.call_data[b''+topic.encode("utf-8")+''] = fun
        self.topic_index += 1
        if self.client != "":
            self.client.subscribe(self.TOPIC[self.topic_index])

    def waitmsg(self):
        while True:
            try:
                return self.client.wait_msg()
            except OSError as e:
                print('wait msg error')
            self.reconnect()



    def app_senddata_self(self,topic,data):
    
        if self.state == 1:
            try:
                
                self.client.publish_str(topic.encode("utf-8"),data.encode("utf-8"))
                #time.sleep_ms(1000)
            
                pass
            except OSError as e:
                print("app senddata self exception---")
                self.reconnect()
                

class SCBoard_app_tcp():
    def __init__(self,ssid,passward,address,port):
    
        self.SSID = ssid       #修改为你的WiFi名称
        self.PASSWORD = passward  #修改为你WiFi密码
        self.SCBordaddress = address #连接的设备地址
        self.port=port
        self.wlan=None
        self.server = None
        # 控制初始化
        self.isclient = 1
        self.conncount = 0
        self.call_data = None
        self.conn = None
        self.addr = None
        self.state = 0
        _thread.start_new_thread(self.testThread, ())
        
        
    def connectWifi(self,ssid,passwd):
        self.wlan=network.WLAN(network.STA_IF)         #create a wlan object
        self.wlan.active(True)                         #Activate the network interface
        self.wlan.disconnect()                         #Disconnect the last connected WiFi
        self.wlan.connect(ssid,passwd)                 #connect wifi
        while(self.wlan.ifconfig()[0]=='0.0.0.0'):
            time.sleep(1)
        return True
        
    def start_tcp(self):
        self.connectWifi(self.SSID,self.PASSWORD) 
        ip=self.wlan.ifconfig()[0]                     #获取IP地址
        self.server = socket.socket(socket.SOCK_DGRAM)            #创建socket服务
        self.server.bind((ip,self.port))              #绑定ip地址
        self.server.listen(5)                    #监听信息
        print ('等待连接')
        
        while True:
            self.conn,self.addr = self.server.accept()
            print("app:", self.addr)
            self.conn.sendto('connect 0k',self.addr)
            self.isclient = 1
            self.state = 1
            while self.isclient:
                try:
                    tttttt = time.ticks_ms()
                    data = self.conn.recv(1024)
                    #print(data)
                    if data == b'':
                        if time.ticks_diff(time.ticks_ms(), tttttt) <2:
                            self.conncount = self.conncount + 1
                            if self.conncount > 3:
                                self.conncount = 0
                                #self.conn.sendto('QuitClient',self.addr)
                                self.conn.close()
                                print("errorclose")
                                self.isclient = 0
                                self.state = 0
                    elif data == b'QuitClient\n':
                        print("close")
                        self.conn.close()
                        self.isclient = 0
                        self.state = 0
                    elif data == b'appisconnect\n':
                        self.conn.sendto("scbordconnect",self.addr)
                    else:
                        datasa = data.decode('utf-8')
                        datasa = datasa.splitlines()
                        datalen = len(datasa)
                        for i in range(0,datalen,1):
                            try:
                                self.call_data(datasa[i])
                                # 进行命令的控制
                            except Exception as e:
                                print("aaa")
                                print(e)
                except:
                    pass

                            

    def app_con_data_tcp(self,f):
        self.call_data = f
        
    def testThread(self):
    
        self.start_tcp()
        
    def app_senddata_tcp(self,name,valse):
    
        if self.state == 1:
            try:
                MQTT_MSG=json.dumps({"type": "sensor_01","name":name,"value": str(valse)});
                MQTT_MSG = MQTT_MSG.encode("utf-8")
                #print(self.TOPIC_PUB)
                #print(MQTT_MSG)
                self.conn.sendto(MQTT_MSG,self.addr)
                
                #time.sleep_ms(1000)
            
                pass
            except:
                pass
    def app_senddata_tcp_sendmsg(self,name):
    
        if self.state == 1:
            try:
                self.conn.sendto(name.encode("utf-8"),self.addr)
                #time.sleep_ms(1000)
            
                pass
            except:
                pass
    
        
class Funs():
    def to_bytearray(self,s):
        return bytearray([int('0x'+s[i:i+2]) for i in range(0,len(s),2)])

#get请求类
class weather():
    def __init__(self,wlan,getadd):
        
        self.getadd = getadd
        self.wlan = wlan
        
    def get_data(self):
    
        try:
            for i in range(0,10,1):
            
                if self.wlan.active():
                    time.sleep_ms(10)
                    getdata = urequests.get(self.getadd)
                    return getdata.text
                    # jsondata = json.loads(getdata.text)
                    # print(jsondata['city'])
                    # print(jsondata)
                else:
                    time.sleep(1000)
                    self.connectwifi()
        except:
            print("get请求数据失败")
            return None

        return None
    def connectwifi(self):  
        self.wlan = network.WLAN(network.STA_IF);
        self.wlan.active(True)
        self.wlan.connect(self.wifiname,self.sifipass)
        
        
        
        
