"""
ReAct 推理流程
"""
from datetime import datetime
from typing import List, Dict
from langchain_core.messages import HumanMessage
from config import model
from debate_tools import (
    search_web, analyze_data, query_knowledge_base,
    calculator, quick_stats, sentiment,
    keyword_extract, current_time,
    wiki_intro, 
)



TOOLS = [
    search_web, analyze_data, query_knowledge_base,
    calculator, quick_stats, sentiment,
    keyword_extract, current_time,
    wiki_intro,
]

def react_reasoning(agent_name: str, context: str) -> str:
    """返回带有思考 / 工具调用 / 推理 / 回应的字符串"""
    think_prompt = f"""
你是 {agent_name}。下面是最新上下文，请思考需要什么信息支撑你的论述：
{context}

请用一句话说明你要找什么信息，（可以使用各种工具，但无需直接调用，需要数据则返回的那句话中含有数据，需要背景，则返回的那句话中含有百科）
"""
    thought = model.invoke([HumanMessage(content=think_prompt)]).content
    search_results: List[str] = []

    if any(k in thought for k in ("计算", "增幅", "%")):
        search_results.append(calculator("((120-80)/80)*100"))

    elif any(k in thought for k in ("均值", "平均", "标准差", "数据波动")):
        sample = [1.2, 3.4, 2.9, 4.1, 3.3]
        search_results.append(quick_stats(sample))

    elif any(k in thought for k in ("情感", "态度", "观点偏向")):
        search_results.append(sentiment(context))

    elif "关键词" in thought or "提取" in thought:
        search_results.append(keyword_extract(context))

    elif any(k in thought for k in ("时间", "现在", "目前")):
        search_results.append(current_time())

    elif "百科" in thought or "wiki" in thought.lower():
        import re
        cand = re.findall(r"[\u4e00-\u9fa5A-Za-z]{2,}", thought)
        keyword = cand[-1] if cand else "人工智能"
        search_results.append(wiki_intro(keyword))

    elif any(k in thought for k in ("数据", "统计")):
        search_results.append(search_web("ai concerns"))
        search_results.append(analyze_data("performance"))


    else:
        search_results.append(query_knowledge_base("situated_learning"))

    reason_prompt = f"""
【已检索信息】
{chr(10).join(search_results)}

请基于以上信息，对观点进行分析与阐述，根据你的角色(正方/反方)进行观点支撑或者反驳，写150-200字。
"""
    reply = model.invoke([HumanMessage(content=reason_prompt)]).content

    return f"""【思考】{thought}

【检索结果】
{chr(10).join(search_results)}

【回应】
{reply}"""
