from rpc import Rpc
import sys
import time
import math
import web3
import requests
import random
import os
import re
import json
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.getcwd())  # 将根目录添加到 Python 的搜索路径中
from dotenv import dotenv_values, set_key
# https://labs.zetachain.com/leaderboard

class Dapp:
    def __init__(self, account, cookie_list, cookie, index):
        self.cookie_list = cookie_list
        self.cookie = cookie
        self.index = index
        self.account = account
        self.gas_limit = 600000
        self.total = len(self.cookie_list)  # 总任务数
        self.headers_cookie = {}
        self.headers_auth = {}

    def generate_user_agent(self, authorization=None, cookie=None):
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
        if authorization:
            headers['authorization'] = 'Bearer ' + authorization
        if cookie:
            headers['cookie'] = cookie
        return headers

    def run(self):
        print(f'开始，总任务数：{self.total}')
        # 带cookie的请求头
        self.headers_cookie = self.generate_user_agent(cookie=self.cookie)
        # 登录
        print('登录')
        zeta_set_cookies, zeta_hasuraJwt, userId = self.login(self.cookie)
        # 带authorization的请求头
        self.headers_auth = self.generate_user_agent(authorization=zeta_hasuraJwt)
        print('获取zeta')
        get_zeta = self.get_zeta()
        print(get_zeta)

        # progress_str = f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}，当前第{0}个账号/总{self.total}个账号，进度{progress:.2f}%\n"
        # print(f"{progress_str}，账号 {userId} 的交易次数：{transactions_count}，积分：{total_earned_points}，排名：{userRank}，跨链信息：{cross_chain_info['result']}，\n跨链结果：{result}")
        # print(f"账号 {userId} 的交易次数：{transactions_count}，积分：{total_earned_points}，排名：{userRank}，跨链信息：{cross_chain_info['result']}，\n跨链结果：{result}")
        # 等待5分钟
        # time.sleep(300)

    # 登录获取


    def login(self, cookie):
        message = '登录获取：'
        response = requests.get(
            'https://labs.zetachain.com/api/auth/session', headers=self.headers_cookie)
        # print(response.json())
        zeta_set_cookies = response.headers.get('set-cookie')
        zeta_hasuraJwt = response.json()['lambdaJwt']
        userId = response.json()['userId']
        # 将新的 Set-Cookie 的__Secure-next-auth.session-token值替换掉当前 cookie
        matches = re.findall('__Secure-next-auth\.(csrf-token|callback-url|session-token)=([^;]+)', zeta_set_cookies)
        cookies = {}
        for match in matches:
            cookies[match[0]] = match[1]
        self.cookie_list[self.index] = '__Secure-next-auth.session-token='+cookies['session-token']
        new_cookie_str = '@'.join(self.cookie_list)
        # 更新 .env 文件中的变量
        env_vars = dotenv_values('.env')
        env_vars[ckos] = new_cookie_str
        set_key('.env', ckos, new_cookie_str)

        return zeta_set_cookies, zeta_hasuraJwt, userId


    # 获取水：
    def get_zeta(self):
        message = '获取水：'
        data = {"address": self.account.address, "coins": [
            {"chain": "goerli", "symbol": "ZETA"}]}
        # print(self.headers_auth)
        response = requests.post(
            'https://zg8bghogy3.execute-api.us-east-1.amazonaws.com/faucet/validator', json=data, headers=self.headers_auth)
        userRank = response.json()
        return userRank


ckos = 'ZETA_COOKIES0'
pkos = 'key0'

if __name__ == '__main__':
    # 读取evn文件中的账号cookie列表
    zeta_cookie = os.getenv(ckos)
    zeta_cookies = zeta_cookie.split('@')

    # 读取evn文件中的账号privkey列表
    zeta_privkey = os.getenv(pkos)
    zeta_privkeys = zeta_privkey.split('@')

    for i, cookie in enumerate(zeta_cookies):
        privkey = zeta_privkeys[i]
        # print(i)
        # print(privkey)
        # print(cookie)
        account = web3.Account.from_key(privkey)
        zeta = Dapp(account, zeta_cookies, cookie, i)  # 实例化 Dapp 类
        result = zeta.run()  # 调用 run() 方法

