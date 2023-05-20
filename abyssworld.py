# -*- coding:utf-8 -*-
"""
cron: 0 0 8,20 * * ?  abyssworld.py
new Env('abyssworld每日签到')
updatetime:2023/5/21
by @StarzL1kerain
"""
import random
import requests
import os
from dotenv import load_dotenv
load_dotenv()


class Dapp:
    def __init__(self):
        self.headers = {}

    def generate_user_agent(self, authorization):
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
            'authorization': authorization,
            'Content-Type': 'application/json',

        }
        return headers

    def day_post(self):
        """POST签到"""
        url = 'https://ca.abyssworld.games/api/user/checkin'
        res = requests.post(url, headers=self.headers)
        return res.json()

    def day_get(self):
        """GET签到"""
        url = 'https://ca.abyssworld.games/api/user/checkin'
        res = requests.get(url, headers=self.headers)
        return res.json()

    def day_info(self):
        """账号信息"""
        url = 'https://ca.abyssworld.games/api/user/info'
        res = requests.get(url, headers=self.headers)
        return res.json()

    def mint(self, authorization):
        self.headers = self.generate_user_agent(authorization)
        day_post = self.day_post()
        day_get = self.day_get()
        info = self.day_info()
        output = "账号:{},code:{}，时间:{}，今天状态:{}，总次数:{}，总分:{}".format(
            info['data']['email'],
            day_post['code'], 
            day_post['data']['date'], 
            day_get['data']['today'],
            day_get['data']['count'], 
            info['data']['points']
        )
        # print(output)
        return output

if __name__ == '__main__':
    # 获取.env中的abyssauths数据，并使用split函数进行分割，得到多个 authorization
    abyssauths = os.getenv("abyssauths")
    authorizations = abyssauths.split('@')

    app = Dapp()
    total_res = []
    for authorization in authorizations:
        # print(authorization)
        res = app.mint(authorization)
        total_res.append(res)
    print(total_res)
