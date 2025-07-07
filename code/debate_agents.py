"""
Agent定义+工厂函数
"""
from typing import List, Dict
from datetime import datetime
from langchain_core.messages import HumanMessage

from config import model, WINDOW_SIZE
from memory_system import MemorySystem


class EnhancedDebateAgent:
    def __init__(self, name: str, role: str, system_prompt: str, capabilities: List[str]):
        self.name, self.role = name, role
        self.system_prompt   = system_prompt
        self.capabilities    = capabilities
        self.strategy        = "balanced"
        self.memory          = MemorySystem()

    def _prompt(self, global_history: List[Dict]) -> str:
        recent = global_history[-WINDOW_SIZE:]
        recent_txt = "\n".join(f"{m['speaker']}: {m['content']}" for m in recent) or "（无）"
        return f"""
{self.system_prompt}

能力: {', '.join(self.capabilities)}
策略: {self.strategy}

【记忆摘要】
{self.memory.summarize()}

【最近对话】
{recent_txt}

请根据以上信息发言。
""".strip()

    def reply(self, global_history: List[Dict]) -> Dict:
        prompt = self._prompt(global_history)
        content = model.invoke([HumanMessage(content=prompt)]).content
        msg = {"speaker": self.name, "content": content,
               "timestamp": datetime.now().isoformat()}
        self.memory.add(msg)
        return msg


def create_agents():
    teacher = EnhancedDebateAgent(
        "Teacher", "moderator",
        "你是辩论主持人，保持中立，领导作用，同时需要总结成果。",
        ["主持", "总结", "提出问题"]
    )
    pro_args = dict(role="supporter", capabilities=["数据分析", "偏向理性", "严密推理"])
    con_args = dict(role="opponent",  capabilities=["信息搜索", "偏向感性", "人文关怀"])

    pro1 = EnhancedDebateAgent("Pro1", **pro_args, system_prompt="正方一辩，用ReAct检索信息。")
    pro2 = EnhancedDebateAgent("Pro2", **pro_args, system_prompt="正方二辩，理性分析成本以及可行性。")
    pro3 = EnhancedDebateAgent("Pro3", **pro_args, system_prompt="正方三辩，进行严密的推理，关注其的应用前景。")

    con1 = EnhancedDebateAgent("Con1", **con_args, system_prompt="反方一辩，用ReAct检索信息。")
    con2 = EnhancedDebateAgent("Con2", **con_args, system_prompt="反方二辩，感性理解AI应用对于师生的影响。")
    con3 = EnhancedDebateAgent("Con3", **con_args, system_prompt="反方三辩，进行人文关怀，关注AI对于教育公平和伦理问题。")

    return teacher, [pro1, pro2, pro3], [con1, con2, con3]
