"""
统一放置模型 & 通用配置
"""
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# ====== OpenAI / 通义千问 兼容模式 ======
model = ChatOpenAI(
    model="qwen-turbo",                           # 模型名称
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=YOUR_API_KEY,
    temperature=0.7
)


WINDOW_SIZE = 6
MAX_ROUNDS = 3

load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")
