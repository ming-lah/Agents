"""
极简记忆系统：短期(5 条) + 长期(重要信息) + 结构化语义片段
"""
from typing import List, Dict

class MemorySystem:
    def __init__(self):
        self.short_term: List[Dict] = []
        self.long_term: List[Dict]  = []
        self.semantic              = {"arguments": [], "evidence": []}

    # -------- 写入 --------
    def add(self, msg: Dict):
        self.short_term.append(msg)
        if len(self.short_term) > 5:
            self.short_term.pop(0)

        if self._important(msg):
            self.long_term.append(msg)
        self._extract_semantic(msg)

    # -------- 读出 --------
    def context(self) -> str:
        short = "\n".join(f"{m['speaker']}: {m['content']}" for m in self.short_term)
        args  = "\n".join(f"- {a}" for a in self.semantic["arguments"][-3:])
        evid  = "\n".join(f"- {e}" for e in self.semantic["evidence"][-3:])
        return f"最近对话:\n{short or '（空）'}\n\n论据:\n{args or '无'}\n证据:\n{evid or '无'}"

    # ===== 私有 =====
    def _important(self, msg):
        return any(k in msg["content"] for k in ("数据", "核心", "本质", "%"))

    def _extract_semantic(self, msg):
        text = msg["content"]
        if "因为" in text or "研究表明" in text:
            self.semantic["arguments"].append(text[:100])
        if "%" in text or "数据" in text:
            self.semantic["evidence"].append(text[:100])
    
    # -------- 新增：自动摘要 --------
    def summarize(self, max_chars: int = 600) -> str:
        """
        将 long_term + short_term 提炼为 ≤max_chars 的摘要，
        供每轮 prompt 注入。
        简单做法：抓取最近 12 条重要片段并拼接；
        若想更智能，可调用 LLM 摘要，这里先 Rule-based。
        """
        # 1) 取重要 long_term（按 round 倒序）
        long_important = [
            f"{x['speaker']}: {x['content']}" 
            for x in reversed(self.long_term[-25:])
            if x.get("important")
        ]
        # 2) 加上短期记忆
        recent = [f"{x['speaker']}: {x['content']}" 
                  for x in self.short_term[-5:]]

        snippets = long_important + recent
        summary = ""
        for s in snippets:
            if len(summary) + len(s) + 1 > max_chars:
                break
            summary += s + "\n"
        return summary.strip() or "（无重要记忆）"