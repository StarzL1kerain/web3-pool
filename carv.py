# -*- coding:utf-8 -*-
"""
cron: 0 20 8,20 * * ?    carv.py
new Env('carv每日签到')
updatetime:2023/5/24
by @StarzL1kerain

比如：https://beta.carv.io/account#quests

多账号@隔开，多账户请多开应用，退出会使Authorization失效
"""
import random
import requests
import os
from dotenv import load_dotenv
load_dotenv()
from rpc import Rpc
from eth_account.messages import encode_defunct
import web3

class Dapp:
    def __init__(self,account):
        self.headers = {}
        self.account = account

    def generate_user_agent(self):
        # 随机生成浏览器类型
        browsers = ["Mozilla/5.0", "AppleWebKit/537.36",
                    "Chrome/58.0.3029.110", "Safari/537.36"]
        browser = random.choice(browsers)
        # 随机生成操作系统
        os_list = ["Windows NT 10.0; Win64; x64", "Windows NT 6.1; Win64; x64",
                   "Macintosh; Intel Mac OS X 10_15_4", "Linux x86_64"]
        user_os = random.choice(os_list)
        # 随机生成浏览器版本号
        version = str(random.randint(50, 100))+".0." + \
            str(random.randint(0, 1000))+".0"
        # 构造 User-Agent
        user_agent = f"{browser} ({user_os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
        headers = {
            'User-Agent': user_agent,
            'Content-Type': 'application/json',
        }
        return headers

    def day_get(self):
        """GET获取时间"""
        url = 'https://worldtimeapi.org/api/timezone/etc/UTC'
        res = requests.get(url, headers=self.headers)
        return str(res.json()['unixtime']) + '000'

    def _sign_message0(self,day_get):
        """钱包签名消息"""
        # print('钱包:' + str(self.account.address))
        remark = f"Hello! Please sign this message to confirm your ownership of the address. This action will not cost any gas fee. Here is a unique text: {day_get}"
        msg = remark
        res = self.account.sign_message(encode_defunct(text=msg))
        # print('签名:' + str(res.signature.hex()))
        return res.signature.hex()

    def day_login(self,sign,time):
        """账号登录"""
        url = 'https://api.carv.io/auth/login'
        payload = {
            "address": f"{self.account.address}",
            "signature": f"{sign}",
            "origin_text": f"Hello! Please sign this message to confirm your ownership of the address. This action will not cost any gas fee. Here is a unique text: {time}"
        }
        res = requests.post(url, headers=self.headers,json=payload,)
        return res.json()['data']
    
    def day_checkin(self,Authorization):
        """签到"""
        url = 'https://api.carv.io/marketplace/quest/checkin'
        headers = {
            'Authorization': Authorization,
            'Content-Type': 'application/json',
        }
        res = requests.post(url, headers=headers)
        return res.json()


    def mint(self):
        self.headers = self.generate_user_agent()
        day_get = self.day_get()
        signature=self._sign_message0(day_get)
        data=self.day_login(signature,day_get)
        day_checkin=self.day_checkin(data['token'])

        output = "账号:{},code:{},message:{}".format(
            data['unique_nickname'],
            day_checkin['code'], 
            day_checkin['msg'], 
        )
        return output

if __name__ == '__main__':
    # 获取.env中的key数据，并使用split函数进行分割，得到多个 authorization
    key = os.getenv("key")
    authorizations = key.split('@')
    # authorizations = ['123']


    total_res = []
    for authorization in authorizations:
        # print(authorization)
        privkey = authorization  # 你的私钥
        account = web3.Account.from_key(privkey)
        app = Dapp(account)  # 实例化 Dapp 类
        res = app.mint()
        total_res.append(res+'\n')
    print(total_res)
