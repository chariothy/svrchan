import sys, os
from datetime import datetime as dt, date, timedelta, time as _time
from typing import Pattern
from pybeans import AppTool
import json
import time
import random
import io

from notify import notify_by_ding_talk


class SvrchanUtil(AppTool):
    def __init__(self):
        super(SvrchanUtil, self).__init__('SVRCHAN', os.getcwd())
        self._session = None


    def random(self):
        return random.Random().random()
    
    
    def ding(self, title: str, text: str):
        result = notify_by_ding_talk(self['dingtalk'], title, text)
        self.debug(result)
        
        
    def sleep(self, sec=3):
        time.sleep(sec)
        
    
    def timestamp(self):
        return time.time_ns()
    
    
    def extract_str(self, reg:Pattern, content:str, default=None):
        """从字符串中提取文本信息

        Args:
            reg (Pattern): 编译后的正则对象
            content (str): 要提取内容的字符串
            default (str|None)
        """
        match = reg.search(content)
        if match:
            groups = match.groups()
            if groups:
                return groups[0].strip().strip('\r')
            else:
                return default
        else:
            return default
    


su = SvrchanUtil()