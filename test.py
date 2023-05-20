import os
from dotenv import load_dotenv
load_dotenv()

# 获取.env中的abyssauths数据，并使用split函数进行分割，得到多个 authorization
abyssauths = os.getenv("abyssauths")
authorizations = abyssauths.split('@')
print(authorizations)
