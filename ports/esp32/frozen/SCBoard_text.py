from framebuf import FrameBuffer as FB


#公共使用的方法
class Funs():
    def to_bytearray(self,s):
        return bytearray([int('0x'+s[i:i+2]) for i in range(0,len(s),2)])


class Font():
    def __init__(self):
        self.f = Funs()
        self.fontsize14 = 14
        self.fontsize8 = 8
        
        self.imginde14 = ["1","2","3","4","5","6","7","8","9","0","-",">","<","=","级"]
        self.imgdict14 = {"1":None,"2":None,"3":None,"4":None,"5":None,"6":None,"7":None,"8":None,"9":None,"0":None,"-":None,">":None,"<":None,"=":None,"级":None}
        self.imgdata14 = ["0000001C7C1C1C1C1C1C1C7F0000","0000007EE707070E1C3870FF0000","0000007EE707073E0707E77E0000","0000000E1E3E3E6EEEFF0E0E0000","0000007F70707E070707EE7C0000","0000003E7060FEE7E7E7773E0000","000000FF060E0C1C183830700000", \
        "0000007EE7E7767EE7E7E77E0000","0000007CEEE7E7E77F060E7C0000","0000007E66E7E7E7E7E7667E0000","00000000000000007E0000000000","0040201008040204081020400000","0002040810204020100804020000","00000000007E00007E0000000000" ]

        
        ji = "20002FC044409440E48024E04420F62005403880C9401220"
        self.ji = FB(self.f.to_bytearray(ji), 16, 12, 3)

        #print("天气")
        self.fontsize32 = 32
        self.imgindeweather = ["晴","阴","多云","小雨","中雨","大雨","雷阵雨","小雪","中雪","大雪"]
        self.imgdictweather = {"晴":None,"阴":None,"多云":None,"小雨":None,"中雨":None,"大雨":None,"雷阵雨":None,"小雪":None,"中雪":None,"大雪":None}
        self.imgdataweather = ["000000000001000000218100043182000611860003098C000180080000C7E030181FF8C00E3FFD00033FFC00007FFE00007FFE0000FFFF7C3EFFFF781EFFFF00007FFE00007FFE40013FFC70073FFC181C1FF9040047E18000C000C00189886003198C3006118400003186000000820000000000000000000000000000000000"\
                        ,"0000000000000000000000000000000000000000000000000000000000000000020000001247E000489FF800273FFC000F7FFE00DF7FFE001EFFFF005EFFFF0081FFFF801FFFFFF83FFFFFFC7FFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7FFFFFFE3FFFFFFC1FFFFFF80000000000000000000000000000000000000000"\
                        ,"000000000000000000000000000000000000000000000000000000000000000007F000001FE7E0003FDFF8003FBFFC003F7FFE007F7FFE007EFFFF007EFFFF00E1FFFF80DFFFFFF8BFFFFFFC7FFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7FFFFFFE3FFFFFFC1FFFFFF80000000000000000000000000000000000000000"\
                        ,"00000000000000000000000000000000000000000003E000000FF800001FFC00001FFE00003FFE00007FFF0007FFFFF01FFFFFF83FFFFFFC3FFFFFFC3FFFFFFC3FFFFFFC1FFFFFF80FFFFFF000000000000100000001000000000000000100000001000000000000000000000001000000010000000000000000000000000000"\
                        ,"00000000000000000000000000000000000000000003E000000FF800001FFC00001FFE00003FFE00007FFF0007FFFFF01FFFFFF83FFFFFFC3FFFFFFC3FFFFFFC3FFFFFFC1FFFFFF80FFFFFF000000000001084000010840000000000000000000010840000108400001004000000000000000000001084000010840000100400"\
                        ,"00000000000000000000000000000000000000000003E000000FF800001FFC00001FFE00003FFE00007FFF0007FFFFF01FFFFFF83FFFFFFC3FFFFFFC3FFFFFFC3FFFFFFC1FFFFFF80FFFFFF000000000009084400090844000000000012108800121088000000000024211000242110000000000048422000484220000000000"\
                        ,"00000000000000000000000000000000000000000003E000000FF800001FFC00001FFE00003FFE00007FFF0007FFFFF01FFFFFF83FFFFFFC3FFFFFFC3FFFFFFC3FFFFFFC1FFFFFF80FFFFFF00000000000908440009084400001800001210880012308800003C0000240D1000240910000008000048122000481220000000000"\
                        ,"000000000003C000000FF000001FF800001FF800003FFC0007FFFFE00FFFFFF01FFFFFF01FFFFFF01FFFFFF00FFFFFE000000000000000000000000000000000000100000005400000038000000FE000000380000005400000010000000000000000000000000000000000000000000000000000000000000000000000000000"\
                        ,"000000000003C000000FF000001FF800001FF800003FFC0007FFFFE00FFFFFF01FFFFFF01FFFFFF01FFFFFF00FFFFFE000000000000000000000000000000000004004000150150000E00E0003F83F8000E00E000150150000400400000000000000000000000000000000000000000000000000000000000000000000000000"\
                        ,"000000000003C000000FF000001FF800001FF800003FFC0007FFFFE00FFFFFF01FFFFFF01FFFFFF01FFFFFF00FFFFFE000000000000000000000000000000000020100000A854080070382A01FCFE1C0070387F00A8541C0020102A0000000800000000000000000000000000000000000000000000000000000000000000000"\
                        ]
                        
    
    def get_img(self,name):
        try:
            if self.imgdictweather[name] == None:
                self.imgdictweather[name] = FB(self.f.to_bytearray(self.imgdataweather[self.imgindeweather.index(name)]), self.fontsize32, self.fontsize32, 3)
            return self.imgdictweather[name]
            
        except:
        
            other = "07e018f021f871ecf9ecfcfcbe7e4c81717e4082307c0f80"
            other = FB(self.f.to_bytearray(other), 16, 12, 3)
            return other
 
    
    def get_14_text(self,name):
    
        if(name=="级"):
            return self.ji
            

        if self.imgdict14[name] == None:
            self.imgdict14[name] = FB(self.f.to_bytearray(self.imgdata14[self.imginde14.index(name)]), self.fontsize8, self.fontsize14, 3)
        return self.imgdict14[name]
        

            
        
            
            
            
        return self.minus
        
    def getzksp(self,x):
        if(x== "zhong"):
            zhong = "000000000C003FFD80377F80377F4037FFE03FB82037FFF037F70037638037FFF03FF770377700377FE07760E07706C067FFC06780C0FF07C0C60380000000"
            zhong = FB(self.f.to_bytearray(zhong), 24, 21, 3)
            return zhong
        elif(x=="ke"):
            ke = "000000071800071C000E0E600FFFF01C00001C00C01CFFE03C40007C00C07CFFE0DC80001C00001CFFE01CE0C01CE0C01CE0C01CFFC01CE0C01CC0C0000000"
            ke = FB(self.f.to_bytearray(ke), 24, 21, 3)
            return ke
        elif(x=="si"):
            si = "0000000181C007C1C07F01C00639C0061DC006CDC0FFE1C04601C00E19C00F9DC01FCDF01EC1F8367FC066E1C0C601C00601C00601C00601C00601C0000000"
            si = FB(self.f.to_bytearray(si), 24, 21, 3)
            return si
        elif(x=="ping"):
            ping = "0000000E0E000E0E000E0E000F8E20FFFFF00E0E000E0E000E0E000FFFE01F30E0FE31C07E19C00E1B800E1F000E0F000E1F002E3FC07EF1F81FC070000000"
            ping = FB(self.f.to_bytearray(ping), 24, 21, 3)
            return ping
        elif(x=="fangge32"):
            fangge32 = "FFFFFFFF8000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001800000018000000180000001FFFFFFFF"
            fangge32 = FB(self.f.to_bytearray(fangge32), 32, 32, 3)
            return fangge32
        elif(x=="fangge16"):
            fangge16 = "FFFF80018001800180018001800180018001800180018001800180018001FFFF"
            fangge16 = FB(self.f.to_bytearray(fangge16), 16, 16, 3)
            return fangge16
        elif(x=="qiuti16"):
            qiuti16 = "0000000007E00FF01F383F9C3FCC3FFC3FFC3FFC3FFC1FF80FF007E000000000"
            qiuti16 = FB(self.f.to_bytearray(qiuti16), 16, 16, 3)
            return qiuti16
        elif(x=="qiuti16xiaolian"):
            qiuti16xiaolian = "0000000007E00FF01FF83BDC318C3BDC3FFC3FFC3BDC1C380FF007E000000000"
            qiuti16xiaolian = FB(self.f.to_bytearray(qiuti16xiaolian), 16, 16, 3)
            return qiuti16xiaolian
        elif(x=="qiuti16kulian"):
            qiuti16kulian = "0000000007E00FF01FF83BDC318C3BDC3FFC3FFC3C3C1BD80FF007E000000000"
            qiuti16kulian = FB(self.f.to_bytearray(qiuti16kulian), 16, 16, 3)
            return qiuti16kulian
        elif(x=="lingdian16"):
            lingdian16 = "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
            lingdian16 = FB(self.f.to_bytearray(lingdian16), 24, 24, 3)
            return lingdian16
            
            
        return zhong
        
        
    def get_24_text(self,x):
        fontsize24 = 24
        fontsize16 = 16
        self.imgdata = [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]
        x = str(x)
        if(x=="1"):
            if self.imgdata[0] == None:
                test1 = "000000000000000007000F001F003F007F007F000F000F000F000F000F000F000F000F000F000F000700000000000000"
                test1 = FB(self.f.to_bytearray(test1), fontsize16, fontsize24, 3)
                self.imgdata[0] = test1
            return self.imgdata[0]
        elif(x=="2"):
            if self.imgdata[1] == None:
                test2 = "00000000000000001F803FC07BE0F1E0E0E000E001E001C003C007800F000E001E003C007FE0FFE07FE0000000000000"
                test2 = FB(self.f.to_bytearray(test2), fontsize16, fontsize24, 3)
                self.imgdata[1] = test2
            return self.imgdata[1]
        elif(x=="3"):
            if self.imgdata[2] == None:
                test3 = "00000000000000001F803FC079E070E070E000E001C00FC00FC003E000E000E0F0E0F1E07FE03FC01F00000000000000"
                test3 = FB(self.f.to_bytearray(test3), fontsize16, fontsize24, 3)
                self.imgdata[2] = test3
            return self.imgdata[2]
        elif(x=="4"):
            if self.imgdata[3] == None:
                test4 = "000000000000000001C003C003C007C00FC00FC01DC03DC079C071C0F1C0FFF0FFF001C001C001C001C0000000000000"
                test4 = FB(self.f.to_bytearray(test4), fontsize16, fontsize24, 3)
                self.imgdata[3] = test4
            return self.imgdata[3]
        elif(x=="5"):
            if self.imgdata[4] == None:
                test5 = "00000000000000003FE03FE07FC0780070007E007F80FFC0F1E000E000E000E0E0E0E1E0FBC07FC03F00000000000000"
                test5 = FB(self.f.to_bytearray(test5), fontsize16, fontsize24, 3)
                self.imgdata[4] = test5
            return self.imgdata[4]
        elif(x=="6"):
            if self.imgdata[5] == None:
                test6 = "0000000000000000038007800F000E001E003C003FC07FE079F0F0F0F070F070F0F070F079E03FC01F80000000000000"
                test6 = FB(self.f.to_bytearray(test6), fontsize16, fontsize24, 3)
                self.imgdata[5] = test6
            return self.imgdata[5]
        elif(x=="7"):
            if self.imgdata[6] == None:
                test7 = "0000000000000000FFF0FFF07FF000E001C001C003800380070007000F000E000E001E001C001C001C00000000000000"
                test7 = FB(self.f.to_bytearray(test7), fontsize16, fontsize24, 3)
                self.imgdata[6] = test7
            return self.imgdata[6]
        elif(x=="8"):
            if self.imgdata[7] == None:
                test8 = "00000000000000001F803FC079E0F0E0F0E071E07BC03FC07FC07BE0F0E0E0F0E0F0F0E0FBE07FC03F80000000000000"
                test8 = FB(self.f.to_bytearray(test8), fontsize16, fontsize24, 3)
                self.imgdata[7] = test8
            return self.imgdata[7]
        elif(x=="9"):
            if self.imgdata[8] == None:
                test9 = "00000000000000001F807FC07BE0F1E0E0E0E0E0E0E0F1E0FBC07FC01F80078007000F000E001E003C00000000000000"
                test9 = FB(self.f.to_bytearray(test9), fontsize16, fontsize24, 3)
                self.imgdata[8] = test9
            return self.imgdata[8]
        elif(x=="0"):
            if self.imgdata[9] == None:
                test0 = "00000000000000001F803FC07FC071E0F0E0F0E0F0E0F0F0E0F0E0E0F0E0F0E070E079E07FC03FC01F00000000000000"
                test0 = FB(self.f.to_bytearray(test0), fontsize16, fontsize24, 3)
                self.imgdata[9] = test0
            return self.imgdata[9]
        elif(x=="-"):
            if self.imgdata[10] == None:
                testj = "000000000000000000000000000000000000000000007FFE7FFE7FFE0000000000000000000000000000000000000000"
                testj = FB(self.f.to_bytearray(testj), fontsize16, fontsize24, 3)
                self.imgdata[10] = testj
            return self.imgdata[10]
        elif(x=="℃"):
            if self.imgdata[11] == None:
                tests = "000000000000000000000000000000000000000000000000200053D024300810080008000810042003C0000000000000"
                tests = FB(self.f.to_bytearray(tests), fontsize16, fontsize24, 3)
                self.imgdata[11] = tests
            return self.imgdata[11]
        elif(x=="."):
            if self.imgdata[12] == None:
                tests = "000000000000000000000000000000000000387C7C7C3800"
                tests = FB(self.f.to_bytearray(tests), 8, fontsize24, 3)
                self.imgdata[12] = tests
            return self.imgdata[12]
        elif(x=="t1"):
            if self.imgdata[13] == None:
                t1 = "001800002400004200008100000000000000000000000000103C08207E0440FF0281FF8181FF8141FF8220FF04107E08003C00000000000000000000008100004200002400001800"
                t1 = FB(self.f.to_bytearray(t1), fontsize24, fontsize24, 3)
                self.imgdata[13] = t1
            return self.imgdata[13]
        elif(x=="t2"):
            if self.imgdata[14] == None:
                t2 = "000608000A1000122000224000428000820201020C0202307C02C07802007802007802FF7802007802007802C07C023002020C010282008240004220002210001208000A04000600"
                t2 = FB(self.f.to_bytearray(t2), fontsize24, fontsize24, 3)
                self.imgdata[14] = t2
            return self.imgdata[14]
        elif(x=="t3"):
            if self.imgdata[15] == None:
                t3 = "0800001C00002A0000080000080000081C00080C000814000820000840000880000900000A00040C0002FFFFFF180002280004480000880000080000080000080000080000080000"
                t3 = FB(self.f.to_bytearray(t3), fontsize24, fontsize24, 3)
                self.imgdata[15] = t3
            return self.imgdata[15]
        elif(x=="t4"):
            if self.imgdata[16] == None:
                t4 = "00000000000000000000000000000000000000001038E0287DF028FFF828FFF844FFFC447FF2833FE2801FC1000F8000070000020000000000000000000000000000000000000000"
                t4 = FB(self.f.to_bytearray(t4), fontsize24, fontsize24, 3)
                self.imgdata[16] = t4
            return self.imgdata[16]
        elif(x=="t5"):
            if self.imgdata[17] == None:
                t5 = "0000E00003F80007FC000FFE000FFE000FFF001FFF001FFF000FFE0027FE0073FC00F9F800FCC001FE0003FC0007F80007E0000FC0001F80003E00003C0000380000400000800000"
                t5 = FB(self.f.to_bytearray(t5), fontsize24, fontsize24, 3)
                self.imgdata[17] = t5
            return self.imgdata[17]
        elif (x=="t6"):
            if self.imgdata[18] == None:
                t6 = "0018700006F90001FC003DFC0001FD0001FC000CF80030710001040002540004520008920000900000000000000000000000000000000000000000000000001FFFF81FFFF8FFFFFF"
                t6 = FB(self.f.to_bytearray(t6), fontsize24, fontsize24, 3)
                self.imgdata[18] = t6
            return self.imgdata[18]
        elif(x=="t7"):
            if self.imgdata[19] == None:
                t7 = "003C0000C20001350002008002788004488004508002610001510001060000F9C10F062010D8102621C82911444811C449114426A9C81028100C46200381C0000000000000000000"
                t7 = FB(self.f.to_bytearray(t7), fontsize24, fontsize24, 3)
                self.imgdata[19] = t7
            return self.imgdata[19]
        elif(x=="t8"):
            if self.imgdata[20] == None:
                t8 = "00000003040000C800003040002C400043400080C0010C7002124C041240080C401000402000404000400180400240400240400FFFFE000040000040000040000040000000000000"
                t8 = FB(self.f.to_bytearray(t8), fontsize24, fontsize24, 3)
                self.imgdata[20] = t8
            return self.imgdata[20]
        elif(x=="d"):
            if self.imgdata[21] == None:
                testd = "000000000000000000E000E000E000E000E00EE03FE07FE071E0F1E0F0E0F0E0F0E0F1E07BE03FE01FE0000000000000"
                testd = FB(self.f.to_bytearray(testd), fontsize16, fontsize24, 3)
                self.imgdata[21] = testd
            return self.imgdata[21]
        elif(x=="B"):
            if self.imgdata[22] == None:
                testB = "0000000000000000FF00FFC0FFE0F1E0F0E0F0E0F1E0FFC0FFC0F3E0F0F0F0F0F0F0F0F0FFE0FFC0FF00000000000000"
                testB = FB(self.f.to_bytearray(testB), fontsize16, fontsize24, 3)
                self.imgdata[22] = testB
            return self.imgdata[22]
            
        other = "07e018f021f871ecf9ecfcfcbe7e4c81717e4082307c0f80"
        other = FB(self.f.to_bytearray(other), 16, 12, 3)
        return other
        



class Game_demo():

    def __init__(self):
        self.f = Funs()
        self.fontsize14 = 14
        self.fontsize12 = 12
        self.fontsize8 = 8
        self.fontsize16 = 16
        self.fontsize32 = 32
        
        self.imginde = ["敌机1","敌机2","炮弹1","炮弹2","炮弹3","炮弹4","炮弹5","炮弹6"]
        self.imgdict = {"敌机1":None,"敌机2":None,"炮弹1":None,"炮弹2":None,"炮弹3":None,"炮弹4":None,"炮弹5":None,"炮弹6":None}
        self.imgdata = ["3C18187EFFFF7E18","183C185AFFFF5A00","0010384400000000","0010383838383838","0010103810101038","1818181800000000","2418000000000000","3810000000000000"]
        
    def get_game_ico(self,name):
        if(name=="飞机1"):
            yin = "001038387CFEBA38387C100000000000"
            yin = FB(self.f.to_bytearray(yin), self.fontsize8, self.fontsize16, 3)
            return yin
        elif (name=="飞机2"):
            yin = "001038EEEE7C38387C00000000000000"
            yin = FB(self.f.to_bytearray(yin), self.fontsize8, self.fontsize16, 3)
            return yin
            
        elif (name=="跑车"):
            yin = "3C7E7EFFFF7E7E7EFFFF7E3C"
            yin = FB(self.f.to_bytearray(yin), self.fontsize8, self.fontsize12, 3)
            return yin
        elif (name=="货车"):
            yin = "7E7E7E187E7E7E7E7E7E7E7E"
            yin = FB(self.f.to_bytearray(yin), self.fontsize8, self.fontsize12, 3)
            return yin
        elif (name=="卡丁车"):
            yin = "00003C7EFF7E7E7EFF7E3C00"
            yin = FB(self.f.to_bytearray(yin), self.fontsize8, self.fontsize12, 3)
            return yin
        elif (name=="赛车"):
            yin = "18247E7E3C3C3C7E7E247E00"
            yin = FB(self.f.to_bytearray(yin), self.fontsize8, self.fontsize12, 3)
            return yin
            
    
        try:
            if self.imgdict[name] == None:
                self.imgdict[name] = FB(self.f.to_bytearray(self.imgdata[self.imginde.index(name)]), self.fontsize8, self.fontsize8, 3)
            return self.imgdict[name]
            
        except:
        
            other = "07e018f021f871ecf9ecfcfcbe7e4c81717e4082307c0f80"
            other = FB(self.f.to_bytearray(other), 16, 12, 3)
            return other
            

        
            
            
            
            