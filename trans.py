from utils import su
import re, os

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(os.getcwd() + '/templates'))

from premailer import transform

SECTION_SP = '####'
DEVICE_SP = '---'


REG_TITLE = {
    'stat': re.compile(r'【.+】路由状态'),
    'connect': re.compile(r'【.+】.+\s+连接了你的路由器'),
    'disconnect': re.compile(r'【.+】.+\s+断开连接'),
    'abnormal': re.compile(r'【.+】.+\s+流量异常'),
    'cos': re.compile(r'【.+】设备状态变化'),    # Change-of-State
    'restart': re.compile(r'【.+】路由器重新启动'),
    'ip': re.compile(r'【.+】IP 地址变化'),
}

REG_STAT = {
    'load': re.compile(r'平均负载：(.+)'),
    'cpu': re.compile(r'CPU占用：(.+)'),
    'mem': re.compile(r'内存占用：(.+)'),
    'period': re.compile(r'运行时间：(.+)'),
}

REG_WAN = {
    'if_ip': re.compile(r'接口ip:(.+)'),
    'net_ip': re.compile(r'外网ip:(.+)')
}

REG_NEW_CLIENT = {
    'name': re.compile(r'客户端名：\s+(.+)'),
    'ip': re.compile(r'客户端IP：\s+(.+)'),
    'mac': re.compile(r'客户端MAC：\s+(.+)'),
    'if': re.compile(r'网络接口：\s+(.+)')
}

REG_OLD_CLIENT = {
    'name': re.compile(r'客户端名：\s+(.+)'),
    'ip': re.compile(r'客户端IP：\s+(.+)'),
    'mac': re.compile(r'客户端MAC：\s+(.+)'),
    'total': re.compile(r'总计流量：\s+(.+)'),
    'period': re.compile(r'在线时间：\s+(.+)')
}

REG_ABNORMAL_CLIENT = {
    'name': re.compile(r'客户端名：\s+(.+)'),
    'ip': re.compile(r'客户端IP：\s+(.+)'),
    'mac': re.compile(r'客户端MAC：\s+(.+)'),
    'total': re.compile(r'总计流量：\s+(.+)'),
    'onem': re.compile(r'一分钟内流量：\s+([\d\.]+\s+(?:bytes|KB|MB|GB))'),
    'period': re.compile(r'在线时间：\s+(.+)')
}

REG_DEV_TEMP = re.compile(r'设备温度\r\n\r\n(.+)')
REG_IP = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

REG_ONLINE_DEV_STAT = re.compile(r'【(.+)】\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+在线 (.+)')
REG_ONLINE_DEV_CONNECT = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(.+)')

def _shrink_time(full_time:str)->str:
    """将4段时间缩短为2段时间
        1天2时3分4秒 -> 1天2时
        0天2时3分4秒 -> 2时3分
        0天0时3分4秒 -> 3分4秒

    Args:
        full_time (str): %d天%d时%d分%d秒

    Returns:
        str: 两段时间
    """
    d, h, m, s = re.findall(r'(\d+)', full_time)
    d = int(d)
    h = int(h)
    m = int(m)
    s = int(s)
    if d > 0 and h > 0:
        return f'{d}天{h}小时'
    elif d == 0 and h > 0 and m > 0:
        return f'{h}小时{m}分'
    else:
        return f'{m}分{s}秒'
    

def _parse_items(reg_dict:dict, content:str):
    data = {}
    for key in reg_dict:
        result = reg_dict[key].findall(content)
        if not result:
            raise RuntimeError(f'"{reg_dict[key].pattern}"无法匹配"{content}"')
        data[key] = result[0].strip('\r')
    #print(data)
    return data


def trans_stat(content: str):
    sections = content.split(SECTION_SP)
    #print(sections)
    data = {}
    if len(sections) > 0:
        if len(sections) == 4:
            _, sys_stat, wan_info, online_dev_str = sections
        else:
            _, sys_stat, dev_temp, wan_info, online_dev_str = sections
            data['temp'] = REG_DEV_TEMP.findall(dev_temp)[0].strip('\r')
        data.update(_parse_items(REG_STAT, sys_stat))
        data.update(_parse_items(REG_WAN, wan_info))
        
        #print(online_dev_str)
        online_devs = []
        for online_dev_item in REG_ONLINE_DEV_STAT.findall(online_dev_str):
            name, ip, period = online_dev_item
            online_devs.append(dict(
                name = name.strip('\r'),
                ip = ip.strip('\r'),
                period = period.strip('\r')
            ))
        data['online_devs'] = online_devs
        data['period'] = _shrink_time(data['period'])
        data['online'] = _shrink_time(data['online'])
    return data
        

def trans_connect(content):
    sections = content.split(SECTION_SP)
    #print(sections)
    data = {}
    if len(sections) == 2:
        # 精简模式
        _, new_dev_str = sections
        new_devs = new_dev_str.split(DEVICE_SP)
        if len(new_devs) > 0:
            data['new_clients'] = []
            for new_dev_item in new_devs:
                if new_dev_item != '\r\n\r\n':
                    data['new_clients'].append(_parse_items(REG_NEW_CLIENT, new_dev_item))
    
    if len(sections) == 3:
        # 完整模式
        online_dev_str = sections[-1]
        online_devs = []
        for online_dev_item in REG_ONLINE_DEV_CONNECT.findall(online_dev_str):
            ip, name = online_dev_item
            online_devs.append(dict(
                name = name.strip('\r'),
                ip = ip.strip('\r'),
            ))
        data['online_devs'] = online_devs
    return data


def trans_disconnect(content):
    sections = content.split(SECTION_SP)
    #print(sections)
    data = {}
    if len(sections) == 2:
        # 精简模式
        _, old_dev_str = sections
        old_devs = old_dev_str.split(DEVICE_SP)
        if len(old_devs) > 0:
            data['old_clients'] = []
            for old_dev_item in old_devs:
                if old_dev_item != '\r\n\r\n':
                    data['old_clients'].append(_parse_items(REG_OLD_CLIENT, old_dev_item))
    if len(sections) == 3:
        # 完整模式
        online_dev_str = sections[-1]
        online_devs = []
        for online_dev_item in REG_ONLINE_DEV_CONNECT.findall(online_dev_str):
            ip, name = online_dev_item
            online_devs.append(dict(
                name = name.strip('\r'),
                ip = ip.strip('\r'),
            ))
        data['online_devs'] = online_devs
    return data


def trans_abnormal(content):
    #print(content)
    data = _parse_items(REG_ABNORMAL_CLIENT, content)
    return data


def trans_cos(content):
    '''cos - change of state
    '''
    sections = content.split(SECTION_SP)
    #print(sections)
    data = {
        'new_clients': [],
        'old_clients': []
    }
    for item in sections:
        if '新设备连接' in item:
            data['new_clients'].append(_parse_items(REG_NEW_CLIENT, item))
        elif '设备断开连接' in item:
            data['old_clients'].append(_parse_items(REG_OLD_CLIENT, item))
        elif '现有在线设备' in item:
            online_devs = []
            for online_dev_item in REG_ONLINE_DEV_CONNECT.findall(item):
                ip, name = online_dev_item
                online_devs.append(dict(
                    name = name.strip('\r'),
                    ip = ip.strip('\r'),
                ))
            data['online_devs'] = online_devs
    return data


def trans_restart(content):
    sections = content.split(SECTION_SP)
    #print(sections)
    data = {}
    if len(sections) == 2:
        # 精简模式
        _, ip_str = sections
        data['new_ip'] = REG_IP.findall(ip_str)[0].strip('\r')
    if len(sections) == 3:
        # 完整模式
        online_dev_str = sections[-1]
        online_devs = []
        for online_dev_item in REG_ONLINE_DEV_CONNECT.findall(online_dev_str):
            ip, name = online_dev_item
            online_devs.append(dict(
                name = name.strip('\r'),
                ip = ip.strip('\r'),
            ))
        data['online_devs'] = online_devs
    return data


def trans_ip(content):
    sections = content.split(SECTION_SP)
    #print(sections)
    data = {}
    if len(sections) == 2:
        # 精简模式
        _, ip_str = sections
        data['new_ip'] = REG_IP.findall(ip_str)[0].strip('\r')
    if len(sections) == 3:
        # 完整模式
        online_dev_str = sections[-1]
        online_devs = []
        for online_dev_item in REG_ONLINE_DEV_CONNECT.findall(online_dev_str):
            ip, name = online_dev_item
            online_devs.append(dict(
                name = name.strip('\r'),
                ip = ip.strip('\r'),
            ))
        data['online_devs'] = online_devs
    return data


def transition(title, content):
    for key in REG_TITLE:
        if REG_TITLE[key].match(title):
            data = globals()[f'trans_{key}'](content)
            #print(data)
            template = env.get_template(f'{key}.html')
            html = template.render(**data)
            html = transform(html)
            #print(html)
            send(title, html)
            return
    else:
        su.info(content)
        raise RuntimeError(f'未知的svrchan消息：{title}')
    

def send(title:str, body:str, html:bool=True):
    #su.ding(title, body)
    #body = body.replace('\r\n', '<br>')
    if html:
        su.send_email(title, html_body=body)
    else:
        su.send_email(title, body)