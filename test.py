"""
cron: 0 0 0 0 0 0 2055  test.py
new Env('测试')
updatetime:2023/5/21
by @StarzL1kerain
"""
import os
from dotenv import load_dotenv
load_dotenv()

# 获取.env中的abyssauths数据，并使用split函数进行分割，得到多个 authorization
abyssauths = os.getenv("abyssauths")
authorizations = abyssauths.split('@')
print(authorizations)
