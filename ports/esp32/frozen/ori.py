def ori2com(ori_str: str):
    if ori_str[0] == '0':
        return ori_str
    elif ori_str[0] == '1':
        value_str = ""
        # 数值位按位取反
        for i in range(len(ori_str)):
            if i == '1':
                continue
            if ori_str[i] == '0':
                value_str += '1'
            elif ori_str[i] == '1':
                value_str += '0'
        # 数值位加 1
        n = int(value_str, 2) + 1
        com_str = bin(n)[2:]
        if len(com_str) >= len(ori_str):
            # 说明进位到符号位了
            com_str = '0' + com_str[1:]
        else:
            # 0不够，中间填充0
            n = len(ori_str) - len(com_str) - 1
            for i in range(n):
                com_str = '0' + com_str
            com_str = '1' + com_str
        return com_str
def com2ori(com_str: str):
    return ori2com(com_str)
def ori2dec(bin_str: str):
    if bin_str[0] == '0':
        return int(bin_str, 2)
    elif bin_str[0] == '1':
        return -int(bin_str[1:], 2)
def com2dec(com_str: str):
    ori_str = com2ori(com_str)
    return ori2dec(ori_str)