"""
cron: 0 0 * * 0/7    zeta5.py
new Env('zeta')
updatetime:2023/6/7
by @StarzL1kerain

持续迭代中
抓GET包，只要请求头cookie的值
和私钥

"""
# zeta.py
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
        zeta_set_cookies, zeta_hasuraJwt, userId = self.login(self.cookie)
        # 带authorization的请求头
        self.headers_auth = self.generate_user_agent(authorization=zeta_hasuraJwt)
        transactions_count, total_earned_points, userRank = self.get_user_info(userId)
        # print(f"账号 {userId} 的交易次数：{transactions_count}，积分：{total_earned_points}，排名：{userRank}")

        cross_chain_info=self.cross_chain_to_Matic()
        print(cross_chain_info)
        result=self.call_api(cross_chain_info=cross_chain_info)
        
        progress_str = f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}，当前第{0}个账号/总{self.total}个账号，进度{progress:.2f}%\n"
        
        print(f"账号 {userId} 的交易次数：{transactions_count}，积分：{total_earned_points}，排名：{userRank}，跨链信息：{cross_chain_info['result']}，\n跨链结果：{result}")
                    
        # 等待5分钟
        wait_time = random.randint(100, 300)
        print(f"等待{wait_time}秒钟")
        time.sleep(wait_time)


    # 登录获取
    def login(self, cookie):
        message = '登录获取：'
        response = requests.get(
            'https://labs.zetachain.com/api/auth/session', headers=self.headers_cookie)
        # print(response.json())
        zeta_set_cookies = response.headers.get('set-cookie')
        zeta_hasuraJwt = response.json()['hasuraJwt']
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
    
    # 查询交易次数、积分和排行
    def get_user_info(self, userId):
        message = '查询交易次数、积分：'
        data = {
            "query": "\n    query GetUserById($id: Int!) {\n  users_by_pk(id: $id) {\n    id\n    mainWalletId\n    lastZetaDrip\n    inviteCode\n    createdAt\n    main_wallet {\n      id\n      address\n    }\n    wallets {\n      id\n      address\n    }\n    transactions_aggregate {\n      aggregate {\n        count\n      }\n    }\n    invited_users_aggregate {\n      aggregate {\n        count\n      }\n    }\n    zeta_points_aggregate {\n      aggregate {\n        sum {\n          totalEarnedPoints\n        }\n      }\n    }\n  }\n}\n    ",
            "variables": {
                "id": userId
            },
            "operationName": "GetUserById"
        }

        response = requests.post(
            'https://zeta-labs-production.hasura.app/v1/graphql', json=data, headers=self.headers_auth)
        # print(message + str(response.status_code))
        # print(response.json())
        transactions_count = response.json(
        )["data"]["users_by_pk"]["transactions_aggregate"]["aggregate"]["count"]
        total_earned_points = response.json(
        )["data"]["users_by_pk"]["zeta_points_aggregate"]["aggregate"]["sum"]["totalEarnedPoints"]
        # 排行
        message = '排行：'
        response = requests.get(
            'https://labs.zetachain.com/api/get-rank', headers=self.headers_cookie)
        # print(message + str(response.status_code))
        # print(response.json())
        userRank = response.json()['userRank']
        return transactions_count, total_earned_points, userRank

    # 进行测试网跨链并返回信息  # Goerli to Matic 3->0.5
    def cross_chain_to_Matic(self):
        __contract_addr = '0x805fE47D1FE7d86496753bB4B36206953c1ae660'
        rpc = Rpc()
        value = 3
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        amount = int(value * BALANCE_PRECISION)
        method = '0x9848a6b3'
        uint_0="000000000000000000000000cc7bb2d219a0fc08033e130629c2b854b7ba9195"
        uint_1="00000000000000000000000000000000000000000000000029a2241af62c0000"
        uint_2="0000000000000000000000000000000000000000000000000000000000000100"
        uint_3="000000000000000000000000000080383847bd75f91c168269aa74004877592f"
        uint_4="0000000000000000000000000000000000000000000000000000000000000000"
        uint_5="0000000000000000000000000000000000000000000000000000000000000000"
        uint_6="0000000000000000000000000000000000000000000000000000000000013881"
        uint_7="0000000000000000000000000000000000000000000000000000000000055730"
        uint_8="0000000000000000000000000000000000000000000000000000000000000014"
        uint_9="15987e0d78fa6193909a86d22abfe62bd8988397000000000000000000000000"
        data = method + uint_0 + uint_1 + uint_2 + uint_3 + uint_4 + uint_5 + uint_6 + uint_7 + uint_8 + uint_9
        cross_chain_info = rpc.transfer(self.account, __contract_addr,
                                        0, self.gas_limit, data=data)
        # 等待10到30秒钟随机时间
        wait_time = random.randint(10, 30)
        print(f"等待{wait_time}秒钟")
        time.sleep(wait_time)
        return cross_chain_info

    # 通过zeta_set_cookies调用接口使用测试网跨链保存的值，并输出结果
    def call_api(self,  cross_chain_info):
        
        message = '保存：'
        url = 'https://labs.zetachain.com/api/save-transaction'
        data = {"sourceChainId": '5', "sourceChainTxHash":
                cross_chain_info['result'], "walletAddress": self.account.address}
        result = requests.post(url, json=data, headers=self.headers_cookie)
        # print(message + str(result.status_code))
        # print(result.json())
        # 等待10到30秒钟随机时间
        wait_time = random.randint(10, 30)
        # print(f"等待{wait_time}秒钟")
        time.sleep(wait_time)
        return result.json()
    
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

