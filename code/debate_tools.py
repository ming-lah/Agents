from langchain_core.tools import tool
from duckduckgo_search import DDGS  
import wikipedia    
from serpapi import GoogleSearch 
import os, textwrap


@tool
def search_web(query: str, max_chars: int = 400) -> str:
    """
    使用 SerpAPI 返回 Google 首条搜索结果的摘要
    """
    params = {
        "q": query,
        "api_key": os.getenv("SERP_API_KEY"),
        "hl": "zh-cn",  # 设置中文搜索
        "num": "1",     # 只取返回的第一条结果
    }
    try:
        search = GoogleSearch(params)
        data = search.get_dict()
        snippet = data.get("organic_results", [{}])[0].get("snippet", "")

        snippet = " ".join(snippet.split())
        return textwrap.shorten(snippet, max_chars, placeholder="…") or "无摘要"
    except Exception as e:
        return f"【Serp ERROR】{e}"


import pandas as pd
import os
import random
@tool
def analyze_data(item: str) -> str:
    """从本地 CSV 文件读取教学相关数据，并随机返回某项数据"""
    try:
        absolute_path = "D:\Desktop\Agents\data\statistics.csv"
        df = pd.read_csv(absolute_path)
        random_item = random.choice(df['item'].tolist())  # 从 'item' 列中随机选择一个项目   
        # 根据随机选择的项来返回数据
        if random_item == "standardized_test":
            performance = df.loc[df['item'] == 'standardized_test', 'performance'].values[0]
            creativity = df.loc[df['item'] == 'creativity_decline', 'performance'].values[0]
            return f"标准化测试平均提分 {performance}%，创造性思维得分下降 {creativity}%"
        elif random_item == "ai_cost":
            ai_project_cost = df.loc[df['item'] == 'ai_cost', 'cost'].values[0]
            return f"AI 项目初始投入 {ai_project_cost} 万"
        elif random_item == "creativity_decline":
            creativity_decline = df.loc[df['item'] == 'creativity_decline', 'performance'].values[0]
            return f"创造性思维得分下降 {creativity_decline}%"
        
        return "暂无该项统计数据"
    
    except Exception as e:
        return f"ERROR: {e}"


@tool
def query_knowledge_base(topic: str) -> str:
    """查询教育理论知识库（模拟数据）"""
    kb = {
        "multiple_intelligences": "霍华德·加德纳（Howard Gardner）于1983年提出的多元智能理论强调人类智力的多样性，并且认为不同个体在不同的智能领域有不同的天赋与潜能。加德纳将智能分为语言智能、逻辑数学智能、空间智能、身体运动智能、音乐智能、人际智能、内省智能和自然智能等八种类型。根据此理论，教育应注重因材施教，针对不同学生的强项提供不同的教育策略，以促进学生全面发展。AI在此理论下可通过智能评估工具、个性化学习路径设计等方式，识别学生的优势智能领域并提供量身定制的学习内容，帮助学生在其强项上深入发展，同时不忽视其他领域的均衡提升。",

        "situated_learning": "情境学习理论（由杰克·L·杜普兰特等学者发展）主张知识是社会化的、情境化的，并且应当在真实情境中进行学习。杜普兰特强调，学习不仅仅是抽象的概念掌握，而是在特定的社会文化环境中，通过实践和社会互动来完成的。情境学习注重学习者在实际任务中的参与与沉浸式学习，认为知识只有通过实际操作和情境化的活动才能得到内化。AI在这一框架中的作用是提供与实际情境相关的学习任务和模拟环境，帮助学生在虚拟现实、仿真环境或实际应用中进行实践操作，增强其问题解决能力和应用技能。",

        "adult_learning": "成人学习理论（由Malcolm Knowles等学者提出）专注于成人学习者的特点与需求。成人学习理论强调成人学习者有着与儿童不同的学习动机和学习方式，成人倾向于将学习与自己的生活经验、职业需求以及个人目标结合起来。Knowles提出了成人学习的六个原则，包括自我导向学习、经验的价值、学习目标的相关性以及社会性学习等。AI在成人教育中的应用可以通过提供灵活的学习方式、即时反馈和自主学习支持，帮助成人学习者在不受传统课堂约束的情况下，根据个人需求与节奏进行学习。AI能够设计个性化学习路径并根据成人学习者的反馈动态调整学习内容，从而增强学习的效果与动力。"
    }
    return kb.get(topic, "该主题暂无记录。")


from math import sqrt
from statistics import mean
import re

@tool
def calculator(expr: str) -> str:
    """
    功能：安全地计算一个简单算术表达式。
    """
    try:
        if not re.fullmatch(r"[0-9+\-*/(). ]+", expr):
            return "ERROR: 只支持加减乘除与括号"
        value = eval(expr, {"__builtins__": {}}, {})
        return f"结果: {value}"
    except Exception as e:
        return f"ERROR: {e}"

@tool
def quick_stats(numbers: list[float]) -> str:
    """
    功能：返回均值、方差平方根（标准差）、极值。
    """
    if not numbers:
        return "ERROR: 空列表"
    avg = mean(numbers)
    var = mean([(x - avg) ** 2 for x in numbers])
    return f"均值={avg:.3f}，Std={sqrt(var):.3f}，最小={min(numbers)}，最大={max(numbers)}"


@tool
def wiki_intro(keyword: str, sentences: int = 2) -> str:
    """
    返回维基百科词条前几句话（优先中文，退回英文）。网络异常时返回错误说明。
    """
    try:
        wikipedia.set_lang("zh")          # 先尝试中文
        summary = wikipedia.summary(keyword, sentences=sentences, auto_suggest=True)
        return " ".join(summary.split())
    except wikipedia.DisambiguationError as d:
        # 关键词太泛时给出可选项
        return f"【Wiki】关键词不明确，可选: {', '.join(d.options[:5])}"
    except Exception:
        try:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(keyword, sentences=sentences, auto_suggest=True)
            return " ".join(summary.split())
        except Exception as e2:
            return f"【Wiki ERROR】{e2}"

import re
from math import sqrt
from statistics import mean
from datetime import datetime
from langchain_core.tools import tool, Tool


@tool
def sentiment(text: str) -> str:
    """
    极简情感分类。
    """
    pos = ("好", "赞", "支持", "优秀", "正面")
    con = ("差", "风险", "担忧", "负面", "糟糕")
    score = sum(word in text for word in pos) - sum(word in text for word in con)
    if score > 0:
        return "情感: 正面"
    if score < 0:
        return "情感: 负面"
    return "情感: 中性"


@tool
def keyword_extract(sentence: str, top_k: int = 5) -> str:
    """
    使用词频 + 停用词过滤提取关键词
    """
    stop = {"的", "了", "和", "是", "在", "对", "与"}
    words = re.findall(r"[\u4e00-\u9fa5A-Za-z]+", sentence)
    freq  = {}
    for w in words:
        if w not in stop:
            freq[w] = freq.get(w, 0) + 1
    kw = sorted(freq, key=freq.get, reverse=True)[:top_k]
    return "关键词: " + ", ".join(kw)


@tool
def current_time(_: str = "") -> str:
    """
    返回当前系统时间
    """
    return datetime.now().isoformat(timespec="seconds")

