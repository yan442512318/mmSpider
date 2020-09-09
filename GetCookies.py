# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 14:13:14 2020

@author: yly
"""
import json
import time
import re
from selenium import webdriver


class MMCookies:
    
    @classmethod
    def download_cookies(cls, filename):
        driver = webdriver.Chrome()
        driver.get("https://acc.maimai.cn/login")
        driver.delete_all_cookies()
        
        driver.implicitly_wait(45)
        time.sleep(60)
        
        cookies = driver.get_cookies()
        
        with open(filename, 'w') as f:
            for item in cookies:
                f.writelines(json.dumps(item))
                f.writelines('\n')
        
        driver.close()
    
    @classmethod
    def get_cookies(cls, filename):
        rlt = []
        
        with open(filename, 'r') as f:
            line = f.readline().strip('\n')
            rlt.append(json.loads(line))
            while line:
                line = f.readline().strip('\n')
                if len(line.strip()) > 0:
                    rlt.append(json.loads(line))
        
        return rlt

if __name__ == "__main__":
    MMCookies.download_cookies("./cookie_proxy/maimai_cookies.txt")