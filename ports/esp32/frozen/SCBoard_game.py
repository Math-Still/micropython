


class SCBoard_Game():
    def __init__(self,oled):
        self.mygamedict = {}
        #初始化标签  
        player = {}#我
        self.mygamedict["player"] = player
        foe = {}#敌人
        self.mygamedict["foe"] = foe
        assistant = {}#助手
        self.mygamedict["assistant"] = assistant
        myweapon = {}#我的武器
        self.mygamedict["myweapon"] = myweapon
        foemyweapon = {}#敌人的武器
        self.mygamedict["foemyweapon"] = foemyweapon
        barrier = {}#障碍物
        self.mygamedict["barrier"] = barrier
        layer1 = {}#layer1
        self.mygamedict["layer1"] = layer1
        layer2 = {}#layer2
        self.mygamedict["layer2"] = layer2
        layer3 = {}#layer3
        self.mygamedict["layer3"] = layer3
        
        
        self.t = Sys_timer_game()
        
        self.oled = oled
        
    #添加一个游戏模型对象
    def add_game_obj(self,name,x,y,demo,layer,scopeminx,scopemaxx,scopeminy,scopemaxy,isshow):
        game_obj = SCBoard_game_obj(name,x,y,demo,layer,scopeminx,scopemaxx,scopeminy,scopemaxy,isshow)
        self.mygamedict[layer][name] = game_obj
        return game_obj
    
    #判断俩物体是否碰撞
    def getOBiscrash(self,obja,objb,scope):
        if obja.is_show == 1 and obja.is_show == 1:
            if obja.get_obj_x() + scope > objb.get_obj_x() > obja.get_obj_x() - scope and obja.get_obj_y() + scope > objb.get_obj_y() > obja.get_obj_y() - scope:
                #print(obja.name + " 和 " + objb.name + " 碰撞1")
                return obja,objb
            else:
                return None,None
    #判断物体和layer是否碰撞
    def getOBiscrash_layer(self,gameobj,layer,scope):
        for i in self.mygamedict[layer]:
            if self.mygamedict[layer][i].is_show == 1 and gameobj.is_show == 1:
                if self.mygamedict[layer][i].get_obj_x() + scope > gameobj.get_obj_x() > self.mygamedict[layer][i].get_obj_x() - scope and self.mygamedict[layer][i].get_obj_y() + scope > gameobj.get_obj_y() > self.mygamedict[layer][i].get_obj_y() - scope:
                    #print(gameobj.name + " 和 " + self.mygamedict[layer][i].name + " 碰撞2")
                    return self.mygamedict[layer][i],gameobj
        return None,None
    #判断layer和layer是否碰撞
    def getOBiscrash_layer_layer(self,layera,layerb,scope):
        
        for i in self.mygamedict[layera]:
            for j in self.mygamedict[layerb]:
                if self.mygamedict[layera][i].is_show == 1 and self.mygamedict[layerb][j].is_show == 1:
                    if self.mygamedict[layera][i].get_obj_x() + scope > self.mygamedict[layerb][j].get_obj_x() > self.mygamedict[layera][i].get_obj_x() - scope:
                        if self.mygamedict[layera][i].get_obj_y() + scope > self.mygamedict[layerb][j].get_obj_y() > self.mygamedict[layera][i].get_obj_y() - scope:
                            #print(self.mygamedict[layerb][j].name + " 和 " + self.mygamedict[layera][i].name + " 碰撞3")
                            return self.mygamedict[layera][i],self.mygamedict[layerb][j]
        return None,None
    
   
        
        
    #添加一个碰撞块,砖块材质，空气材质，蹦蹦球材质：开发中
    def add_box_obj(self,name,x,y,isshow,boxtype):
        pass
    #物体跟随 物体，
    

    #设置系统的时间
    def set_sys_time(self,t):
        self.t.set_time_game(t)
    
    #自动
    def set_auto_obj(self,obj):
        if self.t.get_time_game() > 0:
            if obj.direction == 0 and obj.scopeminy < obj.y:
                obj.y = obj.y - obj.speed * self.t.get_time_game()
            elif obj.direction == 1 and obj.scopemaxy > obj.y:
                obj.y = obj.y + obj.speed * self.t.get_time_game()
            elif obj.direction == 2 and obj.scopeminx < obj.x:
                obj.x = obj.x - obj.speed * self.t.get_time_game()
            elif obj.direction == 3 and obj.scopemaxx > obj.x:
                obj.x = obj.x + obj.speed * self.t.get_time_game()
        
        
    #执行游戏，将模型全部进行显示
    def exe_sys_game(self):
        
        #self.oled.fill(0)
        for i in self.mygamedict:
            for j in self.mygamedict[i]:
                #print(str(self.mygamedict[i][j].is_show) + self.mygamedict[i][j].name)
                if self.mygamedict[i][j].is_show == 1:
                    if self.mygamedict[i][j].stepnum > 0 and self.t.get_time_game() > 0:#判断是否进行自动执行
                        self.mygamedict[i][j].stepnum = self.mygamedict[i][j].stepnum - 1
                        self.set_auto_obj(self.mygamedict[i][j])
                        
                
                    self.oled.framebuf.blit(self.mygamedict[i][j].demo,self.mygamedict[i][j].get_obj_x(),self.mygamedict[i][j].get_obj_y())
                    if self.mygamedict[i][j].is_show_auto == 1:
                        self.mygamedict[i][j].get_obj_isoutscope(0,1)
                            
        self.oled.show()
        

class SCBoard_game_obj():
    def __init__(self,name,x,y,demo,layer,scopeminx,scopemaxx,scopeminy,scopemaxy,isshow):

        self.x = x
        self.y = y
        self.demo = demo
        self.name = name
        self.layer = layer
        
        self.scopeminx = scopeminx
        self.scopemaxx = scopemaxx
        self.scopeminy = scopeminy
        self.scopemaxy = scopemaxy
        
        self.t = Sys_timer_game()
        
        self.is_show = 1
        self.is_show_auto = isshow
        
        self.stepnum = 0
        self.direction = 1
        self.speed = 1


    def auto_speed(self,speed,direction,stepnum):
        self.stepnum = stepnum
        self.direction = direction
        self.speed = speed

    #获取名字
    def get_obj_name(self):
        return self.name
        
    def get_obj_x(self):
        return int(self.x)
        
    def get_obj_y(self):
        return int(self.y)
        
    def get_obj_layer(self):
        
        return self.layer
        
    #设置增量
    def set_obj_seat_xy(self,x,y):
        if self.is_show == 1:
            if  x < 0:
                if  self.x > self.scopeminx:
                    self.x = self.x + (x*self.t.get_time_game())
            elif x > 0:
                if  self.x < self.scopemaxx:
                    self.x = self.x + (x*self.t.get_time_game())
            
            if  y < 0:
                if  self.y > self.scopeminy:
                    self.y = self.y + (y*self.t.get_time_game())
            elif y > 0:
                if  self.y < self.scopemaxy:
                    self.y = self.y + (y*self.t.get_time_game())
                
    #判断是否跑出[["xy","1"],["x", "2"],["y", "3"],["最小边界x", "4"],["最大边界x", "5"],["最小边界y", "6"],["最大边界y", "7"]];
    def get_obj_isoutscope(self,space,border):
        if self.is_show == 0:
            return 0 
        if border == 1:
            if self.scopemaxx - 1 - space >= self.x >= self.scopeminx + 1 + space:
                if self.scopemaxy -1 - space>= self.y >= self.scopeminy + 1 + space:
                    self.is_show = 1
                    return 1
                else:
                    self.is_show = 0
                    return 0
            else:
                self.is_show = 0
                return 0
        elif border == 2:
            if self.scopemaxx - 1 - space >= self.x >= self.scopeminx + 1 + space:
                    
                    return 1
        elif border == 3:
            if self.scopemaxy -1 - space>= self.y >= self.scopeminy + 1 + space:
                    
                    return 1
        elif border == 4:
            if self.x >= self.scopeminx + 1 + space:
                    
                    return 1
        elif border == 5:
            if self.scopemaxx - 1 - space >= self.x:
                    
                    return 1
        elif border == 6:
            if self.y >= self.scopeminy + 1 + space:
                    
                    return 1
        elif border == 7:
            if self.scopemaxy - 1 - space >= self.y:
                    
                    return 1                    
        else:
            return 0
        
    #设置位置
    def set_obj_set_xy(self,x,y):
        
        self.is_show = 1
        self.x = x
        self.y = y
    
    #获取模型对象
    def get_obj_demo(self):
        return self.demo
    
    #设置层
    def set_obj_set_layer(self,layer):
        self.layer = layer
        
    #使得物体隐藏1为显示，0为隐藏
    def set_obj_setdis(self,x):
        
        self.is_show = x
        
    #更改标签
    def set_obj_demo(self,x):
        self.demo = x
    
    #更改模型
    
    
    #更改边框
    
        


#系统时间类
class Sys_timer_game(object):
    time_game = 1
    def set_time_game(self,t):
        Sys_timer_game.time_game = t
    def get_time_game(self):
        return Sys_timer_game.time_game
        
        